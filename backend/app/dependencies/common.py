from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings
from app.core.db import get_db_session
from app.dependencies.container import AppContainer


def get_container(request: Request) -> AppContainer:
    return request.app.state.container


def get_settings_dependency(container: AppContainer = Depends(get_container)) -> Settings:
    return container.settings


async def get_db_session_dependency(
    container: AppContainer = Depends(get_container),
) -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session(container.db_state):
        yield session
