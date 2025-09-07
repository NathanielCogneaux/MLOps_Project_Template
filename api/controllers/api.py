from fastapi import APIRouter
from .endpoints import data, health, updates

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(updates.router, prefix="/updates", tags=["updates"])
