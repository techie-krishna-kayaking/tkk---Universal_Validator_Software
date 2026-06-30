# Validator Plugin SDK

## Plugin Contract
A validator plugin must:
1. Inherit from BaseValidator.
2. Implement validate(context) and return ValidationResult.
3. Expose register_validators(registry) in the module.
4. Register at least one ValidatorSpec.

## Discovery Modes
- Python packages
- Python files (path-based)
- Python entry points group: tkk_uv.validators

## Registration Example
A register_validators function should register:
- spec: ValidatorSpec
- builder: callable(spec, config) -> BaseValidator
- default_config: optional defaults

## Runtime Overrides
Use ValidatorFactory.create_validator(key, runtime_config) for per-run configuration overrides.
