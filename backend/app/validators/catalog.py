from app.validators.implementations import BuiltinValidator
from app.validators.registry import ValidatorRegistry
from app.validators.sdk import ValidationType, ValidatorSpec


SUPPORTED_VALIDATOR_SPECS: tuple[ValidatorSpec, ...] = (
    ValidatorSpec("validation.record_count", "Record Count", ValidationType.RECORD_COUNT, "Compares source and target record counts"),
    ValidatorSpec("validation.column_count", "Column Count", ValidationType.COLUMN_COUNT, "Compares source and target column counts"),
    ValidatorSpec("validation.metadata", "Metadata Validation", ValidationType.METADATA_VALIDATION, "Compares schema metadata"),
    ValidatorSpec("validation.duplicate_detection", "Duplicate Detection", ValidationType.DUPLICATE_DETECTION, "Detects duplicate keys"),
    ValidatorSpec("validation.null_analysis", "Null Analysis", ValidationType.NULL_ANALYSIS, "Compares null distributions"),
    ValidatorSpec("validation.empty_string", "Empty String Detection", ValidationType.EMPTY_STRING_DETECTION, "Detects empty string anomalies"),
    ValidatorSpec("validation.data_comparison", "Data Comparison", ValidationType.DATA_COMPARISON, "Compares source and target row values"),
    ValidatorSpec("validation.column_order", "Column Order", ValidationType.COLUMN_ORDER, "Compares source and target column ordering"),
    ValidatorSpec("validation.precision", "Precision", ValidationType.PRECISION, "Compares numeric precision"),
    ValidatorSpec("validation.scale", "Scale", ValidationType.SCALE, "Compares numeric scale"),
    ValidatorSpec("validation.length", "Length", ValidationType.LENGTH, "Compares string length constraints"),
    ValidatorSpec("validation.distinct_count", "Distinct Count", ValidationType.DISTINCT_COUNT, "Compares distinct value counts"),
    ValidatorSpec("validation.date_range", "Date Range", ValidationType.DATE_RANGE, "Compares date min and max ranges"),
    ValidatorSpec("validation.case_sensitivity", "Case Sensitivity", ValidationType.CASE_SENSITIVITY, "Detects case-only value differences"),
    ValidatorSpec("validation.leading_zeros", "Leading Zeros", ValidationType.LEADING_ZEROS, "Detects leading zero mismatches"),
    ValidatorSpec("validation.special_characters", "Special Characters", ValidationType.SPECIAL_CHARACTERS, "Compares special character distributions"),
    ValidatorSpec("validation.row_checksum", "Row Checksum", ValidationType.ROW_CHECKSUM, "Compares row checksums"),
    ValidatorSpec("validation.symmetric_difference", "Symmetric Difference", ValidationType.SYMMETRIC_DIFFERENCE, "Finds source-only and target-only rows"),
    ValidatorSpec("validation.great_expectations", "Great Expectations", ValidationType.GREAT_EXPECTATIONS, "Runs Great Expectations suite integration"),
    ValidatorSpec("validation.isolation_forest", "Isolation Forest", ValidationType.ISOLATION_FOREST, "Runs anomaly detection using Isolation Forest"),
    ValidatorSpec("validation.custom_sql", "Custom SQL Validator", ValidationType.CUSTOM_SQL, "Runs user-defined SQL validation logic"),
    ValidatorSpec("validation.custom_python", "Custom Python Validator", ValidationType.CUSTOM_PYTHON, "Runs user-defined Python validation logic"),
    ValidatorSpec("validation.custom_spark", "Custom Spark Validator", ValidationType.CUSTOM_SPARK, "Runs user-defined Spark validation logic"),
)


def register_catalog_validators(registry: ValidatorRegistry) -> None:
    for spec in SUPPORTED_VALIDATOR_SPECS:
        registry.register(
            spec=spec,
            builder=lambda validator_spec, config: BuiltinValidator(validator_spec, config),
            default_config={},
        )
