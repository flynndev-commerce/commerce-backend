from fastapi import FastAPI

from app.api.root import router as root_router
from app.api.v1 import api_v1_router


def configure_routers(app: FastAPI) -> None:
    app.include_router(root_router)
    app.include_router(api_v1_router)
