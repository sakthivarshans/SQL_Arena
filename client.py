
from typing import Dict, Optional
from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

try:
    from .models import SQLArenaAction, SQLArenaObservation
except ImportError:
    from models import SQLArenaAction, SQLArenaObservation


class SQLArenaEnv(EnvClient[SQLArenaAction, SQLArenaObservation, State]):

    def _step_payload(self, action: SQLArenaAction) -> Dict:
        return {
            "sql": action.sql,
            "query_type": action.query_type,
        }

    def _parse_result(self, payload: Dict) -> StepResult[SQLArenaObservation]:
        obs_data = payload.get("observation", {})
        observation = SQLArenaObservation(
            # task info
            task_id=obs_data.get("task_id", ""),
            difficulty=obs_data.get("difficulty", "easy"),
            question=obs_data.get("question", ""),
            schema_info=obs_data.get("schema_info", ""),

            # query result
            query_result=obs_data.get("query_result", []),
            query_error=obs_data.get("query_error"),
            query_type=obs_data.get("query_type", "explore"),
            rows_returned=obs_data.get("rows_returned", 0),

            # episode progress
            explore_steps_used=obs_data.get("explore_steps_used", 0),
            explore_steps_remaining=obs_data.get("explore_steps_remaining", 5),
            submitted=obs_data.get("submitted", False),

            # feedback after submit
            is_correct=obs_data.get("is_correct"),
            feedback=obs_data.get("feedback"),
            expected_row_count=obs_data.get("expected_row_count"),

            # base fields
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
        