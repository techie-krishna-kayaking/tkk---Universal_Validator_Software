from app.validators.base import BaseValidator
from app.validators.sdk import ValidationResult, ValidationType, ValidatorSpec


class ExampleValidator(BaseValidator):
    def validate(self, context):
        _ = context
        return ValidationResult(success=True, score=1.0, message="example validator executed")


def register_validators(registry):
    registry.register(
        spec=ValidatorSpec(
            key="validation.custom_example",
            display_name="Custom Example Validator",
            validation_type=ValidationType.CUSTOM_PYTHON,
            description="Example custom validator plugin",
        ),
        builder=lambda spec, config: ExampleValidator(spec, config),
        default_config={},
    )
