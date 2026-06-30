# API Baseline

## Versioning
- Base prefix: /api/v1

## Endpoints
- GET /api/v1/health
- GET /api/v1/health/liveness
- GET /api/v1/health/readiness

## OpenAPI
- Custom OpenAPI metadata is configured in app/core/openapi.py.

## Error Contract
All handled and unhandled errors return structured payloads with a stable error code and message.
