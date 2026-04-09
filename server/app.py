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
    max_concurrent_envs=4,  # allow parallel graders to run
)


def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()