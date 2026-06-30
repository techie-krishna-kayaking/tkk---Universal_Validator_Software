from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def install_custom_openapi(app: FastAPI) -> None:
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        app.openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            summary="Enterprise backend foundation for tkk-UniversalValidator",
            description=(
                "Versioned control-plane API baseline with health probes, "
                "request tracing, and enterprise middleware stack."
            ),
            routes=app.routes,
        )
        app.openapi_schema["info"]["x-api-audience"] = "internal-platform"
        app.openapi_schema["info"]["contact"] = {
            "name": "Platform Engineering",
            "email": "platform@example.com",
        }
        return app.openapi_schema

    app.openapi = custom_openapi
