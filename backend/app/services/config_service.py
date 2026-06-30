import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Callable

from app.config.settings import Settings
from app.core.secret_crypto import SecretCrypto
from app.exceptions.custom import ApiError
from app.models.config_mgmt import ConfigAuditEvent, ConfigSource, ConnectionConfig, ConnectionType
from app.repositories.config_repository import InMemoryConfigRepository
from app.schemas.config_mgmt import (
    ConnectionConfigCreate,
    ConnectionConfigUpdate,
    ConnectionTestResult,
    CredentialValidationResult,
    SecretRotationRequest,
)
from app.utils.yaml_loader import load_yaml


class ConfigurationManagementService:
    def __init__(self, settings: Settings, repository: InMemoryConfigRepository) -> None:
        self.settings = settings
        self.repository = repository
        self.crypto = SecretCrypto(settings.config_encryption_key)
        self.cache_ttl_seconds = settings.secret_cache_ttl_seconds
        self._cache: dict[str, tuple[datetime, dict[str, Any]]] = {}
        self._rotation_hooks: list[Callable[[ConnectionConfig, str], None]] = []

    def register_rotation_hook(self, callback: Callable[[ConnectionConfig, str], None]) -> None:
        self._rotation_hooks.append(callback)

    def create_connection(self, payload: ConnectionConfigCreate, actor_user_id: str) -> ConnectionConfig:
        self._validate_credentials(payload.connection_type, payload.credentials)
        encrypted_payload = self._encrypt_credentials(payload.credentials)
        connection = ConnectionConfig(
            tenant_id=payload.tenant_id,
            name=payload.name,
            connection_type=payload.connection_type.value,
            source=payload.source.value,
            encrypted_payload=encrypted_payload,
            config_metadata=payload.metadata,
            rotate_after_days=payload.rotate_after_days,
            is_active=True,
            version=1,
        )
        self.repository.create_connection(connection)
        self._audit(payload.tenant_id, actor_user_id, "config.create", connection.id, {"name": payload.name})
        return connection

    def list_connections(self, tenant_id: str | None = None) -> list[ConnectionConfig]:
        return self.repository.list_connections(tenant_id)

    def get_connection(self, connection_id: str) -> ConnectionConfig:
        connection = self.repository.get_connection(connection_id)
        if not connection:
            raise ApiError(code="connection_not_found", message="Connection not found", status_code=404)
        return connection

    def update_connection(self, connection_id: str, payload: ConnectionConfigUpdate, actor_user_id: str) -> ConnectionConfig:
        connection = self.get_connection(connection_id)
        if payload.credentials is not None:
            self._validate_credentials(ConnectionType(connection.connection_type), payload.credentials)
            connection.encrypted_payload = self._encrypt_credentials(payload.credentials)
            connection.version += 1
            self._cache.pop(self._cache_key(connection.id, connection.version - 1), None)
        if payload.metadata is not None:
            connection.config_metadata = payload.metadata
        if payload.is_active is not None:
            connection.is_active = payload.is_active
        if payload.rotate_after_days is not None:
            connection.rotate_after_days = payload.rotate_after_days

        self.repository.update_connection(connection)
        self._audit(connection.tenant_id, actor_user_id, "config.update", connection.id, {})
        return connection

    def delete_connection(self, connection_id: str, actor_user_id: str) -> None:
        connection = self.get_connection(connection_id)
        self.repository.delete_connection(connection_id)
        self._audit(connection.tenant_id, actor_user_id, "config.delete", connection_id, {})

    def validate_credentials(self, connection_id: str) -> CredentialValidationResult:
        connection = self.get_connection(connection_id)
        credentials = self.get_plain_credentials(connection)
        missing_fields = self._missing_fields(ConnectionType(connection.connection_type), credentials)
        return CredentialValidationResult(valid=len(missing_fields) == 0, missing_fields=missing_fields)

    def test_connection(self, connection_id: str) -> ConnectionTestResult:
        connection = self.get_connection(connection_id)
        credentials = self.get_plain_credentials(connection)
        validation = self._missing_fields(ConnectionType(connection.connection_type), credentials)
        if validation:
            return ConnectionTestResult(success=False, details={"missing_fields": validation})

        if connection.connection_type == ConnectionType.API.value:
            base_url = str(credentials.get("base_url", ""))
            return ConnectionTestResult(
                success=base_url.startswith("http://") or base_url.startswith("https://"),
                details={"base_url": base_url},
            )

        return ConnectionTestResult(success=True, details={"message": "connection parameters validated"})

    def rotate_secret(
        self,
        connection_id: str,
        payload: SecretRotationRequest,
        actor_user_id: str,
    ) -> ConnectionConfig:
        connection = self.get_connection(connection_id)
        credentials = self.get_plain_credentials(connection)
        if payload.key not in credentials:
            raise ApiError(code="credential_key_not_found", message="Credential key not found", status_code=404)

        credentials[payload.key] = payload.value
        connection.encrypted_payload = self._encrypt_credentials(credentials)
        connection.version += 1
        connection.rotated_at = datetime.now(UTC)
        self.repository.update_connection(connection)
        for callback in self._rotation_hooks:
            callback(connection, payload.key)

        self._audit(
            connection.tenant_id,
            actor_user_id,
            "config.rotate_secret",
            connection.id,
            {"key": payload.key},
        )
        return connection

    def get_masked_credentials(self, connection: ConnectionConfig) -> dict[str, str]:
        plain = self.get_plain_credentials(connection)
        return {key: self._mask_value(str(value)) for key, value in plain.items()}

    def get_plain_credentials(self, connection: ConnectionConfig) -> dict[str, Any]:
        cache_key = self._cache_key(connection.id, connection.version)
        now = datetime.now(UTC)
        cached = self._cache.get(cache_key)
        if cached and cached[0] > now:
            return cached[1]

        decrypted = self._decrypt_credentials(connection.encrypted_payload)
        self._cache[cache_key] = (now + timedelta(seconds=self.cache_ttl_seconds), decrypted)
        return decrypted

    def reload_sources(self, tenant_id: str, actor_user_id: str) -> dict[str, dict]:
        source_payloads = {
            ConfigSource.DOTENV: self._load_dotenv(),
            ConfigSource.YAML: self._load_yaml(),
            ConfigSource.ENV: self._load_environment_vars(),
            ConfigSource.AWS_SECRETS_MANAGER: self._load_json_blob(self.settings.aws_secrets_manager_blob),
            ConfigSource.AZURE_KEY_VAULT: self._load_json_blob(self.settings.azure_key_vault_blob),
            ConfigSource.GOOGLE_SECRET_MANAGER: self._load_json_blob(self.settings.google_secret_manager_blob),
            ConfigSource.HASHICORP_VAULT: self._load_json_blob(self.settings.hashicorp_vault_blob),
        }

        existing = self.repository.list_snapshots(tenant_id)
        revision_offset = len(existing)
        for idx, (source, data) in enumerate(source_payloads.items(), start=1):
            self.repository.save_snapshot(tenant_id=tenant_id, source=source, data=data, revision=revision_offset + idx)

        self._audit(
            tenant_id,
            actor_user_id,
            "config.reload_sources",
            None,
            {"sources": [item.value for item in source_payloads.keys()]},
        )
        return {source.value: data for source, data in source_payloads.items()}

    def list_source_snapshots(self, tenant_id: str) -> list[dict]:
        snapshots = self.repository.list_snapshots(tenant_id)
        return [{"source": item.source, "revision": item.revision, "data": item.data} for item in snapshots]

    def list_audits(self, tenant_id: str | None = None) -> list[ConfigAuditEvent]:
        return self.repository.list_audits(tenant_id)

    def _encrypt_credentials(self, credentials: dict) -> dict[str, str]:
        encrypted: dict[str, str] = {}
        for key, value in credentials.items():
            serialized = json.dumps(value)
            encrypted[key] = self.crypto.encrypt(serialized)
        return encrypted

    def _decrypt_credentials(self, encrypted_payload: dict[str, str]) -> dict[str, Any]:
        decrypted: dict[str, Any] = {}
        for key, value in encrypted_payload.items():
            serialized = self.crypto.decrypt(value)
            decrypted[key] = json.loads(serialized)
        return decrypted

    def _mask_value(self, value: str) -> str:
        if len(value) <= 4:
            return "*" * len(value)
        return f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"

    def _cache_key(self, connection_id: str, version: int) -> str:
        return f"{connection_id}:{version}"

    def _required_fields(self, connection_type: ConnectionType) -> list[str]:
        return {
            ConnectionType.DATABASE: ["host", "port", "database", "username", "password"],
            ConnectionType.CLOUD: ["provider", "access_key", "secret_key"],
            ConnectionType.API: ["base_url", "auth_type", "token"],
            ConnectionType.FILE: ["path", "format"],
            ConnectionType.STORAGE: ["bucket", "region", "access_key", "secret_key"],
            ConnectionType.SMTP: ["host", "port", "username", "password"],
            ConnectionType.SLACK: ["webhook_url"],
            ConnectionType.MICROSOFT_TEAMS: ["webhook_url"],
            ConnectionType.LLM_PROVIDER: ["provider", "api_key", "model"],
            ConnectionType.NOTIFICATION: ["channel"],
        }[connection_type]

    def _missing_fields(self, connection_type: ConnectionType, credentials: dict) -> list[str]:
        required = self._required_fields(connection_type)
        missing: list[str] = []
        for key in required:
            if key not in credentials:
                missing.append(key)
                continue
            value = credentials.get(key)
            if value is None:
                missing.append(key)
            elif isinstance(value, str) and value.strip() == "":
                missing.append(key)
        return missing

    def _validate_credentials(self, connection_type: ConnectionType, credentials: dict) -> None:
        missing = self._missing_fields(connection_type, credentials)
        if missing:
            raise ApiError(
                code="invalid_credentials",
                message=f"Missing credential fields: {', '.join(missing)}",
                status_code=400,
            )

    def _load_dotenv(self) -> dict:
        payload: dict[str, str] = {}
        file_path = Path(self.settings.dotenv_source_path)
        if not file_path.exists():
            return payload

        for line in file_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            payload[key.strip()] = value.strip().strip('"').strip("'")
        return payload

    def _load_yaml(self) -> dict:
        file_path = Path(self.settings.yaml_source_path)
        if not file_path.exists():
            return {}
        return load_yaml(file_path)

    def _load_environment_vars(self) -> dict:
        prefix = self.settings.config_env_prefix
        return {key: value for key, value in os.environ.items() if key.startswith(prefix)}

    def _load_json_blob(self, blob: str) -> dict:
        if not blob.strip():
            return {}
        try:
            parsed = json.loads(blob)
            if isinstance(parsed, dict):
                return parsed
            return {"value": parsed}
        except json.JSONDecodeError:
            return {}

    def _audit(
        self,
        tenant_id: str,
        actor_user_id: str,
        action: str,
        connection_id: str | None,
        details: dict,
    ) -> None:
        self.repository.add_audit(
            ConfigAuditEvent(
                tenant_id=tenant_id,
                actor_user_id=actor_user_id,
                action=action,
                connection_id=connection_id,
                outcome="success",
                details=details,
            )
        )
