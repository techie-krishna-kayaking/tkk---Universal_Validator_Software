from uuid import uuid4

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.constants import DEFAULT_REQUEST_ID_HEADER


class RequestContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, request_id_header: str = DEFAULT_REQUEST_ID_HEADER) -> None:
        super().__init__(app)
        self.request_id_header = request_id_header

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get(self.request_id_header) or str(uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id, path=request.url.path)
        request.state.request_id = request_id

        response: Response = await call_next(request)
        response.headers[self.request_id_header] = request_id
        return response
