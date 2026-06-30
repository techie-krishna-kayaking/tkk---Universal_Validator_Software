import random
from typing import Any

from app.anomaly.service import AnomalyDetectionService
from app.execution.errors import EngineExecutionError, EngineSelectionError
from app.execution.sdk import EngineType, ExecutionOperation, ExecutionPlan, ExecutionProfile, ExecutionResult
from app.services.expectation_service import ExpectationService
from app.services.execution_service import ExecutionService
from app.services.profiling_service import ProfilingService
from app.services.report_service import ReportService
from app.services.result_storage_service import ResultStorageService
from app.services.validation_service import ValidationService
from app.validators.sdk import ValidationContext
from app.workflows.yaml_schema import FilterConfig, TransformationConfig, WorkflowConfig


class YamlWorkflowExecutor:
    def __init__(
        self,
        execution_service: ExecutionService | None = None,
        validation_service: ValidationService | None = None,
        profiling_service: ProfilingService | None = None,
        expectation_service: ExpectationService | None = None,
        anomaly_service: AnomalyDetectionService | None = None,
        result_storage_service: ResultStorageService | None = None,
        report_service: ReportService | None = None,
    ) -> None:
        self.execution_service = execution_service or ExecutionService()
        self.validation_service = validation_service or ValidationService()
        self.profiling_service = profiling_service or ProfilingService()
        self.expectation_service = expectation_service or ExpectationService()
        self.anomaly_service = anomaly_service or AnomalyDetectionService()
        self.result_storage_service = result_storage_service or ResultStorageService()
        self.report_service = report_service or ReportService()

    def execute(self, config: WorkflowConfig) -> dict[str, Any]:
        source_rows = list(config.source.inline_rows)
        target_rows = list(config.target.inline_rows)

        source_rows = self._apply_filters(source_rows, config.filters)
        target_rows = self._apply_filters(target_rows, config.filters)

        source_rows = self._apply_transformations(source_rows, config.transformations)
        target_rows = self._apply_transformations(target_rows, config.transformations)

        source_rows = self._apply_python_transformations(source_rows, config.python_transformations)
        target_rows = self._apply_python_transformations(target_rows, config.python_transformations)

        source_rows = self._apply_sampling(source_rows, config)
        target_rows = self._apply_sampling(target_rows, config)

        execution_profile = self._build_execution_profile(config)
        source_execution = self._execute_plan(
            plan=self._build_execution_plan(rows=source_rows, scope="source", config=config),
            profile=execution_profile,
        )
        target_execution = self._execute_plan(
            plan=self._build_execution_plan(rows=target_rows, scope="target", config=config),
            profile=execution_profile,
        )

        executed_source = source_execution.data if isinstance(source_execution.data, list) else source_rows
        executed_target = target_execution.data if isinstance(target_execution.data, list) else target_rows

        profile_output_dir = config.output_location.path
        profiling_results = self.profiling_service.profile_pair(
            workflow_id=config.workflow_id,
            source_rows=executed_source,
            target_rows=executed_target,
            output_dir=profile_output_dir,
        )

        validation_outcomes: dict[str, Any] = {}
        expectation_cfg = config.great_expectations
        anomaly_cfg = config.anomaly_detection

        def _ge_runner(ctx: ValidationContext) -> dict[str, Any]:
            return self.expectation_service.run_suite(
                suite_id=expectation_cfg.suite_id,
                rows=ctx.source_rows,
                expectations=expectation_cfg.editable_expectations or None,
                auto_generate=expectation_cfg.auto_generate,
                primary_keys=config.primary_keys,
            )

        if expectation_cfg.enabled and expectation_cfg.requested_version:
            latest_suite = self.expectation_service.repository.latest_suite(expectation_cfg.suite_id)
            if latest_suite is None or latest_suite.version != expectation_cfg.requested_version:
                generated = expectation_cfg.editable_expectations or self.expectation_service.engine.auto_generate(
                    rows=executed_source,
                    primary_keys=config.primary_keys,
                )
                self.expectation_service.edit_suite(
                    suite_id=expectation_cfg.suite_id,
                    expectations=generated,
                    requested_version=expectation_cfg.requested_version,
                )

        def _anomaly_runner(ctx: ValidationContext) -> dict[str, Any]:
            features = anomaly_cfg.feature_columns or [
                column
                for column in self._columns_from_rows(ctx.source_rows)
                if any(self._to_float(row.get(column)) is not None for row in ctx.source_rows)
            ]
            result = self.anomaly_service.detect(
                rows=ctx.source_rows,
                feature_columns=features,
                model=anomaly_cfg.model,
                config=anomaly_cfg.options,
            )
            score = max(0.0, 1.0 - (result.anomaly_count / max(1, result.total_rows)))
            return {
                "success": result.success,
                "model": result.model,
                "anomaly_count": result.anomaly_count,
                "total_rows": result.total_rows,
                "anomaly_indices": result.anomaly_indices,
                "anomaly_scores": result.anomaly_scores,
                "visualizations": result.visualizations,
                "warnings": result.warnings,
                "score": score,
            }

        for validator_key in config.validation_selection:
            try:
                validator = self.validation_service.create_validator(validator_key)
                options = {
                    "join_keys": config.join_keys,
                    "great_expectations_suite_id": expectation_cfg.suite_id,
                    "great_expectations_enabled": expectation_cfg.enabled,
                    "anomaly_detection_enabled": anomaly_cfg.enabled,
                    "anomaly_model": anomaly_cfg.model,
                    "anomaly_features": anomaly_cfg.feature_columns,
                    "anomaly_config": anomaly_cfg.options,
                }
                if expectation_cfg.enabled:
                    options["great_expectations_runner"] = _ge_runner
                if anomaly_cfg.enabled:
                    options["anomaly_detection_runner"] = _anomaly_runner

                result = validator.validate(
                    ValidationContext(
                        tenant_id="yaml-workflow",
                        source_rows=executed_source,
                        target_rows=executed_target,
                        source_schema=config.source.schema,
                        target_schema=config.target.schema,
                        source_column_order=config.source.column_order,
                        target_column_order=config.target.column_order,
                        primary_keys=config.primary_keys,
                        options=options,
                    )
                )
                validation_outcomes[validator_key] = {
                    "success": result.success,
                    "score": result.score,
                    "message": result.message,
                    "details": result.details,
                    "warnings": result.warnings,
                    "errors": result.errors,
                }
            except Exception as exc:  # pragma: no cover
                validation_outcomes[validator_key] = {
                    "success": False,
                    "score": 0.0,
                    "message": "validation_error",
                    "details": {},
                    "warnings": [],
                    "errors": [str(exc)],
                }

        overall_success = all(item["success"] for item in validation_outcomes.values()) if validation_outcomes else True

        anomaly_visualizations = {
            key: value.get("details", {}).get("visualizations")
            for key, value in validation_outcomes.items()
            if key in ("validation.isolation_forest",)
            and isinstance(value.get("details"), dict)
            and value.get("details", {}).get("visualizations")
        }

        result_payload = {
            "workflow_id": config.workflow_id,
            "version": config.version,
            "scheduling": config.scheduling.model_dump(),
            "output_location": config.output_location.model_dump(),
            "execution": {
                "source_engine": source_execution.engine.value,
                "target_engine": target_execution.engine.value,
                "source_success": source_execution.success,
                "target_success": target_execution.success,
            },
            "profiling": profiling_results,
            "anomaly_visualizations": anomaly_visualizations,
            "validation_results": validation_outcomes,
            "success": overall_success,
        }

        storage_cfg = config.result_storage
        storage_result = self.result_storage_service.store_result(
            workflow_id=config.workflow_id,
            payload=result_payload,
            output_dir=config.output_location.path,
            formats=list(storage_cfg.formats),
            retention_days=storage_cfg.retention_days,
            archive_enabled=storage_cfg.archive_enabled,
            archive_dir=storage_cfg.archive_path,
        )
        storage_result["allow_download"] = storage_cfg.allow_download
        result_payload["result_storage"] = storage_result

        reporting_cfg = config.reporting
        if reporting_cfg.enabled:
            history = self.result_storage_service.repository.list_by_workflow(config.workflow_id)
            reports = self.report_service.generate_reports(
                workflow_id=config.workflow_id,
                result_id=storage_result["result_id"],
                result_payload=result_payload,
                output_dir=config.output_location.path,
                formats=list(reporting_cfg.formats),
                report_types=list(reporting_cfg.report_types),
                history=history,
                email_recipients=list(reporting_cfg.email_recipients),
            )
            result_payload["reports"] = reports

        return result_payload

    @staticmethod
    def _columns_from_rows(rows: list[dict[str, Any]]) -> list[str]:
        ordered: list[str] = []
        seen: set[str] = set()
        for row in rows:
            for key in row.keys():
                if key not in seen:
                    seen.add(key)
                    ordered.append(key)
        return ordered

    @staticmethod
    def _to_float(value: Any) -> float | None:
        if value is None or isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return None
            try:
                return float(text)
            except ValueError:
                return None
        return None

    def _execute_plan(self, plan: ExecutionPlan, profile: ExecutionProfile):
        try:
            return self.execution_service.execute(plan=plan, profile=profile)
        except (EngineSelectionError, EngineExecutionError):
            if not profile.allow_fallback:
                raise
            return self._identity_fallback(plan)

    @staticmethod
    def _identity_fallback(plan: ExecutionPlan):
        return ExecutionResult(
            engine=EngineType.PANDAS,
            success=True,
            data=plan.rows,
            details={"fallback": "identity"},
        )

    def _build_execution_plan(self, rows: list[dict], scope: str, config: WorkflowConfig) -> ExecutionPlan:
        query = self._resolve_sql_query(scope=scope, config=config)
        pre_sql = self._build_pre_sql(scope=scope, config=config)
        parameters = dict(config.sql_transformations.parameters)

        if query:
            return ExecutionPlan(
                operation=ExecutionOperation.SQL,
                rows=rows,
                sql_query=query,
                pre_sql=pre_sql,
                parameters=parameters,
            )
        return ExecutionPlan(operation=ExecutionOperation.IDENTITY, rows=rows)

    def _resolve_sql_query(self, scope: str, config: WorkflowConfig) -> str | None:
        sql_cfg = config.sql_transformations
        query = sql_cfg.source_sql if scope == "source" else sql_cfg.target_sql

        if query and query.startswith("@"):
            query = sql_cfg.parameterized_queries.get(query[1:])

        if not query:
            query = config.spark_sql

        if not query:
            query = config.sql_queries.source_query if scope == "source" else config.sql_queries.target_query

        scoped_ctes = [cte for cte in sql_cfg.ctes if cte.scope in (scope, "both")]
        if query and scoped_ctes and not query.strip().lower().startswith("with "):
            cte_sql = ", ".join(f"{cte.name} AS ({cte.query})" for cte in scoped_ctes)
            query = f"WITH {cte_sql} {query}"

        return query

    def _build_pre_sql(self, scope: str, config: WorkflowConfig) -> list[str]:
        sql_cfg = config.sql_transformations
        statements: list[str] = []

        for view in sql_cfg.views:
            if view.scope in (scope, "both"):
                statements.append(f"CREATE OR REPLACE VIEW {view.name} AS {view.query}")

        for temp_table in sql_cfg.temporary_tables:
            if temp_table.scope in (scope, "both"):
                statements.append(f"CREATE TEMPORARY TABLE {temp_table.name} AS {temp_table.query}")

        for procedure in sql_cfg.stored_procedures:
            if procedure.scope in (scope, "both"):
                if procedure.call_sql:
                    statements.append(procedure.call_sql)
                else:
                    args = ", ".join(self._sql_literal(arg) for arg in procedure.args)
                    statements.append(f"CALL {procedure.name}({args})")

        return statements

    def _sql_literal(self, value: Any) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"

    def _build_execution_profile(self, config: WorkflowConfig) -> ExecutionProfile:
        preference = (
            EngineType(config.execution_profile.user_preference)
            if config.execution_profile.user_preference
            else None
        )
        return ExecutionProfile(
            file_size_bytes=config.execution_profile.file_size_bytes,
            row_count=config.execution_profile.row_count,
            available_memory_mb=config.execution_profile.available_memory_mb,
            cluster_available=config.execution_profile.cluster_available,
            user_preference=preference,
            allow_fallback=config.execution_profile.allow_fallback,
        )

    def _apply_filters(self, rows: list[dict], filters: list[FilterConfig]) -> list[dict]:
        output = rows
        for filter_item in filters:
            output = [row for row in output if self._matches_filter(row, filter_item)]
        return output

    def _matches_filter(self, row: dict, filter_item: FilterConfig) -> bool:
        value = row.get(filter_item.column)
        expected = filter_item.value
        operator = filter_item.operator

        if operator == "eq":
            return value == expected
        if operator == "neq":
            return value != expected
        if operator == "gt":
            return value is not None and value > expected
        if operator == "lt":
            return value is not None and value < expected
        if operator == "gte":
            return value is not None and value >= expected
        if operator == "lte":
            return value is not None and value <= expected
        if operator == "in":
            return value in expected
        if operator == "contains":
            return isinstance(value, str) and str(expected) in value
        return False

    def _apply_transformations(self, rows: list[dict], transformations: list[TransformationConfig]) -> list[dict]:
        output = rows
        for transformation in transformations:
            if transformation.type == "rename_columns":
                output = [{transformation.mapping.get(k, k): v for k, v in row.items()} for row in output]
            elif transformation.type == "drop_columns":
                drop = set(transformation.columns)
                output = [{k: v for k, v in row.items() if k not in drop} for row in output]
            elif transformation.type == "add_constant" and transformation.column:
                output = [{**row, transformation.column: transformation.value} for row in output]
            elif transformation.type == "select_columns":
                keep = transformation.columns
                output = [{k: row.get(k) for k in keep} for row in output]
        return output

    def _apply_python_transformations(self, rows: list[dict], names: list[str]) -> list[dict]:
        output = rows
        for name in names:
            if name == "trim_strings":
                output = [
                    {
                        key: value.strip() if isinstance(value, str) else value
                        for key, value in row.items()
                    }
                    for row in output
                ]
            elif name == "lowercase_columns":
                output = [{key.lower(): value for key, value in row.items()} for row in output]
            elif name == "uppercase_columns":
                output = [{key.upper(): value for key, value in row.items()} for row in output]
        return output

    def _apply_sampling(self, rows: list[dict], config: WorkflowConfig) -> list[dict]:
        if not config.sampling.enabled:
            return rows
        if config.sampling.method == "head":
            return rows[: config.sampling.size]
        sample_size = min(config.sampling.size, len(rows))
        if sample_size <= 0:
            return []
        return random.sample(rows, sample_size)
