import asyncio
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from app.connectors.factory import ConnectorFactory


class ConnectorOperation(StrEnum):
    TEST_CONNECTION = "test_connection"
    DISCOVER_METADATA = "discover_metadata"
    DISCOVER_SCHEMA = "discover_schema"
    DISCOVER_PRIMARY_KEYS = "discover_primary_keys"
    SAMPLE_DATA = "sample_data"


@dataclass
class ConnectorTask:
    task_id: str
    connector_key: str
    operation: ConnectorOperation
    runtime_config: dict[str, Any] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    retries: int = 0


@dataclass
class ConnectorPipelineTemplate:
    template_id: str
    tasks: list[ConnectorTask]


@dataclass
class TaskExecutionResult:
    task_id: str
    success: bool
    attempts: int
    output: Any = None
    error: str | None = None


class ConnectorPipelineRunner:
    def __init__(self, factory: ConnectorFactory) -> None:
        self.factory = factory

    async def run(
        self,
        tasks: list[ConnectorTask],
        max_parallelism: int = 4,
    ) -> dict[str, TaskExecutionResult]:
        task_map = {task.task_id: task for task in tasks}
        pending = set(task_map.keys())
        completed: dict[str, TaskExecutionResult] = {}
        semaphore = asyncio.Semaphore(max(1, max_parallelism))

        while pending:
            ready = [
                task_map[task_id]
                for task_id in sorted(pending)
                if all(dep in completed and completed[dep].success for dep in task_map[task_id].depends_on)
            ]
            if not ready:
                blocked = ", ".join(sorted(pending))
                raise ValueError(f"Unresolvable task dependencies in pipeline: {blocked}")

            batch = [task for task in ready if task.task_id in pending]
            results = await asyncio.gather(
                *[self._run_single(task, semaphore) for task in batch],
            )
            for result in results:
                completed[result.task_id] = result
                pending.remove(result.task_id)

        return completed

    async def run_template(
        self,
        template: ConnectorPipelineTemplate,
        max_parallelism: int = 4,
    ) -> dict[str, TaskExecutionResult]:
        return await self.run(template.tasks, max_parallelism=max_parallelism)

    async def _run_single(self, task: ConnectorTask, semaphore: asyncio.Semaphore) -> TaskExecutionResult:
        async with semaphore:
            attempts = 0
            last_error: str | None = None
            while attempts <= task.retries:
                attempts += 1
                try:
                    output = await asyncio.to_thread(self._invoke, task)
                    if hasattr(output, "success") and getattr(output, "success") is False:
                        raise RuntimeError(str(getattr(output, "message", "connector operation failed")))
                    return TaskExecutionResult(task_id=task.task_id, success=True, attempts=attempts, output=output)
                except Exception as exc:  # pragma: no cover
                    last_error = str(exc)
            return TaskExecutionResult(
                task_id=task.task_id,
                success=False,
                attempts=attempts,
                error=last_error,
            )

    def _invoke(self, task: ConnectorTask) -> Any:
        connector = self.factory.create_connector(task.connector_key, runtime_config=task.runtime_config)
        operation = task.operation.value
        if operation == ConnectorOperation.TEST_CONNECTION.value:
            return connector.test_connection(context=task.params["context"])
        if operation == ConnectorOperation.DISCOVER_METADATA.value:
            return connector.discover_metadata(context=task.params["context"])
        if operation == ConnectorOperation.DISCOVER_SCHEMA.value:
            return connector.discover_schema(
                context=task.params["context"],
                object_name=task.params.get("object_name"),
            )
        if operation == ConnectorOperation.DISCOVER_PRIMARY_KEYS.value:
            return connector.discover_primary_keys(
                context=task.params["context"],
                object_name=task.params.get("object_name"),
            )
        if operation == ConnectorOperation.SAMPLE_DATA.value:
            return connector.sample_data(
                context=task.params["context"],
                object_name=task.params.get("object_name"),
                limit=int(task.params.get("limit", 10)),
            )
        raise ValueError(f"Unsupported connector operation: {operation}")
