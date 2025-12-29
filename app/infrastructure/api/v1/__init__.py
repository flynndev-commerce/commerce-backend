from fastapi import APIRouter

from app.infrastructure.api.v1 import orders, products, users

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(users.router)
api_v1_router.include_router(products.router)
api_v1_router.include_router(orders.router)
