from dataclasses import dataclass
from typing import Any, Callable

from app.connectors.base import BaseConnector
from app.connectors.errors import ConnectorNotFoundError, ConnectorRegistrationError
from app.connectors.sdk import ConnectorCategory, ConnectorSpec

ConnectorBuilder = Callable[[ConnectorSpec, dict[str, Any]], BaseConnector]


@dataclass
class RegisteredConnector:
    spec: ConnectorSpec
    builder: ConnectorBuilder
    default_config: dict[str, Any]


class ConnectorRegistry:
    def __init__(self) -> None:
        self._registry: dict[str, RegisteredConnector] = {}

    def register(
        self,
        spec: ConnectorSpec,
        builder: ConnectorBuilder,
        default_config: dict[str, Any] | None = None,
    ) -> None:
        if spec.key in self._registry:
            raise ConnectorRegistrationError(f"Connector already registered: {spec.key}")
        self._registry[spec.key] = RegisteredConnector(
            spec=spec,
            builder=builder,
            default_config=default_config or {},
        )

    def get_spec(self, key: str) -> ConnectorSpec:
        registered = self._registry.get(key)
        if not registered:
            raise ConnectorNotFoundError(f"Connector not found: {key}")
        return registered.spec

    def has(self, key: str) -> bool:
        return key in self._registry

    def list_specs(self, category: ConnectorCategory | None = None) -> list[ConnectorSpec]:
        specs = [item.spec for item in self._registry.values()]
        if category is None:
            return sorted(specs, key=lambda value: value.key)
        return sorted([item for item in specs if item.category == category], key=lambda value: value.key)

    def create(self, key: str, runtime_config: dict[str, Any] | None = None) -> BaseConnector:
        registered = self._registry.get(key)
        if not registered:
            raise ConnectorNotFoundError(f"Connector not found: {key}")
        config = dict(registered.default_config)
        if runtime_config:
            config.update(runtime_config)
        return registered.builder(registered.spec, config)
