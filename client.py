"""
SQLArenaEnv Client.

Typed async client for SQLArenaEnv. Maintains a persistent WebSocket
connection for efficient multi-step interactions during RL training.

Example (async):
    async with SQLArenaEnv(base_url="https://your-space.hf.space") as env:
        result = await env.reset(task_id="medium_001")
        print(result.observation.question)

        result = await env.step(SQLArenaAction(
            sql="SELECT * FROM customers LIMIT 5",
            query_type="explore"
        ))
        print(result.observation.query_result)

        result = await env.step(SQLArenaAction(
            sql="SELECT name, city FROM customers WHERE segment='Corporate'",
            query_type="submit"
        ))
        print(result.observation.feedback)

Example (sync):
    with SQLArenaEnv(base_url="http://localhost:8000").sync() as env:
        result = env.reset(difficulty="easy")
        result = env.step(SQLArenaAction(sql="SELECT 1", query_type="submit"))

Example (from Docker):
    env = await SQLArenaEnv.from_docker_image("sql-arena-env:latest")
    try:
        result = await env.reset()
    finally:
        await env.close()
"""

from typing import Dict, Optional
from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

from .models import SQLArenaAction, SQLArenaObservation


class SQLArenaEnv(EnvClient[SQLArenaAction, SQLArenaObservation, State]):
    """
    Async client for SQLArenaEnv.

    This client maintains a persistent WebSocket connection to the environment
    server, enabling efficient multi-step SQL interactions with low latency.
    """

    def _step_payload(self, action: SQLArenaAction) -> Dict:
        return {
            "sql": action.sql,
            "query_type": action.query_type,
        }

    def _parse_result(self, payload: Dict) -> StepResult[SQLArenaObservation]:
        obs_data = payload.get("observation", {})
        observation = SQLArenaObservation(
            # Task context
            task_id=obs_data.get("task_id", ""),
            difficulty=obs_data.get("difficulty", "easy"),
            question=obs_data.get("question", ""),
            schema_info=obs_data.get("schema_info", ""),

            # Query result
            query_result=obs_data.get("query_result", []),
            query_error=obs_data.get("query_error"),
            query_type=obs_data.get("query_type", "explore"),
            rows_returned=obs_data.get("rows_returned", 0),

            # Episode progress
            explore_steps_used=obs_data.get("explore_steps_used", 0),
            explore_steps_remaining=obs_data.get("explore_steps_remaining", 5),
            submitted=obs_data.get("submitted", False),

            # Feedback after submit
            is_correct=obs_data.get("is_correct"),
            feedback=obs_data.get("feedback"),
            expected_row_count=obs_data.get("expected_row_count"),

            # Base fields
            done=payload.get("done", False),
            reward=payload.get("reward", 0.0),
            metadata=obs_data.get("metadata", {}),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward", 0.0),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )
        