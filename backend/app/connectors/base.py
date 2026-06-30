from abc import ABC, abstractmethod
from typing import Any

from app.connectors.sdk import (
    ConnectionTestResult,
    ConnectorCapability,
    ConnectorContext,
    ConnectorReadResult,
    ConnectorSpec,
    MetadataResult,
    PrimaryKeyResult,
    SampleDataResult,
    SchemaResult,
)


class BaseConnector(ABC):
    def __init__(self, spec: ConnectorSpec, config: dict[str, Any]) -> None:
        self.spec = spec
        self.config = config
        self._timeout_seconds = 30
        self._retry_attempts = 3

    def supports(self, capability: ConnectorCapability) -> bool:
        return capability in self.spec.capabilities

    @abstractmethod
    def authenticate(self, context: ConnectorContext) -> None:
        raise NotImplementedError

    @abstractmethod
    def test_connection(self, context: ConnectorContext) -> ConnectionTestResult:
        raise NotImplementedError

    @abstractmethod
    def discover_metadata(self, context: ConnectorContext) -> MetadataResult:
        raise NotImplementedError

    @abstractmethod
    def discover_schema(self, context: ConnectorContext, object_name: str | None = None) -> SchemaResult:
        raise NotImplementedError

    @abstractmethod
    def discover_primary_keys(
        self,
        context: ConnectorContext,
        object_name: str | None = None,
    ) -> PrimaryKeyResult:
        raise NotImplementedError

    @abstractmethod
    def sample_data(
        self,
        context: ConnectorContext,
        object_name: str | None = None,
        limit: int = 10,
    ) -> SampleDataResult:
        raise NotImplementedError

    @abstractmethod
    def read_page(
        self,
        context: ConnectorContext,
        object_name: str | None = None,
        cursor: str | None = None,
        page_size: int = 100,
    ) -> ConnectorReadResult:
        raise NotImplementedError

    @abstractmethod
    def stream_data(self, context: ConnectorContext, object_name: str | None = None) -> ConnectorReadResult:
        raise NotImplementedError

    @abstractmethod
    def incremental_read(
        self,
        context: ConnectorContext,
        object_name: str | None = None,
        since: str | None = None,
    ) -> ConnectorReadResult:
        raise NotImplementedError

    @abstractmethod
    def read_with_pushdown_filters(
        self,
        context: ConnectorContext,
        object_name: str | None = None,
        filters: dict[str, Any] | None = None,
    ) -> ConnectorReadResult:
        raise NotImplementedError

    @abstractmethod
    def parallel_read(
        self,
        context: ConnectorContext,
        object_name: str | None = None,
        partitions: int = 4,
    ) -> ConnectorReadResult:
        raise NotImplementedError

    @abstractmethod
    def get_pool_stats(self) -> dict[str, Any]:
        raise NotImplementedError

    def set_retry_policy(self, attempts: int) -> None:
        self._retry_attempts = max(1, attempts)

    def set_timeout_seconds(self, timeout_seconds: int) -> None:
        self._timeout_seconds = max(1, timeout_seconds)
