from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import AuthenticatedPrincipal, require_permission
from app.dependencies.config_mgmt import get_config_service
from app.models.config_mgmt import ConfigSource, ConnectionType
from app.schemas.config_mgmt import (
    ConfigAuditResponse,
    ConnectionConfigCreate,
    ConnectionConfigResponse,
    ConnectionConfigUpdate,
    ConnectionTestResult,
    CredentialValidationResult,
    SecretRotationRequest,
    SourceReloadRequest,
    SourceSnapshotResponse,
)
from app.services.config_service import ConfigurationManagementService

router = APIRouter(prefix="/admin/configs", tags=["admin-configuration-management"])


def _to_connection_response(
    service: ConfigurationManagementService,
    connection,
) -> ConnectionConfigResponse:
    return ConnectionConfigResponse(
        id=connection.id,
        tenant_id=connection.tenant_id,
        name=connection.name,
        connection_type=ConnectionType(connection.connection_type),
        source=ConfigSource(connection.source),
        masked_credentials=service.get_masked_credentials(connection),
        metadata=connection.config_metadata,
        is_active=connection.is_active,
        version=connection.version,
        rotate_after_days=connection.rotate_after_days,
        rotated_at=connection.rotated_at,
    )


@router.post(
    "/connections",
    response_model=ConnectionConfigResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def create_connection(
    payload: ConnectionConfigCreate,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets")),
    service: ConfigurationManagementService = Depends(get_config_service),
) -> ConnectionConfigResponse:
    connection = service.create_connection(payload, actor_user_id=principal.user_id)
    return _to_connection_response(service, connection)


@router.get(
    "/connections",
    response_model=list[ConnectionConfigResponse],
    dependencies=[Depends(require_permission("can_view_reports"))],
)
async def list_connections(
    tenant_id: str | None = Query(default=None),
    service: ConfigurationManagementService = Depends(get_config_service),
) -> list[ConnectionConfigResponse]:
    return [_to_connection_response(service, item) for item in service.list_connections(tenant_id=tenant_id)]


@router.get(
    "/connections/{connection_id}",
    response_model=ConnectionConfigResponse,
    dependencies=[Depends(require_permission("can_view_reports"))],
)
async def get_connection(
    connection_id: str,
    service: ConfigurationManagementService = Depends(get_config_service),
) -> ConnectionConfigResponse:
    return _to_connection_response(service, service.get_connection(connection_id))


@router.put(
    "/connections/{connection_id}",
    response_model=ConnectionConfigResponse,
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def update_connection(
    connection_id: str,
    payload: ConnectionConfigUpdate,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets")),
    service: ConfigurationManagementService = Depends(get_config_service),
) -> ConnectionConfigResponse:
    connection = service.update_connection(connection_id, payload, actor_user_id=principal.user_id)
    return _to_connection_response(service, connection)


@router.delete(
    "/connections/{connection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def delete_connection(
    connection_id: str,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets")),
    service: ConfigurationManagementService = Depends(get_config_service),
) -> None:
    service.delete_connection(connection_id, actor_user_id=principal.user_id)


@router.post(
    "/connections/{connection_id}/validate",
    response_model=CredentialValidationResult,
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def validate_credentials(
    connection_id: str,
    service: ConfigurationManagementService = Depends(get_config_service),
) -> CredentialValidationResult:
    return service.validate_credentials(connection_id)


@router.post(
    "/connections/{connection_id}/test",
    response_model=ConnectionTestResult,
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def test_connection(
    connection_id: str,
    service: ConfigurationManagementService = Depends(get_config_service),
) -> ConnectionTestResult:
    return service.test_connection(connection_id)


@router.post(
    "/connections/{connection_id}/rotate",
    response_model=ConnectionConfigResponse,
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def rotate_secret(
    connection_id: str,
    payload: SecretRotationRequest,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets")),
    service: ConfigurationManagementService = Depends(get_config_service),
) -> ConnectionConfigResponse:
    connection = service.rotate_secret(connection_id, payload, actor_user_id=principal.user_id)
    return _to_connection_response(service, connection)


@router.post(
    "/reload",
    response_model=dict[str, dict],
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def reload_sources(
    payload: SourceReloadRequest,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets")),
    service: ConfigurationManagementService = Depends(get_config_service),
) -> dict[str, dict]:
    return service.reload_sources(tenant_id=payload.tenant_id, actor_user_id=principal.user_id)


@router.get(
    "/snapshots",
    response_model=list[SourceSnapshotResponse],
    dependencies=[Depends(require_permission("can_view_reports"))],
)
async def list_snapshots(
    tenant_id: str = Query(),
    service: ConfigurationManagementService = Depends(get_config_service),
) -> list[SourceSnapshotResponse]:
    snapshots = service.list_source_snapshots(tenant_id)
    return [
        SourceSnapshotResponse(source=ConfigSource(item["source"]), revision=item["revision"], data=item["data"])
        for item in snapshots
    ]


@router.get(
    "/audits",
    response_model=list[ConfigAuditResponse],
    dependencies=[Depends(require_permission("can_view_reports"))],
)
async def list_audits(
    tenant_id: str | None = Query(default=None),
    service: ConfigurationManagementService = Depends(get_config_service),
) -> list[ConfigAuditResponse]:
    return [
        ConfigAuditResponse(
            id=item.id,
            tenant_id=item.tenant_id,
            actor_user_id=item.actor_user_id,
            action=item.action,
            connection_id=item.connection_id,
            outcome=item.outcome,
            details=item.details,
            created_at=item.created_at,
        )
        for item in service.list_audits(tenant_id)
    ]
