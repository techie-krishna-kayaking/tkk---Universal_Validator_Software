from app.execution.base import BaseExecutionEngine
from app.execution.engines import (
    DuckDBExecutionEngine,
    PandasExecutionEngine,
    PolarsExecutionEngine,
    PySparkExecutionEngine,
)
from app.execution.errors import EngineExecutionError, EngineUnavailableError
from app.execution.sdk import EngineType, ExecutionPlan, ExecutionProfile, ExecutionResult
from app.execution.selector import ExecutionEngineSelector


class ExecutionOrchestrator:
    def __init__(self, engines: dict[EngineType, BaseExecutionEngine] | None = None) -> None:
        self.engines = engines or {
            EngineType.PANDAS: PandasExecutionEngine(),
            EngineType.PYSPARK: PySparkExecutionEngine(),
            EngineType.POLARS: PolarsExecutionEngine(),
            EngineType.DUCKDB: DuckDBExecutionEngine(),
        }
        self.selector = ExecutionEngineSelector(self.engines)

    def execute(self, plan: ExecutionPlan, profile: ExecutionProfile) -> ExecutionResult:
        candidates = self.selector.choose(profile, plan.operation)
        failures: list[dict[str, str]] = []

        for index, engine_type in enumerate(candidates):
            engine = self.engines[engine_type]
            try:
                result = engine.execute(plan)
                result.details.setdefault("selected_engine", engine_type.value)
                result.details.setdefault("candidate_order", [item.value for item in candidates])
                if failures:
                    result.details["fallback_failures"] = failures
                return result
            except (EngineUnavailableError, EngineExecutionError, Exception) as exc:  # pragma: no cover
                failures.append({"engine": engine_type.value, "error": str(exc)})
                if not profile.allow_fallback or index == len(candidates) - 1:
                    return ExecutionResult(
                        engine=engine_type,
                        success=False,
                        error=str(exc),
                        details={
                            "candidate_order": [item.value for item in candidates],
                            "fallback_failures": failures,
                        },
                    )

        return ExecutionResult(
            engine=candidates[0],
            success=False,
            error="No engine execution attempted",
            details={"candidate_order": [item.value for item in candidates], "fallback_failures": failures},
        )
