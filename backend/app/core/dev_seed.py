from dataclasses import dataclass

from app.config.profiles import EnvironmentProfile
from app.core.security import hash_password
from app.models.auth import AuthUser
from app.models.user_mgmt import DEFAULT_ROLES, Organization, Project, Team, UserMembership
from app.repositories.auth_repository import InMemoryAuthRepository
from app.repositories.user_mgmt_repository import InMemoryUserManagementRepository


ORG_ID = "TKK-ORG-001"
TEAM_ID = "TEAM-DE-001"
PROJECT_AMEX_ID = "AMEX-DM-001"
PROJECT_SNOWFLAKE_ID = "SNOW-VAL-001"


@dataclass(frozen=True)
class DevSeedUser:
    username: str
    email: str
    password: str
    role: str


DEV_SEED_USERS: tuple[DevSeedUser, ...] = (
    DevSeedUser(username="admin", email="admin@tkkvalidator.local", password="Admin@123", role="platform_admin"),
    DevSeedUser(
        username="orgadmin",
        email="orgadmin@tkkvalidator.local",
        password="Admin@123",
        role="organization_admin",
    ),
    DevSeedUser(username="architect", email="architect@tkkvalidator.local", password="Architect@123", role="architect"),
    DevSeedUser(username="qalead", email="qalead@tkkvalidator.local", password="QALead@123", role="qa_lead"),
    DevSeedUser(username="tester", email="tester@tkkvalidator.local", password="Tester@123", role="qa_engineer"),
    DevSeedUser(
        username="dataengineer",
        email="dataengineer@tkkvalidator.local",
        password="Data@123",
        role="data_engineer",
    ),
    DevSeedUser(username="viewer", email="viewer@tkkvalidator.local", password="Viewer@123", role="viewer"),
    DevSeedUser(username="guest", email="guest@tkkvalidator.local", password="Guest@123", role="guest"),
)


def seed_development_data(
    app_env: EnvironmentProfile,
    auth_repository: InMemoryAuthRepository,
    user_mgmt_repository: InMemoryUserManagementRepository,
) -> None:
    if app_env not in {EnvironmentProfile.LOCAL, EnvironmentProfile.DEV}:
        return

    admin_user_id = _seed_auth_users(auth_repository)
    _seed_org_hierarchy(user_mgmt_repository, admin_user_id)
    _seed_memberships(auth_repository, user_mgmt_repository)


def _seed_auth_users(auth_repository: InMemoryAuthRepository) -> str:
    admin_user_id = ""

    for entry in DEV_SEED_USERS:
        existing = auth_repository.get_user_by_email(entry.email)
        if existing:
            existing.role = entry.role
            existing.permissions = DEFAULT_ROLES.get(entry.role, [])
            auth_repository.update_user(existing)
            if entry.username == "admin":
                admin_user_id = existing.id
            continue

        user = AuthUser(
            id=f"dev-user-{entry.username}",
            tenant_id=ORG_ID,
            email=entry.email,
            hashed_password=hash_password(entry.password),
            is_active=True,
            is_email_verified=True,
            role=entry.role,
            permissions=DEFAULT_ROLES.get(entry.role, []),
        )
        auth_repository.create_user(user)
        if entry.username == "admin":
            admin_user_id = user.id

    return admin_user_id


def _seed_org_hierarchy(repository: InMemoryUserManagementRepository, admin_user_id: str) -> None:
    if not repository.get_organization(ORG_ID):
        repository.create_organization(
            Organization(
                id=ORG_ID,
                name="TKK Technologies Pvt Ltd",
                slug="tkk-technologies-pvt-ltd",
                owner_user_id=admin_user_id,
                settings={"display_org_id": ORG_ID},
            )
        )

    if not repository.get_team(TEAM_ID):
        repository.create_team(
            Team(
                id=TEAM_ID,
                organization_id=ORG_ID,
                name="Data Engineering Team",
                owner_user_id=admin_user_id,
                settings={"display_team_id": TEAM_ID},
            )
        )

    if not repository.get_project(PROJECT_AMEX_ID):
        repository.create_project(
            Project(
                id=PROJECT_AMEX_ID,
                organization_id=ORG_ID,
                team_id=TEAM_ID,
                name="American Express Data Migration",
                owner_user_id=admin_user_id,
                settings={"project_code": PROJECT_AMEX_ID},
            )
        )

    if not repository.get_project(PROJECT_SNOWFLAKE_ID):
        repository.create_project(
            Project(
                id=PROJECT_SNOWFLAKE_ID,
                organization_id=ORG_ID,
                team_id=TEAM_ID,
                name="Snowflake Migration Validation",
                owner_user_id=admin_user_id,
                settings={"project_code": PROJECT_SNOWFLAKE_ID},
            )
        )


def _seed_memberships(
    auth_repository: InMemoryAuthRepository,
    user_mgmt_repository: InMemoryUserManagementRepository,
) -> None:
    membership_index = {
        (
            membership.user_id,
            membership.organization_id,
            membership.team_id,
            membership.project_id,
        )
        for membership in user_mgmt_repository.memberships.values()
    }

    for entry in DEV_SEED_USERS:
        user = auth_repository.get_user_by_email(entry.email)
        if not user:
            continue

        membership_key = (user.id, ORG_ID, TEAM_ID, None)
        if membership_key in membership_index:
            continue

        user_mgmt_repository.create_membership(
            UserMembership(
                user_id=user.id,
                email=user.email,
                organization_id=ORG_ID,
                team_id=TEAM_ID,
                project_id=None,
                role_name=entry.role,
                custom_permissions=[],
                is_active=True,
            )
        )
