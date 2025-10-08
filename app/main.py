from fastapi import FastAPI

from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.title,
        version=settings.version,
        debug=settings.debug,
    )

    @app.get("/")
    def read_root() -> dict[str, str]:
        return {"Hello": "World"}

    return app


app = create_app()
