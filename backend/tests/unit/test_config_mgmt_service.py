from app.config.settings import Settings
from app.models.config_mgmt import ConfigSource, ConnectionType
from app.repositories.config_repository import InMemoryConfigRepository
from app.schemas.config_mgmt import ConnectionConfigCreate, SecretRotationRequest
from app.services.config_service import ConfigurationManagementService


def test_create_and_rotate_connection_secrets() -> None:
    service = ConfigurationManagementService(
        settings=Settings(CONFIG_ENCRYPTION_KEY="unit-test-config-key-material"),
        repository=InMemoryConfigRepository(),
    )

    connection = service.create_connection(
        ConnectionConfigCreate(
            tenant_id="tenant-a",
            name="primary-db",
            connection_type=ConnectionType.DATABASE,
            source=ConfigSource.ENV,
            credentials={
                "host": "localhost",
                "port": 5432,
                "database": "app_db",
                "username": "dbuser",
                "password": "p@ssw0rd",
            },
            metadata={"purpose": "reporting"},
        ),
        actor_user_id="user-1",
    )

    plain = service.get_plain_credentials(connection)
    assert plain["password"] == "p@ssw0rd"

    masked = service.get_masked_credentials(connection)
    assert masked["password"] != "p@ssw0rd"
    assert "*" in masked["password"]

    rotated = service.rotate_secret(
        connection.id,
        SecretRotationRequest(key="password", value="N3wP@ssword"),
        actor_user_id="user-1",
    )
    assert rotated.version == 2
    assert service.get_plain_credentials(rotated)["password"] == "N3wP@ssword"


def test_reload_sources_and_validate_credentials() -> None:
    settings = Settings(
        CONFIG_ENCRYPTION_KEY="unit-test-config-key-material",
        AWS_SECRETS_MANAGER_BLOB='{"AWS_DB_PASSWORD":"encrypted"}',
        AZURE_KEY_VAULT_BLOB='{"azure-secret":"value"}',
        GOOGLE_SECRET_MANAGER_BLOB='{"gcp-secret":"value"}',
        HASHICORP_VAULT_BLOB='{"vault-secret":"value"}',
    )
    service = ConfigurationManagementService(settings=settings, repository=InMemoryConfigRepository())

    connection = service.create_connection(
        ConnectionConfigCreate(
            tenant_id="tenant-a",
            name="slack-notifier",
            connection_type=ConnectionType.SLACK,
            source=ConfigSource.YAML,
            credentials={"webhook_url": "https://hooks.slack.com/services/X/Y/Z"},
            metadata={},
        ),
        actor_user_id="user-1",
    )

    validation = service.validate_credentials(connection.id)
    assert validation.valid is True

    snapshots = service.reload_sources("tenant-a", actor_user_id="user-1")
    assert "aws_secrets_manager" in snapshots
    assert "azure_key_vault" in snapshots
    assert "google_secret_manager" in snapshots
    assert "hashicorp_vault" in snapshots
