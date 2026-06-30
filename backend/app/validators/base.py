from abc import ABC, abstractmethod
from typing import Any

from app.validators.sdk import ValidationContext, ValidationResult, ValidatorSpec


class BaseValidator(ABC):
    def __init__(self, spec: ValidatorSpec, config: dict[str, Any]) -> None:
        self.spec = spec
        self.config = config

    @abstractmethod
    def validate(self, context: ValidationContext) -> ValidationResult:
        raise NotImplementedError
