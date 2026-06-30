from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=2)
    slug: str = Field(min_length=2)
    settings: dict = Field(default_factory=dict)


class OrganizationUpdate(BaseModel):
    name: str | None = None
    settings: dict | None = None
    is_active: bool | None = None


class TeamCreate(BaseModel):
    organization_id: str
    name: str = Field(min_length=2)
    settings: dict = Field(default_factory=dict)


class TeamUpdate(BaseModel):
    name: str | None = None
    settings: dict | None = None
    is_active: bool | None = None


class ProjectCreate(BaseModel):
    organization_id: str
    team_id: str
    name: str = Field(min_length=2)
    settings: dict = Field(default_factory=dict)


class ProjectUpdate(BaseModel):
    name: str | None = None
    settings: dict | None = None
    is_active: bool | None = None


class RoleCreate(BaseModel):
    organization_id: str | None = None
    name: str = Field(min_length=2)
    permissions: list[str] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    permissions: list[str] = Field(default_factory=list)


class PermissionCreate(BaseModel):
    key: str
    description: str


class InviteUserRequest(BaseModel):
    email: EmailStr
    organization_id: str
    team_id: str | None = None
    project_id: str | None = None
    role_name: str


class AcceptInvitationRequest(BaseModel):
    token: str
    user_id: str


class MembershipResponse(BaseModel):
    id: str
    user_id: str
    email: str
    organization_id: str
    team_id: str | None
    project_id: str | None
    role_name: str
    custom_permissions: list[str]
    is_active: bool


class TransferOwnershipRequest(BaseModel):
    entity_type: str = Field(pattern="^(organization|team|project)$")
    entity_id: str
    to_user_id: str


class DeactivateUserRequest(BaseModel):
    membership_id: str


class DeleteUserRequest(BaseModel):
    membership_id: str


class SettingsUpdateRequest(BaseModel):
    settings: dict


class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: str
    owner_user_id: str
    is_active: bool
    settings: dict


class TeamResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    owner_user_id: str
    is_active: bool
    settings: dict


class ProjectResponse(BaseModel):
    id: str
    organization_id: str
    team_id: str
    name: str
    owner_user_id: str
    is_active: bool
    settings: dict


class InvitationResponse(BaseModel):
    id: str
    email: str
    organization_id: str
    team_id: str | None
    project_id: str | None
    role_name: str
    token: str
    is_accepted: bool
    expires_at: datetime


class AuditResponse(BaseModel):
    id: str
    actor_user_id: str
    action: str
    resource_type: str
    resource_id: str | None
    outcome: str
    details: dict
