"""
SQLArenaEnv Inference Script.

Runs an LLM agent against SQLArenaEnv, emitting the mandatory
[START] / [STEP] / [END] log format required by the hackathon evaluator.

The agent strategy:
  1. Read the question and schema from the reset observation
  2. Run 1-2 exploratory queries to understand the data
  3. Submit a final SQL query as the answer

Usage:
    API_BASE_URL=<url> MODEL_NAME=<model> HF_TOKEN=<token> python inference.py
"""

import asyncio
import os
import textwrap
from typing import List, Optional

from openai import OpenAI
from client import SQLArenaEnv, SQLArenaAction

IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME") or os.getenv("IMAGE_NAME")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
TASK_NAME = os.getenv("SQLARENA_TASK", "medium_001")
BENCHMARK = "sql_arena_env"
MAX_STEPS = 8
TEMPERATURE = 0.2
MAX_TOKENS = 512
SUCCESS_SCORE_THRESHOLD = 0.5

SYSTEM_PROMPT = textwrap.dedent("""
You are an expert SQL agent working with a SQLite database.
You will be given a natural language question and a schema description.
Your job is to write correct SQLite SQL to answer the question.

Rules:
- Use only standard SQLite syntax (no MySQL/PostgreSQL specific features)
- You can run EXPLORE queries first to understand the data structure
- When ready, submit your final answer with query_type="submit"
- SQLite date functions: SUBSTR(date,1,7) for YYYY-MM, julianday() for date math
- Window functions available: ROW_NUMBER(), RANK(), DENSE_RANK(), LAG(), LEAD(), SUM() OVER(), AVG() OVER(), PERCENT_RANK()

Response format — respond with ONLY a JSON object like this:
{"sql": "SELECT ...", "query_type": "explore"}
or
{"sql": "SELECT ...", "query_type": "submit"}

No explanation, no markdown, just the JSON.
""").strip()


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    action_safe = action.replace("\n", " ").replace("\r", "")[:200]
    print(
        f"[STEP] step={step} action={action_safe} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


def build_user_prompt(obs, step: int, history: List[str]) -> str:
    history_block = "\n".join(history[-3:]) if history else "None"
    result_str = str(obs.query_result[:5]) if obs.query_result else "No results yet"

    return textwrap.dedent(f"""
    QUESTION: {obs.question}
    SCHEMA: {obs.schema_info}

    Step: {step}
    Explore steps remaining: {obs.explore_steps_remaining}
    Last query result (first 5 rows): {result_str}
    Last error: {obs.query_error or 'None'}

    Previous actions:
    {history_block}

    {"⚠️ No more explore steps — you MUST submit now (query_type='submit')" if obs.explore_steps_remaining == 0 else "You can explore more or submit your final answer."}

    Respond with ONLY a JSON object: {{"sql": "...", "query_type": "explore" or "submit"}}
    """).strip()


def get_model_action(client: OpenAI, obs, step: int, history: List[str]):
    """Call the LLM and parse its response into a SQLArenaAction."""
    import json

    user_prompt = build_user_prompt(obs, step, history)
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        text = (completion.choices[0].message.content or "").strip()

        # Strip markdown if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        parsed = json.loads(text)
        sql = parsed.get("sql", "SELECT 1")
        query_type = parsed.get("query_type", "explore")

        # Force submit if no explore steps left
        if obs.explore_steps_remaining == 0:
            query_type = "submit"

        return SQLArenaAction(sql=sql, query_type=query_type)

    except Exception as exc:
        print(f"[DEBUG] Model parse error: {exc} | raw: {text[:200] if 'text' in dir() else 'N/A'}", flush=True)
        # Fallback: try a simple submit
        return SQLArenaAction(
            sql=f"SELECT * FROM sqlite_master WHERE type='table'",
            query_type="explore" if obs.explore_steps_remaining > 0 else "submit"
        )


async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    # Connect to environment
    if IMAGE_NAME:
        env = await SQLArenaEnv.from_docker_image(IMAGE_NAME)
    else:
        hf_space_url = os.getenv("HF_SPACE_URL", "http://localhost:8000")
        env = SQLArenaEnv(base_url=hf_space_url)

    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        result = await env.reset(task_id=TASK_NAME)
        obs = result.observation

        for step in range(1, MAX_STEPS + 1):
            if result.done:
                break

            action = get_model_action(client, obs, step, history)
            result = await env.step(action)
            obs = result.observation

            reward = result.reward or 0.0
            done = result.done
            error = obs.query_error

            rewards.append(reward)
            steps_taken = step

            log_step(
                step=step,
                action=f"{action.query_type}:{action.sql[:100]}",
                reward=reward,
                done=done,
                error=error,
            )

            history.append(
                f"Step {step} [{action.query_type}]: {action.sql[:80]} → "
                f"rows={obs.rows_returned} reward={reward:.2f}"
            )

            if done:
                break

        # Score: correctness of final submission (1.0 = correct, 0.4 = partial, 0.0 = wrong)
        final_reward = rewards[-1] if rewards else 0.0
        score = final_reward  # already normalized [0,1]
        success = score >= SUCCESS_SCORE_THRESHOLD

    except Exception as exc:
        print(f"[DEBUG] Episode error: {exc}", flush=True)

    finally:
        try:
            await env.close()
        except Exception as e:
            print(f"[DEBUG] env.close() error: {e}", flush=True)
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())