from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api.router import api_router_v1
from app.config.settings import get_settings
from app.core.constants import DEFAULT_API_PREFIX, DEFAULT_REQUEST_ID_HEADER
from app.core.lifecycle import app_lifespan
from app.core.logging import configure_logging
from app.core.openapi import install_custom_openapi
from app.exceptions.handlers import register_exception_handlers
from app.middleware.csrf import CSRFMiddleware
from app.middleware.rate_limit_hook import InMemoryRateLimiter, RateLimitingHookMiddleware
from app.middleware.request_context import RequestContextMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.app_debug,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        lifespan=app_lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.enable_gzip:
        app.add_middleware(GZipMiddleware, minimum_size=1024)

    app.add_middleware(
        RequestContextMiddleware,
        request_id_header=settings.request_id_header or DEFAULT_REQUEST_ID_HEADER,
    )

    if settings.enable_security_headers:
        app.add_middleware(SecurityHeadersMiddleware)

    if settings.enable_rate_limit_hooks:
        app.add_middleware(
            RateLimitingHookMiddleware,
            hook_factory=lambda: InMemoryRateLimiter(
                attempts=settings.auth_rate_limit_attempts,
                window_seconds=settings.auth_rate_limit_window_seconds,
            ),
        )

    app.add_middleware(
        CSRFMiddleware,
        csrf_header_name=settings.csrf_header_name,
        enabled=settings.csrf_enabled,
    )

    api_prefix = settings.api_v1_prefix or DEFAULT_API_PREFIX
    app.include_router(api_router_v1, prefix=api_prefix)

    register_exception_handlers(app)
    install_custom_openapi(app)

    return app
