from dataclasses import dataclass

from redis.asyncio import Redis

from app.config.settings import Settings


@dataclass
class RedisState:
    client: Redis | None = None
    initialized: bool = False
    last_error: str | None = None


async def init_redis(settings: Settings) -> RedisState:
    state = RedisState()
    if not settings.redis_enabled or not settings.redis_url:
        return state

    client = Redis.from_url(settings.redis_url, decode_responses=True)
    state.client = client
    state.initialized = True
    return state


async def close_redis(state: RedisState) -> None:
    if state.client is not None:
        await state.client.aclose()


async def ping_redis(state: RedisState) -> bool:
    if not state.initialized or state.client is None:
        return False
    return bool(await state.client.ping())
