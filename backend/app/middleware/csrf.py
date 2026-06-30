from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.exceptions.custom import ApiError


class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, csrf_header_name: str, enabled: bool = True) -> None:
        super().__init__(app)
        self.csrf_header_name = csrf_header_name
        self.enabled = enabled

    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)

        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            has_cookie_session = bool(request.cookies.get("session_id"))
            if has_cookie_session:
                csrf_header = request.headers.get(self.csrf_header_name)
                csrf_cookie = request.cookies.get("csrf_token")
                if not csrf_header or not csrf_cookie or csrf_header != csrf_cookie:
                    raise ApiError(code="csrf_validation_failed", message="CSRF token validation failed", status_code=403)

        return await call_next(request)
