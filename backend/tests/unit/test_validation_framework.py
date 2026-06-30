import pytest

from app.validators.base import BaseValidator
from app.validators.factory import ValidatorFactory
from app.validators.pipeline import ValidationPipelineRunner, ValidationTask
from app.validators.sdk import ValidationContext


def _sample_context() -> ValidationContext:
    return ValidationContext(
        tenant_id="tenant-a",
        source_rows=[
            {"id": 1, "name": "Alice", "amount": "10.50", "created_at": "2026-06-01"},
            {"id": 2, "name": "Bob", "amount": "20.00", "created_at": "2026-06-02"},
        ],
        target_rows=[
            {"id": 1, "name": "Alice", "amount": "10.50", "created_at": "2026-06-01"},
            {"id": 2, "name": "Bob", "amount": "20.00", "created_at": "2026-06-02"},
        ],
        source_schema={"id": "int", "name": "string", "amount": "decimal", "created_at": "date"},
        target_schema={"id": "int", "name": "string", "amount": "decimal", "created_at": "date"},
        source_column_order=["id", "name", "amount", "created_at"],
        target_column_order=["id", "name", "amount", "created_at"],
        primary_keys=["id"],
        options={},
    )


def test_validator_catalog_and_factory() -> None:
    factory = ValidatorFactory.with_defaults()
    specs = factory.registry.list_specs()
    assert len(specs) == 23

    validator = factory.create_validator("validation.record_count")
    assert isinstance(validator, BaseValidator)


def test_builtin_validators_success_path() -> None:
    factory = ValidatorFactory.with_defaults()
    context = _sample_context()

    keys = [
        "validation.record_count",
        "validation.column_count",
        "validation.metadata",
        "validation.data_comparison",
        "validation.column_order",
        "validation.precision",
        "validation.scale",
        "validation.length",
        "validation.distinct_count",
        "validation.date_range",
        "validation.row_checksum",
        "validation.symmetric_difference",
    ]

    for key in keys:
        result = factory.create_validator(key).validate(context)
        assert result.success is True


def test_isolation_forest_validator_with_custom_runner() -> None:
    factory = ValidatorFactory.with_defaults()
    context = _sample_context()
    context.options["anomaly_detection_runner"] = lambda _ctx: {
        "success": True,
        "score": 0.95,
        "model": "isolation_forest",
        "anomaly_count": 0,
        "total_rows": len(_ctx.source_rows),
        "visualizations": {
            "scatter": {"points": [{"x": 1, "y": 1, "anomaly": False}]},
            "score_histogram": [{"bucket": "0-1", "count": len(_ctx.source_rows)}],
        },
        "warnings": [],
    }

    result = factory.create_validator("validation.isolation_forest").validate(context)
    assert result.success is True
    assert result.details["model"] == "isolation_forest"
    assert "scatter" in result.details["visualizations"]


@pytest.mark.asyncio
async def test_validation_pipeline_parallel_dependency_execution() -> None:
    factory = ValidatorFactory.with_defaults()
    runner = ValidationPipelineRunner(factory)
    context = _sample_context()

    tasks = [
        ValidationTask(task_id="a", validator_key="validation.record_count", context=context),
        ValidationTask(
            task_id="b",
            validator_key="validation.custom_python",
            context=context,
            runtime_config={"custom_python_runner": lambda _context: False},
            depends_on=["a"],
            retries=2,
        ),
    ]

    results = await runner.run(tasks, max_parallelism=2)
    assert results["a"].success is True
    assert results["b"].success is False
    assert results["b"].attempts == 3
