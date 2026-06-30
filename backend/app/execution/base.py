from abc import ABC, abstractmethod

from app.execution.sdk import EngineType, ExecutionPlan, ExecutionResult


class BaseExecutionEngine(ABC):
    engine_type: EngineType

    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def execute(self, plan: ExecutionPlan) -> ExecutionResult:
        raise NotImplementedError
