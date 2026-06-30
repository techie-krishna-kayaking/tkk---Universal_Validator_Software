from typing import Any

from app.connectors.base import BaseConnector
from app.connectors.sdk import (
    ConnectionTestResult,
    ConnectorContext,
    ConnectorReadResult,
    MetadataResult,
    PrimaryKeyResult,
    SampleDataResult,
    SchemaResult,
)


class StaticConnector(BaseConnector):
    def authenticate(self, context: ConnectorContext) -> None:
        _ = context

    def test_connection(self, context: ConnectorContext) -> ConnectionTestResult:
        _ = context
        required = self.config.get("required", [])
        missing = [field for field in required if not self.config.get(field)]
        if missing:
            return ConnectionTestResult(
                success=False,
                message="Missing required connection fields",
                details={"missing": missing},
            )
        return ConnectionTestResult(success=True, message="Connection test succeeded", details={})

    def discover_metadata(self, context: ConnectorContext) -> MetadataResult:
        _ = context
        objects = self.config.get("objects", [])
        return MetadataResult(objects=objects)

    def discover_schema(self, context: ConnectorContext, object_name: str | None = None) -> SchemaResult:
        _ = context
        _ = object_name
        columns = self.config.get("schema", [])
        return SchemaResult(columns=columns)

    def discover_primary_keys(
        self,
        context: ConnectorContext,
        object_name: str | None = None,
    ) -> PrimaryKeyResult:
        _ = context
        _ = object_name
        return PrimaryKeyResult(keys=self.config.get("primary_keys", []))

    def sample_data(
        self,
        context: ConnectorContext,
        object_name: str | None = None,
        limit: int = 10,
    ) -> SampleDataResult:
        _ = context
        _ = object_name
        rows = self.config.get("sample_rows", [])
        return SampleDataResult(rows=rows[:limit])

    def read_page(
        self,
        context: ConnectorContext,
        object_name: str | None = None,
        cursor: str | None = None,
        page_size: int = 100,
    ) -> ConnectorReadResult:
        _ = context
        _ = object_name
        _ = cursor
        rows = self.config.get("rows", [])
        return ConnectorReadResult(rows=rows[:page_size], next_cursor=None)

    def stream_data(self, context: ConnectorContext, object_name: str | None = None) -> ConnectorReadResult:
        _ = context
        _ = object_name
        return ConnectorReadResult(rows=self.config.get("rows", []), next_cursor=None)

    def incremental_read(
        self,
        context: ConnectorContext,
        object_name: str | None = None,
        since: str | None = None,
    ) -> ConnectorReadResult:
        _ = context
        _ = object_name
        _ = since
        rows = self.config.get("rows", [])
        return ConnectorReadResult(rows=rows, next_cursor=None)

    def read_with_pushdown_filters(
        self,
        context: ConnectorContext,
        object_name: str | None = None,
        filters: dict[str, Any] | None = None,
    ) -> ConnectorReadResult:
        _ = context
        _ = object_name
        filters = filters or {}
        rows = self.config.get("rows", [])
        filtered = []
        for row in rows:
            if all(row.get(key) == value for key, value in filters.items()):
                filtered.append(row)
        return ConnectorReadResult(rows=filtered, next_cursor=None)

    def parallel_read(
        self,
        context: ConnectorContext,
        object_name: str | None = None,
        partitions: int = 4,
    ) -> ConnectorReadResult:
        _ = context
        _ = object_name
        _ = partitions
        return ConnectorReadResult(rows=self.config.get("rows", []), next_cursor=None)

    def get_pool_stats(self) -> dict[str, Any]:
        return {
            "max_connections": int(self.config.get("max_connections", 10)),
            "active_connections": int(self.config.get("active_connections", 0)),
            "retry_attempts": self._retry_attempts,
            "timeout_seconds": self._timeout_seconds,
        }
