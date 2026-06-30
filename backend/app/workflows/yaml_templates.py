from app.workflows.yaml_schema import WorkflowConfig


class YamlTemplateService:
    @staticmethod
    def base_template() -> dict:
        return {
            "workflow_id": "workflow-sample",
            "version": "1.0.0",
            "source": {
                "connector_key": "file.csv",
                "object_name": "source_dataset",
                "inline_rows": [],
                "schema": {},
                "column_order": [],
            },
            "target": {
                "connector_key": "file.csv",
                "object_name": "target_dataset",
                "inline_rows": [],
                "schema": {},
                "column_order": [],
            },
            "primary_keys": ["id"],
            "join_keys": ["id"],
            "filters": [],
            "transformations": [],
            "sql_queries": {
                "source_query": None,
                "target_query": None,
                "compare_query": None,
            },
            "sql_transformations": {
                "source_sql": None,
                "target_sql": None,
                "views": [],
                "temporary_tables": [],
                "ctes": [],
                "stored_procedures": [],
                "parameters": {},
                "parameterized_queries": {},
            },
            "spark_sql": None,
            "python_transformations": [],
            "great_expectations": {
                "enabled": False,
                "suite_id": "default_suite",
                "auto_generate": True,
                "requested_version": None,
                "editable_expectations": [],
            },
            "anomaly_detection": {
                "enabled": False,
                "model": "isolation_forest",
                "feature_columns": [],
                "options": {},
            },
            "validation_selection": [
                "validation.record_count",
                "validation.data_comparison",
            ],
            "sampling": {"enabled": False, "method": "head", "size": 100},
            "scheduling": {"mode": "immediate", "cron": None, "run_at": None},
            "output_location": {"provider": "local", "path": "./results", "format": "json"},
            "result_storage": {
                "formats": ["database", "json", "html"],
                "allow_download": True,
                "retention_days": 30,
                "archive_enabled": True,
                "archive_path": None,
            },
            "reporting": {
                "enabled": True,
                "formats": ["html", "pdf", "excel", "csv", "json"],
                "report_types": [
                    "executive_summary",
                    "detailed_report",
                    "comparison_report",
                    "trend_report",
                ],
                "email_recipients": [],
            },
            "execution_profile": {
                "file_size_bytes": None,
                "row_count": None,
                "available_memory_mb": None,
                "cluster_available": False,
                "user_preference": None,
                "allow_fallback": True,
            },
        }

    @classmethod
    def autocomplete(cls, partial: dict, available_validations: list[str] | None = None) -> dict:
        merged = cls.base_template()
        cls._deep_update(merged, partial)
        if available_validations is not None and not merged.get("validation_selection"):
            merged["validation_selection"] = available_validations

        config = WorkflowConfig.model_validate(merged)
        return config.model_dump()

    @staticmethod
    def _deep_update(base: dict, patch: dict) -> None:
        for key, value in patch.items():
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                YamlTemplateService._deep_update(base[key], value)
            else:
                base[key] = value
