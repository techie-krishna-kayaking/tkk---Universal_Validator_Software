from datetime import datetime

from pydantic import BaseModel, Field

from app.models.config_mgmt import ConfigSource, ConnectionType


class ConnectionConfigCreate(BaseModel):
    tenant_id: str = Field(min_length=2)
    name: str = Field(min_length=2)
    connection_type: ConnectionType
    source: ConfigSource
    credentials: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)
    rotate_after_days: int = Field(default=90, ge=1, le=365)


class ConnectionConfigUpdate(BaseModel):
    credentials: dict | None = None
    metadata: dict | None = None
    is_active: bool | None = None
    rotate_after_days: int | None = Field(default=None, ge=1, le=365)


class ConnectionConfigResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    connection_type: ConnectionType
    source: ConfigSource
    masked_credentials: dict
    metadata: dict
    is_active: bool
    version: int
    rotate_after_days: int
    rotated_at: datetime | None


class ConnectionTestResult(BaseModel):
    success: bool
    details: dict


class CredentialValidationResult(BaseModel):
    valid: bool
    missing_fields: list[str]


class SecretRotationRequest(BaseModel):
    key: str = Field(min_length=1)
    value: str = Field(min_length=1)


class SourceReloadRequest(BaseModel):
    tenant_id: str = Field(min_length=2)


class SourceSnapshotResponse(BaseModel):
    source: ConfigSource
    revision: int
    data: dict


class ConfigAuditResponse(BaseModel):
    id: str
    tenant_id: str
    actor_user_id: str
    action: str
    connection_id: str | None
    outcome: str
    details: dict
    created_at: datetime
