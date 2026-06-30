import asyncio
from dataclasses import dataclass, field

from app.validators.factory import ValidatorFactory
from app.validators.sdk import ValidationContext


@dataclass
class ValidationTask:
    task_id: str
    validator_key: str
    context: ValidationContext
    runtime_config: dict = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    retries: int = 0


@dataclass
class ValidationPipelineTemplate:
    template_id: str
    tasks: list[ValidationTask]


@dataclass
class ValidationTaskExecutionResult:
    task_id: str
    success: bool
    attempts: int
    output: object | None = None
    error: str | None = None


class ValidationPipelineRunner:
    def __init__(self, factory: ValidatorFactory) -> None:
        self.factory = factory

    async def run(
        self,
        tasks: list[ValidationTask],
        max_parallelism: int = 4,
    ) -> dict[str, ValidationTaskExecutionResult]:
        task_map = {task.task_id: task for task in tasks}
        pending = set(task_map.keys())
        completed: dict[str, ValidationTaskExecutionResult] = {}
        semaphore = asyncio.Semaphore(max(1, max_parallelism))

        while pending:
            ready = [
                task_map[task_id]
                for task_id in sorted(pending)
                if all(dep in completed and completed[dep].success for dep in task_map[task_id].depends_on)
            ]
            if not ready:
                blocked = ", ".join(sorted(pending))
                raise ValueError(f"Unresolvable task dependencies in validation pipeline: {blocked}")

            batch = [task for task in ready if task.task_id in pending]
            results = await asyncio.gather(*[self._run_single(task, semaphore) for task in batch])
            for result in results:
                completed[result.task_id] = result
                pending.remove(result.task_id)

        return completed

    async def run_template(
        self,
        template: ValidationPipelineTemplate,
        max_parallelism: int = 4,
    ) -> dict[str, ValidationTaskExecutionResult]:
        return await self.run(template.tasks, max_parallelism=max_parallelism)

    async def _run_single(self, task: ValidationTask, semaphore: asyncio.Semaphore) -> ValidationTaskExecutionResult:
        async with semaphore:
            attempts = 0
            last_error: str | None = None
            while attempts <= task.retries:
                attempts += 1
                try:
                    output = await asyncio.to_thread(self._invoke, task)
                    if hasattr(output, "success") and getattr(output, "success") is False:
                        raise RuntimeError(str(getattr(output, "message", "validation failed")))
                    return ValidationTaskExecutionResult(task_id=task.task_id, success=True, attempts=attempts, output=output)
                except Exception as exc:  # pragma: no cover
                    last_error = str(exc)

            return ValidationTaskExecutionResult(
                task_id=task.task_id,
                success=False,
                attempts=attempts,
                error=last_error,
            )

    def _invoke(self, task: ValidationTask):
        validator = self.factory.create_validator(task.validator_key, runtime_config=task.runtime_config)
        return validator.validate(task.context)
