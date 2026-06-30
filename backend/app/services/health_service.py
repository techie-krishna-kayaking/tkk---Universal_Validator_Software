from app.config.settings import Settings
from app.dependencies.container import AppContainer
from app.repositories.health_repository import HealthRepository
from app.schemas.health import ComponentStatus, HealthPayload, ReadinessPayload


class HealthService:
    def __init__(self, settings: Settings, repository: HealthRepository) -> None:
        self.settings = settings
        self.repository = repository

    async def liveness(self) -> HealthPayload:
        return HealthPayload(
            status="alive",
            service=self.settings.app_name,
            version=self.settings.app_version,
        )

    async def health(self) -> HealthPayload:
        return HealthPayload(
            status="healthy",
            service=self.settings.app_name,
            version=self.settings.app_version,
        )

    async def readiness(self, container: AppContainer) -> ReadinessPayload:
        database_status = await self._component_status(
            initialized=container.db_state.initialized,
            required=self.settings.database_required,
            check_func=lambda: self.repository.check_database(container.db_state),
            unavailable_detail="Database disabled or not initialized",
        )

        redis_status = await self._component_status(
            initialized=container.redis_state.initialized,
            required=self.settings.redis_required,
            check_func=lambda: self.repository.check_redis(container.redis_state),
            unavailable_detail="Redis disabled or not initialized",
        )

        celery_status = await self._component_status(
            initialized=container.celery_state.initialized,
            required=self.settings.celery_required,
            check_func=lambda: self._sync_wrapper(self.repository.check_celery(container.celery_state)),
            unavailable_detail="Celery disabled or not initialized",
        )

        required_ok = all(
            status.healthy or not status.required
            for status in (database_status, redis_status, celery_status)
        )

        return ReadinessPayload(
            status="ready" if required_ok else "not_ready",
            database=database_status,
            redis=redis_status,
            celery=celery_status,
        )

    async def _component_status(
        self,
        *,
        initialized: bool,
        required: bool,
        check_func,
        unavailable_detail: str,
    ) -> ComponentStatus:
        if not initialized:
            return ComponentStatus(
                initialized=False,
                healthy=not required,
                required=required,
                detail=unavailable_detail,
            )

        try:
            healthy = bool(await check_func())
            detail = None if healthy else "Health probe failed"
            return ComponentStatus(initialized=True, healthy=healthy, required=required, detail=detail)
        except Exception as exc:  # pragma: no cover
            return ComponentStatus(
                initialized=True,
                healthy=False,
                required=required,
                detail=str(exc),
            )

    async def _sync_wrapper(self, value: bool) -> bool:
        return value
