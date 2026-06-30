from app.execution.sdk import EngineType, ExecutionOperation, ExecutionResult
from app.validators.sdk import ValidationContext, ValidationResult
from app.workflows.yaml_executor import YamlWorkflowExecutor
from app.workflows.yaml_schema import WorkflowConfig


class CapturingExecutionService:
    def __init__(self) -> None:
        self.plans = []

    def execute(self, plan, profile):  # noqa: ANN001
        self.plans.append(plan)
        if plan.operation == ExecutionOperation.SQL and plan.parameters.get("status") is not None:
            status = plan.parameters["status"]
            transformed = [row for row in plan.rows if row.get("status") == status]
        else:
            transformed = list(plan.rows)
        return ExecutionResult(engine=EngineType.DUCKDB, success=True, data=transformed)


class StatusOnlyValidator:
    def validate(self, context: ValidationContext) -> ValidationResult:
        ok = all(row.get("status") == "active" for row in context.source_rows)
        return ValidationResult(
            success=ok,
            score=1.0 if ok else 0.0,
            message="status_check",
            details={"source_row_count": len(context.source_rows)},
        )


class FakeValidationService:
    def create_validator(self, key: str, runtime_config=None):  # noqa: ANN001
        return StatusOnlyValidator()


class FakeProfilingService:
    def profile_pair(self, workflow_id, source_rows, target_rows, output_dir):  # noqa: ANN001
        return {
            "source": {"row_count": len(source_rows), "schema": {}},
            "target": {"row_count": len(target_rows), "schema": {}},
            "html_report_path": f"{output_dir}/{workflow_id}_profile_report.html",
        }


def _workflow_config() -> WorkflowConfig:
    return WorkflowConfig.model_validate(
        {
            "workflow_id": "wf-sql-transform",
            "version": "1.0.0",
            "source": {
                "inline_rows": [
                    {"id": 1, "status": "active", "amount": 10},
                    {"id": 2, "status": "inactive", "amount": 20},
                ]
            },
            "target": {
                "inline_rows": [
                    {"id": 1, "status": "active", "amount": 10},
                    {"id": 3, "status": "inactive", "amount": 30},
                ]
            },
            "sql_transformations": {
                "source_sql": "@active_source",
                "target_sql": "select * from dataset where status = :status",
                "views": [
                    {
                        "name": "v_source",
                        "query": "select * from dataset",
                        "scope": "source",
                    }
                ],
                "temporary_tables": [
                    {
                        "name": "tmp_source",
                        "query": "select * from dataset where status = :status",
                        "scope": "source",
                    }
                ],
                "ctes": [
                    {
                        "name": "active_rows",
                        "query": "select * from dataset where status = :status",
                        "scope": "source",
                    }
                ],
                "stored_procedures": [
                    {
                        "name": "prepare_source",
                        "call_sql": "select 1",
                        "scope": "source",
                    }
                ],
                "parameters": {"status": "active"},
                "parameterized_queries": {
                    "active_source": "select * from active_rows"
                },
            },
            "great_expectations": {
                "enabled": False,
                "suite_id": "suite-sql-transform",
                "auto_generate": True,
                "editable_expectations": [],
            },
            "validation_selection": ["validation.custom.status"],
        }
    )


def test_sql_transformations_are_compiled_into_execution_plan() -> None:
    execution = CapturingExecutionService()
    validator = FakeValidationService()
    profiler = FakeProfilingService()
    executor = YamlWorkflowExecutor(
        execution_service=execution,
        validation_service=validator,
        profiling_service=profiler,
    )

    executor.execute(_workflow_config())

    source_plan = execution.plans[0]
    assert source_plan.operation == ExecutionOperation.SQL
    assert source_plan.sql_query.startswith("WITH active_rows AS")
    assert "select * from active_rows" in source_plan.sql_query
    assert source_plan.parameters == {"status": "active"}
    assert "CREATE OR REPLACE VIEW v_source AS select * from dataset" in source_plan.pre_sql
    assert "CREATE TEMPORARY TABLE tmp_source AS select * from dataset where status = :status" in source_plan.pre_sql
    assert "select 1" in source_plan.pre_sql


def test_validation_runs_after_sql_transformation() -> None:
    execution = CapturingExecutionService()
    validator = FakeValidationService()
    profiler = FakeProfilingService()
    executor = YamlWorkflowExecutor(
        execution_service=execution,
        validation_service=validator,
        profiling_service=profiler,
    )

    result = executor.execute(_workflow_config())

    assert result["validation_results"]["validation.custom.status"]["success"] is True
    assert result["success"] is True
