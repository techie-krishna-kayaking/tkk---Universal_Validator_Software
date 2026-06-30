from app.repositories.user_mgmt_repository import InMemoryUserManagementRepository
from app.schemas.user_mgmt import (
    AcceptInvitationRequest,
    InviteUserRequest,
    OrganizationCreate,
    ProjectCreate,
    TeamCreate,
    TransferOwnershipRequest,
)
from app.services.user_mgmt_service import UserManagementService


def test_user_mgmt_crud_invite_and_transfer() -> None:
    service = UserManagementService(repository=InMemoryUserManagementRepository())
    actor = "actor-1"

    org = service.create_organization(OrganizationCreate(name="Org A", slug="org-a"), actor_user_id=actor)
    team = service.create_team(TeamCreate(organization_id=org.id, name="Team A"), actor_user_id=actor)
    project = service.create_project(
        payload=ProjectCreate(
            organization_id=org.id,
            team_id=team.id,
            name="Project A",
            settings={},
        ),
        actor_user_id=actor,
    )

    invite = service.invite_user(
        InviteUserRequest(
            email="user@example.com",
            organization_id=org.id,
            team_id=team.id,
            project_id=project.id,
            role_name="viewer",
        ),
        actor_user_id=actor,
    )

    membership = service.accept_invitation(
        AcceptInvitationRequest(token=invite.token, user_id="user-123"),
        actor_user_id="user-123",
    )

    service.transfer_ownership(
        TransferOwnershipRequest(entity_type="project", entity_id=project.id, to_user_id="user-123"),
        actor_user_id=actor,
    )

    assert membership.user_id == "user-123"
    updated_project = service.repository.get_project(project.id)
    assert updated_project is not None
    assert updated_project.owner_user_id == "user-123"
