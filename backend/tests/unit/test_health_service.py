import pytest

from app.config.settings import Settings
from app.core.celery_app import CeleryState
from app.core.db import DatabaseState
from app.core.redis import RedisState
from app.dependencies.container import AppContainer
from app.repositories.auth_repository import InMemoryAuthRepository
from app.repositories.config_repository import InMemoryConfigRepository
from app.repositories.health_repository import HealthRepository
from app.repositories.user_mgmt_repository import InMemoryUserManagementRepository
from app.services.health_service import HealthService


@pytest.mark.asyncio
async def test_liveness_payload() -> None:
    settings = Settings(APP_NAME="svc", APP_VERSION="1.2.3")
    service = HealthService(settings=settings, repository=HealthRepository())

    payload = await service.liveness()

    assert payload.status == "alive"
    assert payload.service == "svc"


@pytest.mark.asyncio
async def test_readiness_not_ready_when_required_component_missing() -> None:
    settings = Settings(DATABASE_REQUIRED=True, DATABASE_ENABLED=False)
    service = HealthService(settings=settings, repository=HealthRepository())
    container = AppContainer(
        settings=settings,
        db_state=DatabaseState(initialized=False),
        redis_state=RedisState(initialized=False),
        celery_state=CeleryState(initialized=False),
        auth_repository=InMemoryAuthRepository(),
        user_mgmt_repository=InMemoryUserManagementRepository(),
        config_repository=InMemoryConfigRepository(),
    )

    payload = await service.readiness(container)

    assert payload.status == "not_ready"
    assert payload.database.required is True
    assert payload.database.healthy is False
