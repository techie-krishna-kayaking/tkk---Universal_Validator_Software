from dataclasses import dataclass

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.dependencies.common import get_container
from app.dependencies.container import AppContainer
from app.exceptions.custom import ApiError
from app.models.auth import AuthUser
from app.repositories.auth_repository import InMemoryAuthRepository
from app.services.auth_service import AuthService

security_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthenticatedPrincipal:
    user_id: str
    tenant_id: str
    role: str
    permissions: list[str]


def get_auth_repository(container: AppContainer = Depends(get_container)) -> InMemoryAuthRepository:
    return container.auth_repository


def get_auth_service(
    container: AppContainer = Depends(get_container),
    repository: InMemoryAuthRepository = Depends(get_auth_repository),
) -> AuthService:
    return AuthService(settings=container.settings, repository=repository)


def get_current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthenticatedPrincipal:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise ApiError(code="auth_required", message="Authentication required", status_code=401)

    try:
        info = auth_service.get_session_info_from_access_token(credentials.credentials)
    except Exception as exc:  # pragma: no cover
        raise ApiError(code="invalid_token", message="Invalid bearer token", status_code=401) from exc

    return AuthenticatedPrincipal(
        user_id=info.user_id,
        tenant_id=info.tenant_id,
        role=info.role,
        permissions=info.permissions,
    )


def require_tenant_access(
    tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
) -> AuthenticatedPrincipal:
    if tenant_id and tenant_id != principal.tenant_id:
        raise ApiError(code="tenant_forbidden", message="Tenant authorization failed", status_code=403)
    return principal


def require_role(*allowed_roles: str):
    def checker(principal: AuthenticatedPrincipal = Depends(require_tenant_access)) -> AuthenticatedPrincipal:
        if principal.role not in allowed_roles:
            raise ApiError(code="role_forbidden", message="Role authorization failed", status_code=403)
        return principal

    return checker


def require_permission(permission: str):
    def checker(principal: AuthenticatedPrincipal = Depends(require_tenant_access)) -> AuthenticatedPrincipal:
        if permission not in principal.permissions and principal.role not in {
            "platform_admin",
            "organization_admin",
            "Platform Admin",
            "Organization Admin",
        }:
            raise ApiError(
                code="permission_forbidden",
                message="Permission authorization failed",
                status_code=403,
            )
        return principal

    return checker
