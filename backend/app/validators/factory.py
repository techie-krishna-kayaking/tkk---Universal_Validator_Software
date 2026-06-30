from app.validators.catalog import register_catalog_validators
from app.validators.loader import ValidatorLoader
from app.validators.registry import ValidatorRegistry


class ValidatorFactory:
    def __init__(self, registry: ValidatorRegistry, loader: ValidatorLoader) -> None:
        self.registry = registry
        self.loader = loader

    @classmethod
    def with_defaults(cls) -> "ValidatorFactory":
        registry = ValidatorRegistry()
        register_catalog_validators(registry)
        loader = ValidatorLoader(registry)
        return cls(registry=registry, loader=loader)

    def discover_plugins(
        self,
        packages: list[str] | None = None,
        paths: list[str] | None = None,
        entrypoint_group: str | None = "tkk_uv.validators",
    ) -> dict[str, list[str]]:
        loaded: dict[str, list[str]] = {"packages": [], "paths": [], "entrypoints": []}

        for package in packages or []:
            loaded["packages"].extend(self.loader.discover_from_package(package))

        if paths:
            loaded["paths"].extend(self.loader.discover_from_paths(paths))

        if entrypoint_group:
            loaded["entrypoints"].extend(self.loader.discover_from_entrypoints(entrypoint_group))

        return loaded

    def create_validator(self, key: str, runtime_config: dict | None = None):
        return self.registry.create(key, runtime_config=runtime_config)
