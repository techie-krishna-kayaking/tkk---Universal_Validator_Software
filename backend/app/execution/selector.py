from app.execution.base import BaseExecutionEngine
from app.execution.errors import EngineSelectionError
from app.execution.sdk import EngineType, ExecutionOperation, ExecutionProfile


class ExecutionEngineSelector:
    def __init__(self, engines: dict[EngineType, BaseExecutionEngine]) -> None:
        self.engines = engines

    def choose(self, profile: ExecutionProfile, operation: ExecutionOperation) -> list[EngineType]:
        available = [engine_type for engine_type, engine in self.engines.items() if engine.is_available()]
        if not available:
            raise EngineSelectionError("No execution engine is available")

        ranked: list[EngineType] = []

        if profile.user_preference and profile.user_preference in available:
            ranked.append(profile.user_preference)

        row_count = profile.row_count or 0
        file_size = profile.file_size_bytes or 0
        memory_mb = profile.available_memory_mb or 0

        if profile.cluster_available and (row_count >= 1_000_000 or file_size >= 1_000_000_000):
            self._append_if_available(ranked, available, EngineType.PYSPARK)

        if operation == ExecutionOperation.SQL:
            self._append_if_available(ranked, available, EngineType.DUCKDB)

        if memory_mb and memory_mb < 1024:
            self._append_if_available(ranked, available, EngineType.POLARS)
            self._append_if_available(ranked, available, EngineType.DUCKDB)

        if row_count >= 500_000 or file_size >= 500_000_000:
            self._append_if_available(ranked, available, EngineType.POLARS)
            self._append_if_available(ranked, available, EngineType.DUCKDB)
            if profile.cluster_available:
                self._append_if_available(ranked, available, EngineType.PYSPARK)

        self._append_if_available(ranked, available, EngineType.PANDAS)
        self._append_if_available(ranked, available, EngineType.POLARS)
        self._append_if_available(ranked, available, EngineType.DUCKDB)
        self._append_if_available(ranked, available, EngineType.PYSPARK)

        for engine_type in available:
            if engine_type not in ranked:
                ranked.append(engine_type)

        return ranked

    @staticmethod
    def _append_if_available(
        ranked: list[EngineType],
        available: list[EngineType],
        engine_type: EngineType,
    ) -> None:
        if engine_type in available and engine_type not in ranked:
            ranked.append(engine_type)
