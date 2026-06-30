from dataclasses import dataclass
from typing import Callable

from app.validators.base import BaseValidator
from app.validators.errors import ValidatorNotFoundError, ValidatorRegistrationError
from app.validators.sdk import ValidatorSpec

ValidatorBuilder = Callable[[ValidatorSpec, dict], BaseValidator]


@dataclass
class RegisteredValidator:
    spec: ValidatorSpec
    builder: ValidatorBuilder
    default_config: dict


class ValidatorRegistry:
    def __init__(self) -> None:
        self._registry: dict[str, RegisteredValidator] = {}

    def register(
        self,
        spec: ValidatorSpec,
        builder: ValidatorBuilder,
        default_config: dict | None = None,
    ) -> None:
        if spec.key in self._registry:
            raise ValidatorRegistrationError(f"Validator already registered: {spec.key}")
        self._registry[spec.key] = RegisteredValidator(spec=spec, builder=builder, default_config=default_config or {})

    def has(self, key: str) -> bool:
        return key in self._registry

    def get_spec(self, key: str) -> ValidatorSpec:
        if key not in self._registry:
            raise ValidatorNotFoundError(f"Validator not found: {key}")
        return self._registry[key].spec

    def list_specs(self) -> list[ValidatorSpec]:
        return sorted([item.spec for item in self._registry.values()], key=lambda value: value.key)

    def create(self, key: str, runtime_config: dict | None = None) -> BaseValidator:
        if key not in self._registry:
            raise ValidatorNotFoundError(f"Validator not found: {key}")
        registered = self._registry[key]
        config = dict(registered.default_config)
        if runtime_config:
            config.update(runtime_config)
        return registered.builder(registered.spec, config)
