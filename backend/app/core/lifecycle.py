from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from app.config.settings import Settings
from app.core.db import close_database
from app.core.dev_seed import seed_development_data
from app.core.redis import close_redis
from app.dependencies.container import AppContainer, create_container

logger = structlog.get_logger(__name__)


async def validate_required_dependencies(container: AppContainer, settings: Settings) -> None:
    if settings.database_required and not container.db_state.initialized:
        raise RuntimeError("Database is required but not initialized")
    if settings.redis_required and not container.redis_state.initialized:
        raise RuntimeError("Redis is required but not initialized")
    if settings.celery_required and not container.celery_state.initialized:
        raise RuntimeError("Celery is required but not initialized")


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("application_starting")
    container = await create_container()
    seed_development_data(
        app_env=container.settings.app_env,
        auth_repository=container.auth_repository,
        user_mgmt_repository=container.user_mgmt_repository,
    )
    await validate_required_dependencies(container, container.settings)
    app.state.container = container
    app.state.started = True
    logger.info("application_started", environment=container.settings.app_env)

    try:
        yield
    finally:
        logger.info("application_stopping")
        await close_redis(container.redis_state)
        await close_database(container.db_state)
        app.state.started = False
        logger.info("application_stopped")
