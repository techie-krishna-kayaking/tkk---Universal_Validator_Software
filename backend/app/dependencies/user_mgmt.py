from fastapi import Depends

from app.dependencies.auth import AuthenticatedPrincipal, require_permission
from app.dependencies.common import get_container
from app.dependencies.container import AppContainer
from app.services.user_mgmt_service import UserManagementService


def get_user_mgmt_service(container: AppContainer = Depends(get_container)) -> UserManagementService:
    return UserManagementService(repository=container.user_mgmt_repository)


def require_admin_scope(principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets"))):
    return principal
