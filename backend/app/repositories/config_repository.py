from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from app.models.config_mgmt import ConfigAuditEvent, ConfigSource, ConfigSourceSnapshot, ConnectionConfig


@dataclass
class InMemoryConfigRepository:
    connections: dict[str, ConnectionConfig] = field(default_factory=dict)
    snapshots: dict[str, list[ConfigSourceSnapshot]] = field(default_factory=dict)
    audits: list[ConfigAuditEvent] = field(default_factory=list)

    def create_connection(self, connection: ConnectionConfig) -> ConnectionConfig:
        connection.id = connection.id or str(uuid4())
        connection.encrypted_payload = connection.encrypted_payload or {}
        connection.config_metadata = connection.config_metadata or {}
        connection.is_active = True if connection.is_active is None else connection.is_active
        connection.version = connection.version or 1
        connection.rotate_after_days = connection.rotate_after_days or 90
        connection.created_at = connection.created_at or datetime.now(UTC)
        connection.updated_at = connection.updated_at or datetime.now(UTC)
        self.connections[connection.id] = connection
        return connection

    def update_connection(self, connection: ConnectionConfig) -> ConnectionConfig:
        connection.updated_at = datetime.now(UTC)
        self.connections[connection.id] = connection
        return connection

    def get_connection(self, connection_id: str) -> ConnectionConfig | None:
        return self.connections.get(connection_id)

    def list_connections(self, tenant_id: str | None = None) -> list[ConnectionConfig]:
        if tenant_id is None:
            return list(self.connections.values())
        return [item for item in self.connections.values() if item.tenant_id == tenant_id]

    def delete_connection(self, connection_id: str) -> bool:
        return self.connections.pop(connection_id, None) is not None

    def save_snapshot(
        self,
        tenant_id: str,
        source: ConfigSource,
        data: dict,
        revision: int,
    ) -> ConfigSourceSnapshot:
        snapshot = ConfigSourceSnapshot(
            tenant_id=tenant_id,
            source=source.value,
            data=data,
            revision=revision,
        )
        snapshot.id = snapshot.id or str(uuid4())
        snapshot.created_at = snapshot.created_at or datetime.now(UTC)
        bucket = self.snapshots.setdefault(tenant_id, [])
        bucket.append(snapshot)
        return snapshot

    def list_snapshots(self, tenant_id: str) -> list[ConfigSourceSnapshot]:
        return list(self.snapshots.get(tenant_id, []))

    def add_audit(self, audit: ConfigAuditEvent) -> None:
        audit.id = audit.id or str(uuid4())
        audit.created_at = audit.created_at or datetime.now(UTC)
        self.audits.append(audit)

    def list_audits(self, tenant_id: str | None = None) -> list[ConfigAuditEvent]:
        if tenant_id is None:
            return list(self.audits)
        return [event for event in self.audits if event.tenant_id == tenant_id]
