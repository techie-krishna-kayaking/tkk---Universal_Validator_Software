import pytest

from app.connectors.base import BaseConnector
from app.connectors.factory import ConnectorFactory
from app.connectors.pipeline import ConnectorOperation, ConnectorTask, ConnectorPipelineRunner
from app.connectors.sdk import ALL_CAPABILITIES, ConnectorCategory, ConnectorContext


def test_catalog_registration_and_factory_create() -> None:
    factory = ConnectorFactory.with_defaults()

    specs = factory.registry.list_specs()
    assert len(specs) == 57
    assert all(spec.capabilities == ALL_CAPABILITIES for spec in specs)

    connector = factory.create_connector(
        "db.postgresql",
        runtime_config={
            "required": ["host", "username", "password"],
            "host": "localhost",
            "username": "postgres",
            "password": "secret",
        },
    )
    assert isinstance(connector, BaseConnector)
    result = connector.test_connection(ConnectorContext(tenant_id="tenant-a"))
    assert result.success is True


def test_category_filtering() -> None:
    factory = ConnectorFactory.with_defaults()
    file_specs = factory.registry.list_specs(ConnectorCategory.FILES)
    assert len(file_specs) == 18
    api_specs = factory.registry.list_specs(ConnectorCategory.APIS)
    assert len(api_specs) == 5


@pytest.mark.asyncio
async def test_pipeline_dependency_order_and_retry_handling() -> None:
    factory = ConnectorFactory.with_defaults()
    runner = ConnectorPipelineRunner(factory)
    context = ConnectorContext(tenant_id="tenant-a")

    tasks = [
        ConnectorTask(
            task_id="a",
            connector_key="api.rest",
            operation=ConnectorOperation.TEST_CONNECTION,
            params={"context": context},
            runtime_config={"required": []},
        ),
        ConnectorTask(
            task_id="b",
            connector_key="api.rest",
            operation=ConnectorOperation.TEST_CONNECTION,
            params={"context": context},
            runtime_config={"required": ["token"]},
            depends_on=["a"],
            retries=2,
        ),
    ]

    results = await runner.run(tasks, max_parallelism=2)
    assert results["a"].success is True
    assert results["b"].success is False
    assert results["b"].attempts == 3
