from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class EngineType(StrEnum):
    PANDAS = "pandas"
    PYSPARK = "pyspark"
    POLARS = "polars"
    DUCKDB = "duckdb"


class ExecutionOperation(StrEnum):
    IDENTITY = "identity"
    COUNT = "count"
    SELECT_COLUMNS = "select_columns"
    SQL = "sql"


@dataclass
class ExecutionProfile:
    file_size_bytes: int | None = None
    row_count: int | None = None
    available_memory_mb: int | None = None
    cluster_available: bool = False
    user_preference: EngineType | None = None
    allow_fallback: bool = True


@dataclass
class ExecutionPlan:
    operation: ExecutionOperation
    rows: list[dict[str, Any]] = field(default_factory=list)
    columns: list[str] = field(default_factory=list)
    sql_query: str | None = None
    pre_sql: list[str] = field(default_factory=list)
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    engine: EngineType
    success: bool
    data: Any = None
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
