from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ValidationType(StrEnum):
    RECORD_COUNT = "record_count"
    COLUMN_COUNT = "column_count"
    METADATA_VALIDATION = "metadata_validation"
    DUPLICATE_DETECTION = "duplicate_detection"
    NULL_ANALYSIS = "null_analysis"
    EMPTY_STRING_DETECTION = "empty_string_detection"
    DATA_COMPARISON = "data_comparison"
    COLUMN_ORDER = "column_order"
    PRECISION = "precision"
    SCALE = "scale"
    LENGTH = "length"
    DISTINCT_COUNT = "distinct_count"
    DATE_RANGE = "date_range"
    CASE_SENSITIVITY = "case_sensitivity"
    LEADING_ZEROS = "leading_zeros"
    SPECIAL_CHARACTERS = "special_characters"
    ROW_CHECKSUM = "row_checksum"
    SYMMETRIC_DIFFERENCE = "symmetric_difference"
    GREAT_EXPECTATIONS = "great_expectations"
    ISOLATION_FOREST = "isolation_forest"
    CUSTOM_SQL = "custom_sql"
    CUSTOM_PYTHON = "custom_python"
    CUSTOM_SPARK = "custom_spark"


@dataclass(frozen=True)
class ValidatorSpec:
    key: str
    display_name: str
    validation_type: ValidationType
    description: str


@dataclass
class ValidationContext:
    tenant_id: str
    source_rows: list[dict[str, Any]]
    target_rows: list[dict[str, Any]] = field(default_factory=list)
    source_schema: dict[str, str] = field(default_factory=dict)
    target_schema: dict[str, str] = field(default_factory=dict)
    source_column_order: list[str] = field(default_factory=list)
    target_column_order: list[str] = field(default_factory=list)
    primary_keys: list[str] = field(default_factory=list)
    options: dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    success: bool
    score: float
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
