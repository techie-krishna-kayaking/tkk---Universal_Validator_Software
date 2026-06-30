from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.models.user_mgmt import (
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


@dataclass
class InMemoryUserManagementRepository:
    organizations: dict[str, Organization] = field(default_factory=dict)
    teams: dict[str, Team] = field(default_factory=dict)
    projects: dict[str, Project] = field(default_factory=dict)
    roles: dict[str, Role] = field(default_factory=dict)
    permissions: dict[str, Permission] = field(default_factory=dict)
    memberships: dict[str, UserMembership] = field(default_factory=dict)
    invitations: dict[str, Invitation] = field(default_factory=dict)
    audits: list[UserManagementAuditEvent] = field(default_factory=list)
    transfers: list[OwnershipTransferEvent] = field(default_factory=list)
    outbox: list[EmailOutboxEvent] = field(default_factory=list)

    def create_organization(self, org: Organization) -> Organization:
        org.id = org.id or str(uuid4())
        org.is_active = True if org.is_active is None else org.is_active
        org.settings = org.settings or {}
        org.created_at = org.created_at or datetime.now(UTC)
        org.updated_at = org.updated_at or datetime.now(UTC)
        self.organizations[org.id] = org
        return org

    def list_organizations(self) -> list[Organization]:
        return list(self.organizations.values())

    def get_organization(self, org_id: str) -> Organization | None:
        return self.organizations.get(org_id)

    def update_organization(self, org: Organization) -> Organization:
        org.updated_at = datetime.now(UTC)
        self.organizations[org.id] = org
        return org

    def delete_organization(self, org_id: str) -> bool:
        return self.organizations.pop(org_id, None) is not None

    def create_team(self, team: Team) -> Team:
        team.id = team.id or str(uuid4())
        team.is_active = True if team.is_active is None else team.is_active
        team.settings = team.settings or {}
        team.created_at = team.created_at or datetime.now(UTC)
        team.updated_at = team.updated_at or datetime.now(UTC)
        self.teams[team.id] = team
        return team

    def list_teams(self, organization_id: str | None = None) -> list[Team]:
        if not organization_id:
            return list(self.teams.values())
        return [team for team in self.teams.values() if team.organization_id == organization_id]

    def get_team(self, team_id: str) -> Team | None:
        return self.teams.get(team_id)

    def update_team(self, team: Team) -> Team:
        team.updated_at = datetime.now(UTC)
        self.teams[team.id] = team
        return team

    def delete_team(self, team_id: str) -> bool:
        return self.teams.pop(team_id, None) is not None

    def create_project(self, project: Project) -> Project:
        project.id = project.id or str(uuid4())
        project.is_active = True if project.is_active is None else project.is_active
        project.settings = project.settings or {}
        project.created_at = project.created_at or datetime.now(UTC)
        project.updated_at = project.updated_at or datetime.now(UTC)
        self.projects[project.id] = project
        return project

    def list_projects(self, organization_id: str | None = None, team_id: str | None = None) -> list[Project]:
        projects = list(self.projects.values())
        if organization_id:
            projects = [project for project in projects if project.organization_id == organization_id]
        if team_id:
            projects = [project for project in projects if project.team_id == team_id]
        return projects

    def get_project(self, project_id: str) -> Project | None:
        return self.projects.get(project_id)

    def update_project(self, project: Project) -> Project:
        project.updated_at = datetime.now(UTC)
        self.projects[project.id] = project
        return project

    def delete_project(self, project_id: str) -> bool:
        return self.projects.pop(project_id, None) is not None

    def create_permission(self, permission: Permission) -> Permission:
        permission.id = permission.id or str(uuid4())
        permission.is_system = False if permission.is_system is None else permission.is_system
        self.permissions[permission.key] = permission
        return permission

    def list_permissions(self) -> list[Permission]:
        return list(self.permissions.values())

    def create_role(self, role: Role) -> Role:
        role.id = role.id or str(uuid4())
        role.permissions = role.permissions or []
        role.is_system = False if role.is_system is None else role.is_system
        key = f"{role.organization_id or 'system'}:{role.name}"
        self.roles[key] = role
        return role

    def get_role(self, role_name: str, organization_id: str | None) -> Role | None:
        custom = self.roles.get(f"{organization_id}:{role_name}") if organization_id else None
        return custom or self.roles.get(f"system:{role_name}")

    def list_roles(self, organization_id: str | None) -> list[Role]:
        roles = [role for key, role in self.roles.items() if key.startswith("system:")]
        if organization_id:
            roles.extend(
                role for key, role in self.roles.items() if key.startswith(f"{organization_id}:")
            )
        return roles

    def create_membership(self, membership: UserMembership) -> UserMembership:
        membership.id = membership.id or str(uuid4())
        membership.custom_permissions = membership.custom_permissions or []
        membership.is_active = True if membership.is_active is None else membership.is_active
        self.memberships[membership.id] = membership
        return membership

    def get_membership(self, membership_id: str) -> UserMembership | None:
        return self.memberships.get(membership_id)

    def list_memberships(self, organization_id: str | None = None) -> list[UserMembership]:
        memberships = list(self.memberships.values())
        if organization_id:
            memberships = [membership for membership in memberships if membership.organization_id == organization_id]
        return memberships

    def update_membership(self, membership: UserMembership) -> UserMembership:
        self.memberships[membership.id] = membership
        return membership

    def delete_membership(self, membership_id: str) -> bool:
        return self.memberships.pop(membership_id, None) is not None

    def create_invitation(self, invitation: Invitation) -> Invitation:
        invitation.id = invitation.id or str(uuid4())
        invitation.token = invitation.token or uuid4().hex
        invitation.is_accepted = False if invitation.is_accepted is None else invitation.is_accepted
        invitation.expires_at = invitation.expires_at or (datetime.now(UTC) + timedelta(days=7))
        invitation.created_at = invitation.created_at or datetime.now(UTC)
        self.invitations[invitation.token] = invitation
        return invitation

    def get_invitation_by_token(self, token: str) -> Invitation | None:
        return self.invitations.get(token)

    def update_invitation(self, invitation: Invitation) -> Invitation:
        self.invitations[invitation.token] = invitation
        return invitation

    def add_audit(self, audit: UserManagementAuditEvent) -> None:
        audit.id = audit.id or str(uuid4())
        self.audits.append(audit)

    def list_audits(self, organization_id: str | None = None) -> list[UserManagementAuditEvent]:
        if not organization_id:
            return list(self.audits)
        return [event for event in self.audits if event.organization_id == organization_id]

    def add_transfer(self, transfer: OwnershipTransferEvent) -> None:
        transfer.id = transfer.id or str(uuid4())
        self.transfers.append(transfer)

    def queue_email(self, email_event: EmailOutboxEvent) -> None:
        email_event.id = email_event.id or str(uuid4())
        self.outbox.append(email_event)
