from collections.abc import AsyncGenerator
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.config.settings import Settings


@dataclass
class DatabaseState:
    engine: AsyncEngine | None = None
    session_factory: async_sessionmaker[AsyncSession] | None = None
    initialized: bool = False
    last_error: str | None = None


def init_database(settings: Settings) -> DatabaseState:
    state = DatabaseState()
    if not settings.database_enabled or not settings.database_url:
        return state

    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    state.engine = engine
    state.session_factory = session_factory
    state.initialized = True
    return state


async def close_database(state: DatabaseState) -> None:
    if state.engine is not None:
        await state.engine.dispose()


async def ping_database(state: DatabaseState) -> bool:
    if not state.initialized or state.session_factory is None:
        return False

    async with state.session_factory() as session:
        await session.execute(text("SELECT 1"))
    return True


async def get_db_session(state: DatabaseState) -> AsyncGenerator[AsyncSession, None]:
    if state.session_factory is None:
        raise RuntimeError("Database session factory is not initialized")

    async with state.session_factory() as session:
        yield session
