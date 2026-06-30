from dataclasses import dataclass

from celery import Celery

from app.config.settings import Settings


@dataclass
class CeleryState:
    app: Celery | None = None
    initialized: bool = False
    last_error: str | None = None


def init_celery(settings: Settings) -> CeleryState:
    state = CeleryState()
    if not settings.celery_enabled:
        return state

    app = Celery(
        "tkk_universal_validator",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
    )
    app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
    )
    state.app = app
    state.initialized = True
    return state


def ping_celery(state: CeleryState) -> bool:
    if not state.initialized or state.app is None:
        return False
    return True
