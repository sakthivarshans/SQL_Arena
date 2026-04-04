
from typing import Any, Dict, List, Optional
from openenv.core.env_server.types import Action, Observation
from pydantic import Field


class SQLArenaAction(Action):

    sql: str = Field(..., description="SQL query to execute against the database")
    query_type: str = Field(
        default="explore",
        description="'explore' for investigative queries, 'submit' for final answer"
    )


class SQLArenaObservation(Observation):

    # task context
    task_id: str = Field(default="", description="Current task identifier")
    difficulty: str = Field(default="easy", description="Task difficulty: easy/medium/hard/expert")
    question: str = Field(default="", description="Natural language question to answer via SQL")
    schema_info: str = Field(default="", description="Database schema description")

    # query result
    query_result: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Rows returned by the SQL query (up to 20 rows shown)"
    )
    query_error: Optional[str] = Field(
        default=None,
        description="SQL error message if query failed, null otherwise"
    )
    query_type: str = Field(default="explore", description="Type of query just executed")
    rows_returned: int = Field(default=0, description="Number of rows returned")

    # episode progress
    explore_steps_used: int = Field(default=0, description="Number of explore actions used so far")
    explore_steps_remaining: int = Field(default=5, description="Explore actions remaining before forced submit")
    submitted: bool = Field(default=False, description="Whether agent has submitted final answer")

    # feedback shown only after submit
    is_correct: Optional[bool] = Field(default=None, description="Whether submitted answer is correct (after submit only)")
    feedback: Optional[str] = Field(default=None, description="Feedback message after submission")
    expected_row_count: Optional[int] = Field(default=None, description="How many rows correct answer has")