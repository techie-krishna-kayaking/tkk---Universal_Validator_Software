from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.exceptions.custom import ApiError


class RateLimiterHook:
    async def check(self, request: Request) -> None:
        return None


@dataclass
class InMemoryRateLimiter(RateLimiterHook):
    attempts: int
    window_seconds: int
    protected_paths: tuple[str, ...] = ("/api/v1/auth/login", "/api/v1/auth/refresh")

    def __post_init__(self) -> None:
        self._hits: dict[str, deque[datetime]] = defaultdict(deque)

    async def check(self, request: Request) -> None:
        if request.url.path not in self.protected_paths:
            return

        ip = request.client.host if request.client else "unknown"
        key = f"{ip}:{request.url.path}"
        now = datetime.now(UTC)
        window_start = now - timedelta(seconds=self.window_seconds)
        hits = self._hits[key]

        while hits and hits[0] < window_start:
            hits.popleft()

        if len(hits) >= self.attempts:
            raise ApiError(code="rate_limited", message="Too many requests", status_code=429)

        hits.append(now)


class RateLimitingHookMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, hook_factory: Callable[[], RateLimiterHook] | None = None) -> None:
        super().__init__(app)
        self.hook = hook_factory() if hook_factory else RateLimiterHook()

    async def dispatch(self, request: Request, call_next):
        await self.hook.check(request)
        return await call_next(request)
