from fastapi import APIRouter

from app.api.v1.auth import protected_router as auth_protected_router
from app.api.v1.auth import public_router as auth_public_router
from app.api.v1.config_mgmt import router as config_mgmt_router
from app.api.v1.health import router as health_router
from app.api.v1.user_mgmt import router as user_mgmt_router

api_router_v1 = APIRouter()
api_router_v1.include_router(auth_public_router)
api_router_v1.include_router(auth_protected_router)
api_router_v1.include_router(health_router)
api_router_v1.include_router(user_mgmt_router)
api_router_v1.include_router(config_mgmt_router)
