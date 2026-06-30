from app.validators.factory import ValidatorFactory
from app.validators.pipeline import ValidationPipelineRunner
from app.validators.sdk import ValidatorSpec


class ValidationService:
    def __init__(self, factory: ValidatorFactory | None = None) -> None:
        self.factory = factory or ValidatorFactory.with_defaults()
        self.pipeline_runner = ValidationPipelineRunner(self.factory)

    def list_validators(self) -> list[ValidatorSpec]:
        return self.factory.registry.list_specs()

    def create_validator(self, key: str, runtime_config: dict | None = None):
        return self.factory.create_validator(key, runtime_config)

    def discover_plugins(
        self,
        packages: list[str] | None = None,
        paths: list[str] | None = None,
    ) -> dict[str, list[str]]:
        return self.factory.discover_plugins(packages=packages, paths=paths)
