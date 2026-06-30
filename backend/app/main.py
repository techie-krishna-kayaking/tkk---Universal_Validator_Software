import uvicorn

from app.config.settings import get_settings
from app.core.application import create_app

app = create_app()


def run() -> None:
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "local",
        factory=False,
    )
