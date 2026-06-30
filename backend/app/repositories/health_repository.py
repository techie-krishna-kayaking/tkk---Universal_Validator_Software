from app.core.celery_app import CeleryState, ping_celery
from app.core.db import DatabaseState, ping_database
from app.core.redis import RedisState, ping_redis


class HealthRepository:
    async def check_database(self, state: DatabaseState) -> bool:
        return await ping_database(state)

    async def check_redis(self, state: RedisState) -> bool:
        return await ping_redis(state)

    def check_celery(self, state: CeleryState) -> bool:
        return ping_celery(state)
