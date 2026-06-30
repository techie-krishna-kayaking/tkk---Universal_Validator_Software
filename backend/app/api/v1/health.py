from fastapi import APIRouter, Depends, Request, status

from app.dependencies.auth import require_tenant_access
from app.dependencies.common import get_container
from app.dependencies.container import AppContainer
from app.repositories.health_repository import HealthRepository
from app.schemas.health import HealthPayload, ReadinessPayload
from app.services.health_service import HealthService

router = APIRouter(
    prefix="/health",
    tags=["health"],
    dependencies=[Depends(require_tenant_access)],
)


def get_health_service(
    container: AppContainer = Depends(get_container),
) -> HealthService:
    return HealthService(settings=container.settings, repository=HealthRepository())


@router.get("", response_model=HealthPayload, status_code=status.HTTP_200_OK)
async def health_endpoint(service: HealthService = Depends(get_health_service)) -> HealthPayload:
    return await service.health()


@router.get("/liveness", response_model=HealthPayload, status_code=status.HTTP_200_OK)
async def liveness_endpoint(service: HealthService = Depends(get_health_service)) -> HealthPayload:
    return await service.liveness()


@router.get("/readiness", response_model=ReadinessPayload, status_code=status.HTTP_200_OK)
async def readiness_endpoint(
    request: Request,
    service: HealthService = Depends(get_health_service),
    container: AppContainer = Depends(get_container),
) -> ReadinessPayload:
    readiness = await service.readiness(container)
    if readiness.status != "ready":
        request.state.readiness_failed = True
    return readiness
