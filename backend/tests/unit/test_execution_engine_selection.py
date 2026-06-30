from app.execution.base import BaseExecutionEngine
from app.execution.errors import EngineExecutionError
from app.execution.orchestrator import ExecutionOrchestrator
from app.execution.sdk import EngineType, ExecutionOperation, ExecutionPlan, ExecutionProfile, ExecutionResult
from app.execution.selector import ExecutionEngineSelector


class FakeEngine(BaseExecutionEngine):
    def __init__(self, engine_type: EngineType, available: bool, should_fail: bool = False) -> None:
        self.engine_type = engine_type
        self._available = available
        self._should_fail = should_fail

    def is_available(self) -> bool:
        return self._available

    def execute(self, plan: ExecutionPlan) -> ExecutionResult:
        if self._should_fail:
            raise EngineExecutionError(f"{self.engine_type.value} failed")
        if plan.operation == ExecutionOperation.COUNT:
            return ExecutionResult(engine=self.engine_type, success=True, data=len(plan.rows))
        return ExecutionResult(engine=self.engine_type, success=True, data=plan.rows)


def _fake_engines() -> dict[EngineType, BaseExecutionEngine]:
    return {
        EngineType.PANDAS: FakeEngine(EngineType.PANDAS, available=True),
        EngineType.PYSPARK: FakeEngine(EngineType.PYSPARK, available=True),
        EngineType.POLARS: FakeEngine(EngineType.POLARS, available=True),
        EngineType.DUCKDB: FakeEngine(EngineType.DUCKDB, available=True),
    }


def test_selector_respects_user_preference() -> None:
    selector = ExecutionEngineSelector(_fake_engines())
    profile = ExecutionProfile(user_preference=EngineType.DUCKDB)

    order = selector.choose(profile=profile, operation=ExecutionOperation.COUNT)
    assert order[0] == EngineType.DUCKDB


def test_selector_prefers_spark_for_large_cluster_jobs() -> None:
    selector = ExecutionEngineSelector(_fake_engines())
    profile = ExecutionProfile(row_count=2_000_000, file_size_bytes=2_000_000_000, cluster_available=True)

    order = selector.choose(profile=profile, operation=ExecutionOperation.COUNT)
    assert order[0] == EngineType.PYSPARK


def test_selector_prefers_duckdb_for_sql_workloads() -> None:
    selector = ExecutionEngineSelector(_fake_engines())
    profile = ExecutionProfile()

    order = selector.choose(profile=profile, operation=ExecutionOperation.SQL)
    assert order[0] == EngineType.DUCKDB


def test_orchestrator_fallback_to_next_engine() -> None:
    engines = _fake_engines()
    engines[EngineType.PANDAS] = FakeEngine(EngineType.PANDAS, available=True, should_fail=True)

    orchestrator = ExecutionOrchestrator(engines=engines)
    plan = ExecutionPlan(operation=ExecutionOperation.COUNT, rows=[{"id": 1}, {"id": 2}])
    profile = ExecutionProfile(user_preference=EngineType.PANDAS, allow_fallback=True)

    result = orchestrator.execute(plan=plan, profile=profile)
    assert result.success is True
    assert result.engine != EngineType.PANDAS
    assert result.data == 2
    assert len(result.details.get("fallback_failures", [])) == 1


def test_orchestrator_no_fallback_when_disabled() -> None:
    engines = _fake_engines()
    engines[EngineType.PANDAS] = FakeEngine(EngineType.PANDAS, available=True, should_fail=True)

    orchestrator = ExecutionOrchestrator(engines=engines)
    plan = ExecutionPlan(operation=ExecutionOperation.COUNT, rows=[{"id": 1}])
    profile = ExecutionProfile(user_preference=EngineType.PANDAS, allow_fallback=False)

    result = orchestrator.execute(plan=plan, profile=profile)
    assert result.success is False
    assert result.engine == EngineType.PANDAS
    assert "failed" in (result.error or "")
