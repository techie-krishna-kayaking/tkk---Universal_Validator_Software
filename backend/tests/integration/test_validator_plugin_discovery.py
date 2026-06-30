from pathlib import Path

from app.validators.factory import ValidatorFactory
from app.validators.sdk import ValidationContext


def test_discover_validator_plugin_from_path(tmp_path: Path) -> None:
    plugin_file = tmp_path / "custom_validator.py"
    plugin_file.write_text(
        """
from app.validators.base import BaseValidator
from app.validators.sdk import ValidationResult, ValidationType, ValidatorSpec


class CustomPathValidator(BaseValidator):
    def validate(self, context):
        _ = context
        return ValidationResult(success=True, score=1.0, message=\"custom validator executed\")


def register_validators(registry):
    registry.register(
        spec=ValidatorSpec(
            key=\"validation.custom_path\",
            display_name=\"Custom Path Validator\",
            validation_type=ValidationType.CUSTOM_PYTHON,
            description=\"Custom plugin validator\",
        ),
        builder=lambda spec, config: CustomPathValidator(spec, config),
        default_config={},
    )
""",
        encoding="utf-8",
    )

    factory = ValidatorFactory.with_defaults()
    loaded = factory.discover_plugins(paths=[str(plugin_file)], entrypoint_group=None)
    assert len(loaded["paths"]) == 1

    validator = factory.create_validator("validation.custom_path")
    result = validator.validate(ValidationContext(tenant_id="tenant-a", source_rows=[]))
    assert result.success is True
