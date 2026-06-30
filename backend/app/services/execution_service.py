from app.execution.orchestrator import ExecutionOrchestrator
from app.execution.sdk import ExecutionPlan, ExecutionProfile, ExecutionResult


class ExecutionService:
    def __init__(self, orchestrator: ExecutionOrchestrator | None = None) -> None:
        self.orchestrator = orchestrator or ExecutionOrchestrator()

    def execute(self, plan: ExecutionPlan, profile: ExecutionProfile) -> ExecutionResult:
        return self.orchestrator.execute(plan=plan, profile=profile)
