# Backend Foundation

This backend module provides enterprise bootstrap infrastructure for tkk-UniversalValidator.

## Scope
- Application factory and dependency wiring.
- Environment-aware configuration and profiles.
- Structured logging and request tracing.
- Middleware stack (CORS, compression, security headers, rate-limit hooks).
- Health, liveness, and readiness endpoints.
- API versioning and OpenAPI customization.
- SQLAlchemy session management, Redis init, Celery init.
- Startup and graceful shutdown lifecycle.
- Unit and integration test baseline.

## Quick Start
1. Install Poetry.
2. Run `poetry install`.
3. Copy `.env.example` to `.env`.
4. Run `poetry run backend-api`.

## Test
- `poetry run pytest`

## Documentation
- docs/DEVELOPER_GUIDE.md
- docs/ARCHITECTURE_BACKEND_FOUNDATION.md
- docs/API_BASELINE.md
