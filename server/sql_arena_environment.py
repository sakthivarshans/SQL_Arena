
import sqlite3
import json
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import SQLArenaAction, SQLArenaObservation
    from ..tasks import SQLTask, get_task, get_tasks_by_difficulty, ALL_TASKS
except ImportError:
    from models import SQLArenaAction, SQLArenaObservation
    from tasks import SQLTask, get_task, get_tasks_by_difficulty, ALL_TASKS


MAX_EXPLORE_STEPS = 5        # max explore queries allowed
MAX_RESULT_ROWS = 20         # max rows shown to agent
MAX_QUERY_TIMEOUT_MS = 5000  # query timeout in ms


class SQLArenaEnvironment(Environment):

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._conn: Optional[sqlite3.Connection] = None
        self._current_task: Optional[SQLTask] = None
        self._explore_steps_used: int = 0
        self._submitted: bool = False
        self._expected_result: Optional[List[Dict]] = None
        self._task_id_override: Optional[str] = None
        self._difficulty_override: Optional[str] = None

    # openenv required interface
    # ─────────────────────────────────────────

    def reset(self, task_id: Optional[str] = None, difficulty: Optional[str] = None) -> SQLArenaObservation:
        # close old db connection
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass

        # pick which task to run
        if task_id:
            task = get_task(task_id)
            if not task:
                task = list(ALL_TASKS.values())[0]
        elif difficulty:
            tasks = get_tasks_by_difficulty(difficulty)
            import random
            task = random.choice(tasks) if tasks else list(ALL_TASKS.values())[0]
        else:
            import random
            task = random.choice(list(ALL_TASKS.values()))

        self._current_task = task
        self._explore_steps_used = 0
        self._submitted = False
        self._state = State(episode_id=str(uuid4()), step_count=0)

        # fresh sqlite db in memory
        self._conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._conn.row_factory = sqlite3.Row

        # Load schema and seed data
        try:
            self._conn.executescript(task.schema_sql)
            self._conn.executescript(task.seed_sql)
            self._conn.commit()
        except Exception as e:
            return self._make_obs(
                query_error=f"Environment setup error: {e}",
                query_result=[],
                query_type="reset",
            )

        # run reference answer ahead of time
        self._expected_result = self._run_query_safe(task.solution_sql)

        return self._make_obs(
            query_result=[],
            query_type="reset",
            query_error=None,
        )

    def step(self, action: SQLArenaAction) -> SQLArenaObservation:
        if self._current_task is None:
            return self._make_obs(
                query_error="Environment not initialized. Call reset() first.",
                query_result=[],
                query_type=action.query_type,
                done=True,
                reward=-1.0,
            )

        if self._submitted:
            return self._make_obs(
                query_error="Episode already ended. Call reset() to start a new episode.",
                query_result=[],
                query_type=action.query_type,
                done=True,
                reward=0.0,
            )

        self._state.step_count += 1
        sql = action.sql.strip()
        query_type = action.query_type.lower()

        # explore step
        if query_type == "explore":
            # force submit if explore budget is done
            if self._explore_steps_used >= MAX_EXPLORE_STEPS:
                query_type = "submit"
            else:
                self._explore_steps_used += 1
                result, error = self._execute_safe(sql)
                # small cost per explore step
                reward = -0.02

                return self._make_obs(
                    query_result=result,
                    query_error=error,
                    query_type="explore",
                    done=False,
                    reward=reward,
                )

        # submit step
        self._submitted = True
        result, error = self._execute_safe(sql)

        if error:
            # syntax error penalty
            reward = -0.1
            feedback = f"SQL error on submission: {error}. Correct your query."
            return self._make_obs(
                query_result=[],
                query_error=error,
                query_type="submit",
                done=True,
                reward=reward,
                is_correct=False,
                feedback=feedback,
            )

        # grade the submitted query
        is_correct, partial, feedback = self._grade(result)
        if is_correct:
            reward = 1.0
        elif partial:
            reward = 0.4
        else:
            reward = 0.0

        return self._make_obs(
            query_result=result,
            query_error=None,
            query_type="submit",
            done=True,
            reward=reward,
            is_correct=is_correct,
            feedback=feedback,
        )

    @property
    def state(self) -> State:
        return self._state

    # internal helpers
    # ─────────────────────────────────────────

    def _execute_safe(self, sql: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        if not self._conn:
            return [], "Database not initialized"
        try:
            # block dangerous ops
            sql_upper = sql.upper().strip()
            dangerous = ["DROP ", "ALTER ", "TRUNCATE ", "PRAGMA ", "ATTACH ", "DETACH "]
            if any(sql_upper.startswith(d) for d in dangerous):
                return [], "Operation not permitted in this environment"

            cursor = self._conn.execute(sql)
            rows = cursor.fetchmany(MAX_RESULT_ROWS + 1)
            truncated = len(rows) > MAX_RESULT_ROWS
            rows = rows[:MAX_RESULT_ROWS]
            result = [dict(row) for row in rows]
            if truncated:
                result.append({"__info__": f"Results truncated to {MAX_RESULT_ROWS} rows"})
            return result, None
        except sqlite3.Error as e:
            return [], str(e)
        except Exception as e:
            return [], f"Unexpected error: {e}"

    def _run_query_safe(self, sql: str) -> Optional[List[Dict[str, Any]]]:
        if not self._conn:
            return None
        try:
            cursor = self._conn.execute(sql)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception:
            return None

    def _grade(self, agent_result: List[Dict]) -> Tuple[bool, bool, str]:
        expected = self._expected_result
        if expected is None:
            return False, False, "Could not compute expected result. Contact organizers."

        # compare both result sets
        def normalize(rows: List[Dict]) -> List[str]:
            normalized = []
            for row in rows:
                # skip internal marker rows
                clean = {k: v for k, v in row.items() if not k.startswith("__")}
                # round floats to avoid precision noise
                rounded = {}
                for k, v in clean.items():
                    if isinstance(v, float):
                        rounded[k] = round(v, 2)
                    else:
                        rounded[k] = v
                normalized.append(json.dumps(rounded, sort_keys=True))
            return sorted(normalized)

        # remove info markers from agent result
        agent_clean = [r for r in agent_result if not any(k.startswith("__") for k in r.keys())]

        expected_norm = normalize(expected)
        agent_norm = normalize(agent_clean)

        # exact match
        if expected_norm == agent_norm:
            return True, False, f"✓ Correct! Your query returned the exact expected result ({len(expected)} rows)."

        # check partial match conditions
        same_count = len(agent_clean) == len(expected)

        # same column names?
        exp_cols = set(expected[0].keys()) if expected else set()
        agent_cols = set(agent_clean[0].keys()) if agent_clean else set()
        same_cols = exp_cols == agent_cols

        # count matching rows
        matching_rows = len(set(expected_norm) & set(agent_norm))
        match_pct = matching_rows / max(len(expected_norm), 1) * 100

        if same_cols and same_count and match_pct >= 50:
            return False, True, (
                f"Partial credit. Correct columns, {same_count} rows, "
                f"but {matching_rows}/{len(expected)} rows match exactly. "
                f"Check your WHERE conditions or aggregation."
            )

        if same_cols and not same_count:
            return False, True, (
                f"Partial credit. Correct columns but wrong row count: "
                f"got {len(agent_clean)}, expected {len(expected)}. "
                f"Check your filters."
            ) if match_pct >= 30 else (False, False, (
                f"Wrong answer. Got {len(agent_clean)} rows, expected {len(expected)}. "
                f"Expected columns: {sorted(exp_cols)}."
            ))

        feedback = (
            f"Wrong answer. Expected {len(expected)} rows with columns {sorted(exp_cols)}. "
            f"You returned {len(agent_clean)} rows"
            + (f" with columns {sorted(agent_cols)}." if agent_clean else " (empty result).")
        )
        return False, False, feedback

    def _make_obs(
        self,
        query_result: List[Dict],
        query_type: str,
        query_error: Optional[str] = None,
        done: bool = False,
        reward: float = 0.0,
        is_correct: Optional[bool] = None,
        feedback: Optional[str] = None,
    ) -> SQLArenaObservation:
        task = self._current_task
        expected_count = len(self._expected_result) if self._expected_result else None

        return SQLArenaObservation(
            # task info
            task_id=task.task_id if task else "",
            difficulty=task.difficulty if task else "easy",
            question=task.question if task else "",
            schema_info=task.schema_description if task else "",

            # query result
            query_result=query_result,
            query_error=query_error,
            query_type=query_type,
            rows_returned=len([r for r in query_result if not any(k.startswith("__") for k in r.keys())]),

            # episode progress
            explore_steps_used=self._explore_steps_used,
            explore_steps_remaining=max(0, MAX_EXPLORE_STEPS - self._explore_steps_used),
            submitted=self._submitted,

            # feedback fields
            is_correct=is_correct,
            feedback=feedback,
            expected_row_count=expected_count,

            # base openenv fields
            done=done,
            reward=reward,
            metadata={
                "episode_id": self._state.episode_id,
                "step_count": self._state.step_count,
            },
        )