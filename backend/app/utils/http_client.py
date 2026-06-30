from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

import httpx


@asynccontextmanager
async def http_client(timeout_seconds: float = 10.0) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        yield client
