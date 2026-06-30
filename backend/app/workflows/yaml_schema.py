import re
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.utils.yaml_loader import load_yaml

SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


class DatasetConfig(BaseModel):
    connector_key: str | None = None
    object_name: str | None = None
    inline_rows: list[dict[str, Any]] = Field(default_factory=list)
    schema: dict[str, str] = Field(default_factory=dict)
    column_order: list[str] = Field(default_factory=list)
    file_size_bytes: int | None = None
    row_count: int | None = None


class FilterConfig(BaseModel):
    column: str
    operator: Literal["eq", "neq", "gt", "lt", "gte", "lte", "in", "contains"]
    value: Any


class TransformationConfig(BaseModel):
    type: Literal["rename_columns", "drop_columns", "add_constant", "select_columns"]
    mapping: dict[str, str] = Field(default_factory=dict)
    columns: list[str] = Field(default_factory=list)
    column: str | None = None
    value: Any = None


class SqlQueriesConfig(BaseModel):
    source_query: str | None = None
    target_query: str | None = None
    compare_query: str | None = None


class SqlObjectConfig(BaseModel):
    name: str
    query: str
    scope: Literal["source", "target", "both"] = "both"


class StoredProcedureConfig(BaseModel):
    name: str
    args: list[Any] = Field(default_factory=list)
    call_sql: str | None = None
    scope: Literal["source", "target", "both"] = "both"


class SqlTransformationConfig(BaseModel):
    source_sql: str | None = None
    target_sql: str | None = None
    views: list[SqlObjectConfig] = Field(default_factory=list)
    temporary_tables: list[SqlObjectConfig] = Field(default_factory=list)
    ctes: list[SqlObjectConfig] = Field(default_factory=list)
    stored_procedures: list[StoredProcedureConfig] = Field(default_factory=list)
    parameters: dict[str, Any] = Field(default_factory=dict)
    parameterized_queries: dict[str, str] = Field(default_factory=dict)


class SamplingConfig(BaseModel):
    enabled: bool = False
    method: Literal["head", "random"] = "head"
    size: int = 100


class SchedulingConfig(BaseModel):
    mode: Literal["immediate", "cron", "once", "one_time", "recurring"] = "immediate"
    cron: str | None = None
    run_at: str | None = None
    interval_seconds: int | None = None
    max_retries: int = 0
    priority: int = 100
    queue: str = "default"
    concurrency_key: str | None = None
    notification_channel: str = "system"


class OutputLocationConfig(BaseModel):
    provider: Literal["local", "s3", "azure_blob", "gcs"] = "local"
    path: str = "./results"
    format: Literal["json", "csv", "parquet", "html", "excel"] = "json"


class WorkflowExecutionProfile(BaseModel):
    file_size_bytes: int | None = None
    row_count: int | None = None
    available_memory_mb: int | None = None
    cluster_available: bool = False
    user_preference: Literal["pandas", "pyspark", "polars", "duckdb"] | None = None
    allow_fallback: bool = True


class GreatExpectationsConfig(BaseModel):
    enabled: bool = False
    suite_id: str = "default_suite"
    auto_generate: bool = True
    requested_version: str | None = None
    editable_expectations: list[dict[str, Any]] = Field(default_factory=list)


class AnomalyDetectionConfig(BaseModel):
    enabled: bool = False
    model: Literal[
        "isolation_forest",
        "one_class_svm",
        "autoencoder",
        "prophet",
        "seasonal_detection",
    ] = "isolation_forest"
    feature_columns: list[str] = Field(default_factory=list)
    options: dict[str, Any] = Field(default_factory=dict)


class ResultStorageConfig(BaseModel):
    formats: list[Literal["database", "csv", "json", "parquet", "html", "excel"]] = Field(
        default_factory=lambda: ["database", "json", "html"]
    )
    allow_download: bool = True
    retention_days: int = 30
    archive_enabled: bool = True
    archive_path: str | None = None


class ReportingConfig(BaseModel):
    enabled: bool = True
    formats: list[Literal["html", "pdf", "excel", "csv", "json"]] = Field(
        default_factory=lambda: ["html", "json"]
    )
    report_types: list[Literal["executive_summary", "detailed_report", "comparison_report", "trend_report"]] = Field(
        default_factory=lambda: [
            "executive_summary",
            "detailed_report",
            "comparison_report",
            "trend_report",
        ]
    )
    email_recipients: list[str] = Field(default_factory=list)


class WorkflowConfig(BaseModel):
    workflow_id: str = Field(min_length=2)
    version: str = "1.0.0"
    source: DatasetConfig
    target: DatasetConfig
    primary_keys: list[str] = Field(default_factory=list)
    join_keys: list[str] = Field(default_factory=list)
    filters: list[FilterConfig] = Field(default_factory=list)
    transformations: list[TransformationConfig] = Field(default_factory=list)
    sql_queries: SqlQueriesConfig = Field(default_factory=SqlQueriesConfig)
    sql_transformations: SqlTransformationConfig = Field(default_factory=SqlTransformationConfig)
    spark_sql: str | None = None
    python_transformations: list[str] = Field(default_factory=list)
    great_expectations: GreatExpectationsConfig = Field(default_factory=GreatExpectationsConfig)
    anomaly_detection: AnomalyDetectionConfig = Field(default_factory=AnomalyDetectionConfig)
    validation_selection: list[str] = Field(default_factory=list)
    sampling: SamplingConfig = Field(default_factory=SamplingConfig)
    scheduling: SchedulingConfig = Field(default_factory=SchedulingConfig)
    output_location: OutputLocationConfig = Field(default_factory=OutputLocationConfig)
    result_storage: ResultStorageConfig = Field(default_factory=ResultStorageConfig)
    reporting: ReportingConfig = Field(default_factory=ReportingConfig)
    execution_profile: WorkflowExecutionProfile = Field(default_factory=WorkflowExecutionProfile)

    @field_validator("version")
    @classmethod
    def validate_semver(cls, value: str) -> str:
        if not SEMVER_PATTERN.match(value):
            raise ValueError("version must follow semantic version format MAJOR.MINOR.PATCH")
        return value

    @model_validator(mode="after")
    def validate_schema_rules(self) -> "WorkflowConfig":
        if self.scheduling.mode == "cron" and not self.scheduling.cron:
            raise ValueError("scheduling.cron is required when scheduling.mode is cron")
        if self.scheduling.mode in ("once", "one_time") and not self.scheduling.run_at:
            raise ValueError("scheduling.run_at is required when scheduling.mode is once")
        if self.scheduling.mode == "recurring" and (self.scheduling.interval_seconds is None or self.scheduling.interval_seconds <= 0):
            raise ValueError("scheduling.interval_seconds must be positive when scheduling.mode is recurring")
        if self.scheduling.max_retries < 0:
            raise ValueError("scheduling.max_retries must be non-negative")
        if not 1 <= self.scheduling.priority <= 1000:
            raise ValueError("scheduling.priority must be between 1 and 1000")
        if not self.scheduling.queue.strip():
            raise ValueError("scheduling.queue must not be empty")
        if self.sampling.enabled and self.sampling.size <= 0:
            raise ValueError("sampling.size must be positive when sampling is enabled")
        if self.result_storage.retention_days < 0:
            raise ValueError("result_storage.retention_days must be non-negative")
        return self


class YamlWorkflowLoader:
    @staticmethod
    def from_dict(payload: dict[str, Any]) -> WorkflowConfig:
        return WorkflowConfig.model_validate(payload)

    @staticmethod
    def from_file(path: str | Path) -> WorkflowConfig:
        payload = load_yaml(path)
        return WorkflowConfig.model_validate(payload)
