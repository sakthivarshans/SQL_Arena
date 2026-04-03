"""
FastAPI application for SQLArenaEnv.

Exposes SQLArenaEnvironment over HTTP and WebSocket endpoints,
fully compatible with OpenEnv EnvClient.

Endpoints:
    POST /reset    — start new episode (accepts task_id or difficulty in body)
    POST /step     — submit SQL action
    GET  /state    — get episode state
    GET  /schema   — action/observation schema
    GET  /tasks    — list all available tasks
    GET  /health   — liveness check
    WS   /ws       — persistent WebSocket session (preferred for training)
"""

try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:
    raise ImportError(
        "openenv-core is required. Install with: pip install openenv-core"
    ) from e

try:
    from ..models import SQLArenaAction, SQLArenaObservation
    from .sql_arena_environment import SQLArenaEnvironment
except ImportError:
    from models import SQLArenaAction, SQLArenaObservation
    from server.sql_arena_environment import SQLArenaEnvironment


app = create_app(
    SQLArenaEnvironment,
    SQLArenaAction,
    SQLArenaObservation,
    env_name="sql_arena_env",
    max_concurrent_envs=4,  # support parallel grader runs
)


def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    main(port=args.port)