from app.config.profiles import EnvironmentProfile
from app.core.dev_seed import ORG_ID, PROJECT_AMEX_ID, PROJECT_SNOWFLAKE_ID, TEAM_ID, seed_development_data
from app.repositories.auth_repository import InMemoryAuthRepository
from app.repositories.user_mgmt_repository import InMemoryUserManagementRepository


def test_seed_development_data_creates_users_org_team_and_projects() -> None:
    auth_repository = InMemoryAuthRepository()
    user_mgmt_repository = InMemoryUserManagementRepository()

    seed_development_data(EnvironmentProfile.DEV, auth_repository, user_mgmt_repository)

    admin_user = auth_repository.get_user_by_email("admin@tkkvalidator.local")
    assert admin_user is not None
    assert admin_user.role == "platform_admin"
    assert admin_user.tenant_id == ORG_ID

    org = user_mgmt_repository.get_organization(ORG_ID)
    team = user_mgmt_repository.get_team(TEAM_ID)
    amex = user_mgmt_repository.get_project(PROJECT_AMEX_ID)
    snowflake = user_mgmt_repository.get_project(PROJECT_SNOWFLAKE_ID)

    assert org is not None
    assert team is not None
    assert amex is not None
    assert snowflake is not None
    assert len(user_mgmt_repository.memberships) >= 8


def test_seed_development_data_is_noop_for_prod() -> None:
    auth_repository = InMemoryAuthRepository()
    user_mgmt_repository = InMemoryUserManagementRepository()

    seed_development_data(EnvironmentProfile.PROD, auth_repository, user_mgmt_repository)

    assert auth_repository.get_user_by_email("admin@tkkvalidator.local") is None
    assert user_mgmt_repository.get_organization(ORG_ID) is None
