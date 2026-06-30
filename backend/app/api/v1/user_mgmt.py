from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import AuthenticatedPrincipal, require_permission
from app.dependencies.user_mgmt import get_user_mgmt_service
from app.schemas.user_mgmt import (
    AcceptInvitationRequest,
    AuditResponse,
    DeactivateUserRequest,
    DeleteUserRequest,
    InvitationResponse,
    InviteUserRequest,
    MembershipResponse,
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
    PermissionCreate,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    RoleCreate,
    RoleUpdate,
    SettingsUpdateRequest,
    TeamCreate,
    TeamResponse,
    TeamUpdate,
    TransferOwnershipRequest,
)
from app.services.user_mgmt_service import UserManagementService

router = APIRouter(prefix="/admin", tags=["admin-user-management"])


def _to_org_response(org) -> OrganizationResponse:
    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        owner_user_id=org.owner_user_id,
        is_active=org.is_active,
        settings=org.settings,
    )


def _to_team_response(team) -> TeamResponse:
    return TeamResponse(
        id=team.id,
        organization_id=team.organization_id,
        name=team.name,
        owner_user_id=team.owner_user_id,
        is_active=team.is_active,
        settings=team.settings,
    )


def _to_project_response(project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        organization_id=project.organization_id,
        team_id=project.team_id,
        name=project.name,
        owner_user_id=project.owner_user_id,
        is_active=project.is_active,
        settings=project.settings,
    )


def _to_membership_response(membership) -> MembershipResponse:
    return MembershipResponse(
        id=membership.id,
        user_id=membership.user_id,
        email=membership.email,
        organization_id=membership.organization_id,
        team_id=membership.team_id,
        project_id=membership.project_id,
        role_name=membership.role_name,
        custom_permissions=membership.custom_permissions,
        is_active=membership.is_active,
    )


def _to_invitation_response(invitation) -> InvitationResponse:
    return InvitationResponse(
        id=invitation.id,
        email=invitation.email,
        organization_id=invitation.organization_id,
        team_id=invitation.team_id,
        project_id=invitation.project_id,
        role_name=invitation.role_name,
        token=invitation.token,
        is_accepted=invitation.is_accepted,
        expires_at=invitation.expires_at,
    )


@router.post(
    "/organizations",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def create_organization(
    payload: OrganizationCreate,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets")),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> OrganizationResponse:
    org = service.create_organization(payload, actor_user_id=principal.user_id)
    return _to_org_response(org)


@router.get(
    "/organizations",
    response_model=list[OrganizationResponse],
    dependencies=[Depends(require_permission("can_view_reports"))],
)
async def list_organizations(
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> list[OrganizationResponse]:
    return [_to_org_response(org) for org in service.list_organizations()]


@router.put(
    "/organizations/{organization_id}",
    response_model=OrganizationResponse,
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def update_organization(
    organization_id: str,
    payload: OrganizationUpdate,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets")),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> OrganizationResponse:
    org = service.update_organization(organization_id, payload, actor_user_id=principal.user_id)
    return _to_org_response(org)


@router.delete(
    "/organizations/{organization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def delete_organization(
    organization_id: str,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets")),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> None:
    service.delete_organization(organization_id, actor_user_id=principal.user_id)


@router.post(
    "/teams",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("can_configure_schedulers"))],
)
async def create_team(
    payload: TeamCreate,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_configure_schedulers")),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> TeamResponse:
    team = service.create_team(payload, actor_user_id=principal.user_id)
    return _to_team_response(team)


@router.get(
    "/teams",
    response_model=list[TeamResponse],
    dependencies=[Depends(require_permission("can_view_reports"))],
)
async def list_teams(
    organization_id: str | None = Query(default=None),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> list[TeamResponse]:
    return [_to_team_response(team) for team in service.list_teams(organization_id)]


@router.put(
    "/teams/{team_id}",
    response_model=TeamResponse,
    dependencies=[Depends(require_permission("can_configure_schedulers"))],
)
async def update_team(
    team_id: str,
    payload: TeamUpdate,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_configure_schedulers")),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> TeamResponse:
    return _to_team_response(service.update_team(team_id, payload, actor_user_id=principal.user_id))


@router.delete(
    "/teams/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("can_configure_schedulers"))],
)
async def delete_team(
    team_id: str,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_configure_schedulers")),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> None:
    service.delete_team(team_id, actor_user_id=principal.user_id)


@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("can_run_validation"))],
)
async def create_project(
    payload: ProjectCreate,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_run_validation")),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> ProjectResponse:
    return _to_project_response(service.create_project(payload, actor_user_id=principal.user_id))


@router.get(
    "/projects",
    response_model=list[ProjectResponse],
    dependencies=[Depends(require_permission("can_view_reports"))],
)
async def list_projects(
    organization_id: str | None = Query(default=None),
    team_id: str | None = Query(default=None),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> list[ProjectResponse]:
    return [_to_project_response(project) for project in service.list_projects(organization_id, team_id)]


@router.put(
    "/projects/{project_id}",
    response_model=ProjectResponse,
    dependencies=[Depends(require_permission("can_run_validation"))],
)
async def update_project(
    project_id: str,
    payload: ProjectUpdate,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_run_validation")),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> ProjectResponse:
    return _to_project_response(service.update_project(project_id, payload, actor_user_id=principal.user_id))


@router.delete(
    "/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("can_run_validation"))],
)
async def delete_project(
    project_id: str,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_run_validation")),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> None:
    service.delete_project(project_id, actor_user_id=principal.user_id)


@router.post(
    "/roles",
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def create_custom_role(
    payload: RoleCreate,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets")),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> dict:
    role = service.create_custom_role(payload, actor_user_id=principal.user_id)
    return {"id": role.id, "name": role.name, "permissions": role.permissions}


@router.put(
    "/roles/{role_name}",
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def update_role(
    role_name: str,
    payload: RoleUpdate,
    organization_id: str | None = Query(default=None),
    principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets")),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> dict:
    role = service.update_role(organization_id=organization_id, role_name=role_name, payload=payload, actor_user_id=principal.user_id)
    return {"id": role.id, "name": role.name, "permissions": role.permissions}


@router.get(
    "/roles",
    dependencies=[Depends(require_permission("can_view_reports"))],
)
async def list_roles(
    organization_id: str | None = Query(default=None),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> list[dict]:
    return [
        {
            "id": role.id,
            "organization_id": role.organization_id,
            "name": role.name,
            "permissions": role.permissions,
            "is_system": role.is_system,
        }
        for role in service.list_roles(organization_id)
    ]


@router.post(
    "/permissions",
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def create_permission(
    payload: PermissionCreate,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets")),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> dict:
    permission = service.create_permission(payload, actor_user_id=principal.user_id)
    return {"id": permission.id, "key": permission.key, "description": permission.description}


@router.get(
    "/permissions",
    dependencies=[Depends(require_permission("can_view_reports"))],
)
async def list_permissions(service: UserManagementService = Depends(get_user_mgmt_service)) -> list[dict]:
    return [{"id": permission.id, "key": permission.key, "description": permission.description} for permission in service.list_permissions()]


@router.post(
    "/invitations",
    response_model=InvitationResponse,
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def invite_user(
    payload: InviteUserRequest,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets")),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> InvitationResponse:
    invitation = service.invite_user(payload, actor_user_id=principal.user_id)
    return _to_invitation_response(invitation)


@router.post(
    "/invitations/accept",
    response_model=MembershipResponse,
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def accept_invitation(
    payload: AcceptInvitationRequest,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets")),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> MembershipResponse:
    membership = service.accept_invitation(payload, actor_user_id=principal.user_id)
    return _to_membership_response(membership)


@router.post(
    "/memberships/deactivate",
    response_model=MembershipResponse,
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def deactivate_user(
    payload: DeactivateUserRequest,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets")),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> MembershipResponse:
    membership = service.deactivate_user(payload, actor_user_id=principal.user_id)
    return _to_membership_response(membership)


@router.delete(
    "/memberships",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def delete_user(
    payload: DeleteUserRequest,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets")),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> None:
    service.delete_user(payload, actor_user_id=principal.user_id)


@router.post(
    "/ownership/transfer",
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def transfer_ownership(
    payload: TransferOwnershipRequest,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets")),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> dict:
    service.transfer_ownership(payload, actor_user_id=principal.user_id)
    return {"message": "Ownership transferred"}


@router.put(
    "/organizations/{organization_id}/settings",
    response_model=OrganizationResponse,
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def update_organization_settings(
    organization_id: str,
    payload: SettingsUpdateRequest,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets")),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> OrganizationResponse:
    return _to_org_response(service.update_organization_settings(organization_id, payload, actor_user_id=principal.user_id))


@router.put(
    "/teams/{team_id}/settings",
    response_model=TeamResponse,
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def update_team_settings(
    team_id: str,
    payload: SettingsUpdateRequest,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets")),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> TeamResponse:
    return _to_team_response(service.update_team_settings(team_id, payload, actor_user_id=principal.user_id))


@router.put(
    "/projects/{project_id}/settings",
    response_model=ProjectResponse,
    dependencies=[Depends(require_permission("can_manage_secrets"))],
)
async def update_project_settings(
    project_id: str,
    payload: SettingsUpdateRequest,
    principal: AuthenticatedPrincipal = Depends(require_permission("can_manage_secrets")),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> ProjectResponse:
    return _to_project_response(service.update_project_settings(project_id, payload, actor_user_id=principal.user_id))


@router.get(
    "/audits",
    response_model=list[AuditResponse],
    dependencies=[Depends(require_permission("can_view_reports"))],
)
async def list_audits(
    organization_id: str | None = Query(default=None),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> list[AuditResponse]:
    return [
        AuditResponse(
            id=audit.id,
            actor_user_id=audit.actor_user_id,
            action=audit.action,
            resource_type=audit.resource_type,
            resource_id=audit.resource_id,
            outcome=audit.outcome,
            details=audit.details,
        )
        for audit in service.list_audit_events(organization_id=organization_id)
    ]
