from app.connectors.base import BaseConnector
from app.connectors.sdk import (
    ALL_CAPABILITIES,
    ConnectionTestResult,
    ConnectorCategory,
    ConnectorReadResult,
    ConnectorSpec,
    MetadataResult,
    PrimaryKeyResult,
    SampleDataResult,
    SchemaResult,
)


class ExampleConnector(BaseConnector):
    def authenticate(self, context):
        _ = context

    def test_connection(self, context):
        _ = context
        return ConnectionTestResult(success=True, message="ok", details={})

    def discover_metadata(self, context):
        _ = context
        return MetadataResult(objects=[])

    def discover_schema(self, context, object_name=None):
        _ = context
        _ = object_name
        return SchemaResult(columns=[])

    def discover_primary_keys(self, context, object_name=None):
        _ = context
        _ = object_name
        return PrimaryKeyResult(keys=[])

    def sample_data(self, context, object_name=None, limit=10):
        _ = context
        _ = object_name
        _ = limit
        return SampleDataResult(rows=[])

    def read_page(self, context, object_name=None, cursor=None, page_size=100):
        _ = context
        _ = object_name
        _ = cursor
        _ = page_size
        return ConnectorReadResult(rows=[], next_cursor=None)

    def stream_data(self, context, object_name=None):
        _ = context
        _ = object_name
        return ConnectorReadResult(rows=[], next_cursor=None)

    def incremental_read(self, context, object_name=None, since=None):
        _ = context
        _ = object_name
        _ = since
        return ConnectorReadResult(rows=[], next_cursor=None)

    def read_with_pushdown_filters(self, context, object_name=None, filters=None):
        _ = context
        _ = object_name
        _ = filters
        return ConnectorReadResult(rows=[], next_cursor=None)

    def parallel_read(self, context, object_name=None, partitions=4):
        _ = context
        _ = object_name
        _ = partitions
        return ConnectorReadResult(rows=[], next_cursor=None)

    def get_pool_stats(self):
        return {"active_connections": 0, "max_connections": 10}


def register_plugins(registry):
    registry.register(
        spec=ConnectorSpec(
            key="custom.example",
            display_name="Example Connector",
            category=ConnectorCategory.APIS,
            provider="example",
            capabilities=ALL_CAPABILITIES,
        ),
        builder=lambda spec, config: ExampleConnector(spec, config),
        default_config={},
    )
