from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ConnectorCategory(StrEnum):
    FILES = "files"
    DATABASES = "databases"
    CLOUD_STORAGE = "cloud_storage"
    BIG_DATA = "big_data"
    APIS = "apis"


class ConnectorCapability(StrEnum):
    CONNECTION_TEST = "connection_test"
    AUTHENTICATION = "authentication"
    METADATA_DISCOVERY = "metadata_discovery"
    SCHEMA_DISCOVERY = "schema_discovery"
    PRIMARY_KEY_DISCOVERY = "primary_key_discovery"
    SAMPLE_DATA = "sample_data"
    PAGINATION = "pagination"
    STREAMING = "streaming"
    INCREMENTAL_READ = "incremental_read"
    PUSHDOWN_FILTERS = "pushdown_filters"
    PARALLEL_READ = "parallel_read"
    CONNECTION_POOLING = "connection_pooling"
    RETRY_LOGIC = "retry_logic"
    TIMEOUT = "timeout"
    ERROR_HANDLING = "error_handling"
    METRICS = "metrics"
    LOGGING = "logging"


@dataclass(frozen=True)
class ConnectorSpec:
    key: str
    display_name: str
    category: ConnectorCategory
    provider: str
    capabilities: tuple[ConnectorCapability, ...]


@dataclass
class ConnectorContext:
    tenant_id: str
    user_id: str | None = None
    request_id: str | None = None


@dataclass
class ConnectionTestResult:
    success: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class MetadataResult:
    objects: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class SchemaResult:
    columns: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class PrimaryKeyResult:
    keys: list[str] = field(default_factory=list)


@dataclass
class SampleDataResult:
    rows: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ConnectorReadResult:
    rows: list[dict[str, Any]] = field(default_factory=list)
    next_cursor: str | None = None


ALL_CAPABILITIES: tuple[ConnectorCapability, ...] = tuple(ConnectorCapability)
