from fastapi import Depends

from app.dependencies.auth import AuthenticatedPrincipal, require_permission
from app.dependencies.common import get_container
from app.dependencies.container import AppContainer
from app.services.config_service import ConfigurationManagementService


def get_config_service(container: AppContainer = Depends(get_container)) -> ConfigurationManagementService:
    return ConfigurationManagementService(settings=container.settings, repository=container.config_repository)


def require_config_admin(principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets"))):
    return principal
