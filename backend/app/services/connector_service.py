from app.connectors.factory import ConnectorFactory
from app.connectors.pipeline import ConnectorPipelineRunner
from app.connectors.sdk import ConnectorCategory, ConnectorSpec


class ConnectorService:
    def __init__(self, factory: ConnectorFactory | None = None) -> None:
        self.factory = factory or ConnectorFactory.with_defaults()
        self.pipeline_runner = ConnectorPipelineRunner(self.factory)

    def list_connectors(self, category: ConnectorCategory | None = None) -> list[ConnectorSpec]:
        return self.factory.registry.list_specs(category)

    def create_connector(self, key: str, runtime_config: dict | None = None):
        return self.factory.create_connector(key, runtime_config)

    def discover_plugins(
        self,
        packages: list[str] | None = None,
        paths: list[str] | None = None,
    ) -> dict[str, list[str]]:
        return self.factory.discover_plugins(packages=packages, paths=paths)
