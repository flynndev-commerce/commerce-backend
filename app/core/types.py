from fastapi import FastAPI

from app.containers import Container


class AppWithContainer(FastAPI):
    container: Container
