from dataclasses import dataclass

from app.config.settings import Settings, get_settings
from app.core.celery_app import CeleryState, init_celery
from app.core.db import DatabaseState, init_database
from app.core.redis import RedisState, init_redis
from app.repositories.auth_repository import InMemoryAuthRepository
from app.repositories.config_repository import InMemoryConfigRepository
from app.repositories.user_mgmt_repository import InMemoryUserManagementRepository


@dataclass
class AppContainer:
    settings: Settings
    db_state: DatabaseState
    redis_state: RedisState
    celery_state: CeleryState
    auth_repository: InMemoryAuthRepository
    user_mgmt_repository: InMemoryUserManagementRepository
    config_repository: InMemoryConfigRepository


async def create_container() -> AppContainer:
    settings = get_settings()
    db_state = init_database(settings)
    redis_state = await init_redis(settings)
    celery_state = init_celery(settings)
    auth_repository = InMemoryAuthRepository()
    user_mgmt_repository = InMemoryUserManagementRepository()
    config_repository = InMemoryConfigRepository()
    return AppContainer(
        settings=settings,
        db_state=db_state,
        redis_state=redis_state,
        celery_state=celery_state,
        auth_repository=auth_repository,
        user_mgmt_repository=user_mgmt_repository,
        config_repository=config_repository,
    )
