from app.execution.base import BaseExecutionEngine
from app.execution.orchestrator import ExecutionOrchestrator
from app.execution.sdk import EngineType, ExecutionOperation, ExecutionPlan, ExecutionProfile, ExecutionResult
from app.services.execution_service import ExecutionService


class AvailableEngine(BaseExecutionEngine):
    def __init__(self, engine_type: EngineType) -> None:
        self.engine_type = engine_type

    def is_available(self) -> bool:
        return True

    def execute(self, plan: ExecutionPlan) -> ExecutionResult:
        if plan.operation == ExecutionOperation.COUNT:
            return ExecutionResult(engine=self.engine_type, success=True, data=len(plan.rows))
        return ExecutionResult(engine=self.engine_type, success=True, data=plan.rows)


def test_execution_service_end_to_end_with_profile() -> None:
    engines = {
        EngineType.PANDAS: AvailableEngine(EngineType.PANDAS),
        EngineType.PYSPARK: AvailableEngine(EngineType.PYSPARK),
        EngineType.POLARS: AvailableEngine(EngineType.POLARS),
        EngineType.DUCKDB: AvailableEngine(EngineType.DUCKDB),
    }
    service = ExecutionService(orchestrator=ExecutionOrchestrator(engines=engines))

    plan = ExecutionPlan(operation=ExecutionOperation.COUNT, rows=[{"id": 1}, {"id": 2}, {"id": 3}])
    profile = ExecutionProfile(user_preference=EngineType.POLARS)

    result = service.execute(plan=plan, profile=profile)
    assert result.success is True
    assert result.engine == EngineType.POLARS
    assert result.data == 3
