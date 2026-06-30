from datetime import UTC, datetime, timedelta

from app.exceptions.custom import ApiError
from app.models.user_mgmt import (
    DEFAULT_FEATURE_PERMISSIONS,
    DEFAULT_ROLES,
    EmailOutboxEvent,
    Invitation,
    Organization,
    OwnershipTransferEvent,
    Permission,
    Project,
    Role,
    Team,
    UserManagementAuditEvent,
    UserMembership,
)
from app.repositories.user_mgmt_repository import InMemoryUserManagementRepository
from app.schemas.user_mgmt import (
    AcceptInvitationRequest,
    DeactivateUserRequest,
    DeleteUserRequest,
    InviteUserRequest,
    OrganizationCreate,
    OrganizationUpdate,
    PermissionCreate,
    ProjectCreate,
    ProjectUpdate,
    RoleCreate,
    RoleUpdate,
    SettingsUpdateRequest,
    TeamCreate,
    TeamUpdate,
    TransferOwnershipRequest,
)


class UserManagementService:
    def __init__(self, repository: InMemoryUserManagementRepository) -> None:
        self.repository = repository
        self._bootstrap_defaults()

    def _bootstrap_defaults(self) -> None:
        if not self.repository.permissions:
            for key in DEFAULT_FEATURE_PERMISSIONS:
                self.repository.create_permission(Permission(key=key, description=key.replace("_", " ")))
        if not self.repository.roles:
            for role_name, perms in DEFAULT_ROLES.items():
                self.repository.create_role(Role(organization_id=None, name=role_name, is_system=True, permissions=perms))

    def create_organization(self, payload: OrganizationCreate, actor_user_id: str) -> Organization:
        org = Organization(name=payload.name, slug=payload.slug, owner_user_id=actor_user_id, settings=payload.settings)
        self.repository.create_organization(org)
        self.repository.add_audit(
            UserManagementAuditEvent(
                actor_user_id=actor_user_id,
                organization_id=org.id,
                action="organization.create",
                resource_type="organization",
                resource_id=org.id,
                outcome="success",
                details={"name": org.name, "slug": org.slug},
            )
        )
        return org

    def list_organizations(self) -> list[Organization]:
        return self.repository.list_organizations()

    def update_organization(self, org_id: str, payload: OrganizationUpdate, actor_user_id: str) -> Organization:
        org = self.repository.get_organization(org_id)
        if not org:
            raise ApiError(code="organization_not_found", message="Organization not found", status_code=404)

        if payload.name is not None:
            org.name = payload.name
        if payload.settings is not None:
            org.settings = payload.settings
        if payload.is_active is not None:
            org.is_active = payload.is_active

        self.repository.update_organization(org)
        self.repository.add_audit(
            UserManagementAuditEvent(
                actor_user_id=actor_user_id,
                organization_id=org.id,
                action="organization.update",
                resource_type="organization",
                resource_id=org.id,
                outcome="success",
                details={"settings_updated": payload.settings is not None},
            )
        )
        return org

    def delete_organization(self, org_id: str, actor_user_id: str) -> None:
        if not self.repository.delete_organization(org_id):
            raise ApiError(code="organization_not_found", message="Organization not found", status_code=404)
        self.repository.add_audit(
            UserManagementAuditEvent(
                actor_user_id=actor_user_id,
                organization_id=org_id,
                action="organization.delete",
                resource_type="organization",
                resource_id=org_id,
                outcome="success",
                details={},
            )
        )

    def create_team(self, payload: TeamCreate, actor_user_id: str) -> Team:
        if not self.repository.get_organization(payload.organization_id):
            raise ApiError(code="organization_not_found", message="Organization not found", status_code=404)

        team = Team(
            organization_id=payload.organization_id,
            name=payload.name,
            owner_user_id=actor_user_id,
            settings=payload.settings,
        )
        self.repository.create_team(team)
        self.repository.add_audit(
            UserManagementAuditEvent(
                actor_user_id=actor_user_id,
                organization_id=team.organization_id,
                action="team.create",
                resource_type="team",
                resource_id=team.id,
                outcome="success",
                details={"name": team.name},
            )
        )
        return team

    def list_teams(self, organization_id: str | None = None) -> list[Team]:
        return self.repository.list_teams(organization_id=organization_id)

    def update_team(self, team_id: str, payload: TeamUpdate, actor_user_id: str) -> Team:
        team = self.repository.get_team(team_id)
        if not team:
            raise ApiError(code="team_not_found", message="Team not found", status_code=404)
        if payload.name is not None:
            team.name = payload.name
        if payload.settings is not None:
            team.settings = payload.settings
        if payload.is_active is not None:
            team.is_active = payload.is_active
        self.repository.update_team(team)
        self.repository.add_audit(
            UserManagementAuditEvent(
                actor_user_id=actor_user_id,
                organization_id=team.organization_id,
                action="team.update",
                resource_type="team",
                resource_id=team.id,
                outcome="success",
                details={"settings_updated": payload.settings is not None},
            )
        )
        return team

    def delete_team(self, team_id: str, actor_user_id: str) -> None:
        team = self.repository.get_team(team_id)
        if not team:
            raise ApiError(code="team_not_found", message="Team not found", status_code=404)
        self.repository.delete_team(team_id)
        self.repository.add_audit(
            UserManagementAuditEvent(
                actor_user_id=actor_user_id,
                organization_id=team.organization_id,
                action="team.delete",
                resource_type="team",
                resource_id=team_id,
                outcome="success",
                details={},
            )
        )

    def create_project(self, payload: ProjectCreate, actor_user_id: str) -> Project:
        if not self.repository.get_organization(payload.organization_id):
            raise ApiError(code="organization_not_found", message="Organization not found", status_code=404)
        if not self.repository.get_team(payload.team_id):
            raise ApiError(code="team_not_found", message="Team not found", status_code=404)

        project = Project(
            organization_id=payload.organization_id,
            team_id=payload.team_id,
            name=payload.name,
            owner_user_id=actor_user_id,
            settings=payload.settings,
        )
        self.repository.create_project(project)
        self.repository.add_audit(
            UserManagementAuditEvent(
                actor_user_id=actor_user_id,
                organization_id=project.organization_id,
                action="project.create",
                resource_type="project",
                resource_id=project.id,
                outcome="success",
                details={"name": project.name},
            )
        )
        return project

    def list_projects(self, organization_id: str | None = None, team_id: str | None = None) -> list[Project]:
        return self.repository.list_projects(organization_id=organization_id, team_id=team_id)

    def update_project(self, project_id: str, payload: ProjectUpdate, actor_user_id: str) -> Project:
        project = self.repository.get_project(project_id)
        if not project:
            raise ApiError(code="project_not_found", message="Project not found", status_code=404)
        if payload.name is not None:
            project.name = payload.name
        if payload.settings is not None:
            project.settings = payload.settings
        if payload.is_active is not None:
            project.is_active = payload.is_active
        self.repository.update_project(project)
        self.repository.add_audit(
            UserManagementAuditEvent(
                actor_user_id=actor_user_id,
                organization_id=project.organization_id,
                action="project.update",
                resource_type="project",
                resource_id=project.id,
                outcome="success",
                details={"settings_updated": payload.settings is not None},
            )
        )
        return project

    def delete_project(self, project_id: str, actor_user_id: str) -> None:
        project = self.repository.get_project(project_id)
        if not project:
            raise ApiError(code="project_not_found", message="Project not found", status_code=404)
        self.repository.delete_project(project_id)
        self.repository.add_audit(
            UserManagementAuditEvent(
                actor_user_id=actor_user_id,
                organization_id=project.organization_id,
                action="project.delete",
                resource_type="project",
                resource_id=project_id,
                outcome="success",
                details={},
            )
        )

    def create_custom_role(self, payload: RoleCreate, actor_user_id: str) -> Role:
        role = Role(
            organization_id=payload.organization_id,
            name=payload.name,
            is_system=False,
            permissions=payload.permissions,
        )
        self.repository.create_role(role)
        self.repository.add_audit(
            UserManagementAuditEvent(
                actor_user_id=actor_user_id,
                organization_id=payload.organization_id,
                action="role.create",
                resource_type="role",
                resource_id=role.id,
                outcome="success",
                details={"role": role.name, "permissions": role.permissions},
            )
        )
        return role

    def update_role(self, organization_id: str | None, role_name: str, payload: RoleUpdate, actor_user_id: str) -> Role:
        role = self.repository.get_role(role_name=role_name, organization_id=organization_id)
        if not role:
            raise ApiError(code="role_not_found", message="Role not found", status_code=404)
        if role.is_system:
            raise ApiError(code="system_role_immutable", message="System roles are immutable", status_code=400)

        role.permissions = payload.permissions
        self.repository.create_role(role)
        self.repository.add_audit(
            UserManagementAuditEvent(
                actor_user_id=actor_user_id,
                organization_id=organization_id,
                action="role.update",
                resource_type="role",
                resource_id=role.id,
                outcome="success",
                details={"role": role.name, "permissions": role.permissions},
            )
        )
        return role

    def list_roles(self, organization_id: str | None) -> list[Role]:
        return self.repository.list_roles(organization_id=organization_id)

    def create_permission(self, payload: PermissionCreate, actor_user_id: str) -> Permission:
        permission = Permission(key=payload.key, description=payload.description, is_system=False)
        self.repository.create_permission(permission)
        self.repository.add_audit(
            UserManagementAuditEvent(
                actor_user_id=actor_user_id,
                organization_id=None,
                action="permission.create",
                resource_type="permission",
                resource_id=permission.id,
                outcome="success",
                details={"key": permission.key},
            )
        )
        return permission

    def list_permissions(self) -> list[Permission]:
        return self.repository.list_permissions()

    def invite_user(self, payload: InviteUserRequest, actor_user_id: str) -> Invitation:
        invitation = Invitation(
            email=payload.email,
            organization_id=payload.organization_id,
            team_id=payload.team_id,
            project_id=payload.project_id,
            role_name=payload.role_name,
            invited_by_user_id=actor_user_id,
            token=uuid_hex(),
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
        self.repository.create_invitation(invitation)
        self.repository.queue_email(
            EmailOutboxEvent(
                recipient_email=payload.email,
                subject="You are invited to tkk-UniversalValidator",
                template="invite_user",
                payload={
                    "token": invitation.token,
                    "organization_id": payload.organization_id,
                    "team_id": payload.team_id,
                    "project_id": payload.project_id,
                    "role_name": payload.role_name,
                },
            )
        )
        self.repository.add_audit(
            UserManagementAuditEvent(
                actor_user_id=actor_user_id,
                organization_id=payload.organization_id,
                action="invitation.create",
                resource_type="invitation",
                resource_id=invitation.id,
                outcome="success",
                details={"email": payload.email, "role_name": payload.role_name},
            )
        )
        return invitation

    def accept_invitation(self, payload: AcceptInvitationRequest, actor_user_id: str) -> UserMembership:
        invitation = self.repository.get_invitation_by_token(payload.token)
        if not invitation:
            raise ApiError(code="invitation_not_found", message="Invitation not found", status_code=404)
        if invitation.is_accepted:
            raise ApiError(code="invitation_already_used", message="Invitation already accepted", status_code=400)
        if invitation.expires_at < datetime.now(UTC):
            raise ApiError(code="invitation_expired", message="Invitation expired", status_code=400)

        membership = UserMembership(
            user_id=payload.user_id,
            email=invitation.email,
            organization_id=invitation.organization_id,
            team_id=invitation.team_id,
            project_id=invitation.project_id,
            role_name=invitation.role_name,
            custom_permissions=[],
            is_active=True,
        )
        self.repository.create_membership(membership)
        invitation.is_accepted = True
        self.repository.update_invitation(invitation)
        self.repository.add_audit(
            UserManagementAuditEvent(
                actor_user_id=actor_user_id,
                organization_id=invitation.organization_id,
                action="invitation.accept",
                resource_type="invitation",
                resource_id=invitation.id,
                outcome="success",
                details={"user_id": payload.user_id},
            )
        )
        return membership

    def deactivate_user(self, payload: DeactivateUserRequest, actor_user_id: str) -> UserMembership:
        membership = self.repository.get_membership(payload.membership_id)
        if not membership:
            raise ApiError(code="membership_not_found", message="Membership not found", status_code=404)
        membership.is_active = False
        self.repository.update_membership(membership)
        self.repository.add_audit(
            UserManagementAuditEvent(
                actor_user_id=actor_user_id,
                organization_id=membership.organization_id,
                action="membership.deactivate",
                resource_type="membership",
                resource_id=membership.id,
                outcome="success",
                details={"user_id": membership.user_id},
            )
        )
        return membership

    def delete_user(self, payload: DeleteUserRequest, actor_user_id: str) -> None:
        membership = self.repository.get_membership(payload.membership_id)
        if not membership:
            raise ApiError(code="membership_not_found", message="Membership not found", status_code=404)
        self.repository.delete_membership(payload.membership_id)
        self.repository.add_audit(
            UserManagementAuditEvent(
                actor_user_id=actor_user_id,
                organization_id=membership.organization_id,
                action="membership.delete",
                resource_type="membership",
                resource_id=payload.membership_id,
                outcome="success",
                details={"user_id": membership.user_id},
            )
        )

    def transfer_ownership(self, payload: TransferOwnershipRequest, actor_user_id: str) -> None:
        org_id = None
        team_id = None
        project_id = None

        if payload.entity_type == "organization":
            org = self.repository.get_organization(payload.entity_id)
            if not org:
                raise ApiError(code="organization_not_found", message="Organization not found", status_code=404)
            from_user = org.owner_user_id
            org.owner_user_id = payload.to_user_id
            org_id = org.id
            self.repository.update_organization(org)
        elif payload.entity_type == "team":
            team = self.repository.get_team(payload.entity_id)
            if not team:
                raise ApiError(code="team_not_found", message="Team not found", status_code=404)
            from_user = team.owner_user_id
            team.owner_user_id = payload.to_user_id
            team_id = team.id
            org_id = team.organization_id
            self.repository.update_team(team)
        else:
            project = self.repository.get_project(payload.entity_id)
            if not project:
                raise ApiError(code="project_not_found", message="Project not found", status_code=404)
            from_user = project.owner_user_id
            project.owner_user_id = payload.to_user_id
            project_id = project.id
            org_id = project.organization_id
            self.repository.update_project(project)

        self.repository.add_transfer(
            OwnershipTransferEvent(
                organization_id=org_id,
                team_id=team_id,
                project_id=project_id,
                from_user_id=from_user,
                to_user_id=payload.to_user_id,
                transferred_by_user_id=actor_user_id,
            )
        )
        self.repository.add_audit(
            UserManagementAuditEvent(
                actor_user_id=actor_user_id,
                organization_id=org_id,
                action="ownership.transfer",
                resource_type=payload.entity_type,
                resource_id=payload.entity_id,
                outcome="success",
                details={"from_user_id": from_user, "to_user_id": payload.to_user_id},
            )
        )

    def update_organization_settings(
        self, organization_id: str, payload: SettingsUpdateRequest, actor_user_id: str
    ) -> Organization:
        return self.update_organization(
            org_id=organization_id,
            payload=OrganizationUpdate(settings=payload.settings),
            actor_user_id=actor_user_id,
        )

    def update_team_settings(self, team_id: str, payload: SettingsUpdateRequest, actor_user_id: str) -> Team:
        return self.update_team(team_id=team_id, payload=TeamUpdate(settings=payload.settings), actor_user_id=actor_user_id)

    def update_project_settings(self, project_id: str, payload: SettingsUpdateRequest, actor_user_id: str) -> Project:
        return self.update_project(
            project_id=project_id,
            payload=ProjectUpdate(settings=payload.settings),
            actor_user_id=actor_user_id,
        )

    def list_audit_events(self, organization_id: str | None = None) -> list[UserManagementAuditEvent]:
        return self.repository.list_audits(organization_id=organization_id)


def uuid_hex() -> str:
    from uuid import uuid4

    return uuid4().hex
