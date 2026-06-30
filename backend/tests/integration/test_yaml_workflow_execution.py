from app.services.yaml_workflow_service import YamlWorkflowService
from app.workflows.yaml_schema import WorkflowConfig


def test_yaml_workflow_execution_end_to_end(tmp_path) -> None:  # noqa: ANN001
    service = YamlWorkflowService()

    config = WorkflowConfig.model_validate(
        {
            "workflow_id": "wf-exec-1",
            "version": "1.0.0",
            "source": {
                "inline_rows": [
                    {"id": 1, "name": " Alice ", "status": "active", "amount": "10.50"},
                    {"id": 2, "name": " Bob ", "status": "inactive", "amount": "20.00"},
                ],
                "schema": {"id": "int", "name": "string", "status": "string", "amount": "decimal"},
                "column_order": ["id", "name", "status", "amount"],
            },
            "target": {
                "inline_rows": [
                    {"id": 1, "name": "Alice", "status": "active", "amount": "10.50"},
                    {"id": 2, "name": "Bob", "status": "inactive", "amount": "20.00"},
                ],
                "schema": {"id": "int", "name": "string", "status": "string", "amount": "decimal"},
                "column_order": ["id", "name", "status", "amount"],
            },
            "primary_keys": ["id"],
            "join_keys": ["id"],
            "filters": [{"column": "status", "operator": "eq", "value": "active"}],
            "python_transformations": ["trim_strings"],
            "great_expectations": {
                "enabled": True,
                "suite_id": "wf-exec-1-suite",
                "auto_generate": True,
                "editable_expectations": [],
            },
            "anomaly_detection": {
                "enabled": True,
                "model": "one_class_svm",
                "feature_columns": ["id", "amount"],
                "options": {},
            },
            "validation_selection": [
                "validation.record_count",
                "validation.data_comparison",
                "validation.great_expectations",
                "validation.isolation_forest",
            ],
            "sampling": {"enabled": False, "method": "head", "size": 100},
            "scheduling": {"mode": "immediate"},
            "output_location": {"provider": "local", "path": str(tmp_path), "format": "json"},
            "result_storage": {
                "formats": ["database", "csv", "json", "parquet", "html", "excel"],
                "allow_download": True,
                "retention_days": 30,
                "archive_enabled": True,
                "archive_path": str(tmp_path / "archive"),
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
                "email_recipients": ["qa@example.com"],
            },
            "execution_profile": {
                "row_count": 2,
                "file_size_bytes": 100,
                "available_memory_mb": 2048,
                "cluster_available": False,
                "user_preference": "pandas",
                "allow_fallback": True,
            },
        }
    )

    version = service.save_versioned(config)
    result = service.execute(config)

    assert version == "1.0.0"
    assert result["workflow_id"] == "wf-exec-1"
    assert result["execution"]["source_success"] is True
    assert result["execution"]["target_success"] is True
    assert result["profiling"]["source"]["schema"]["id"] == "int"
    assert result["profiling"]["target"]["columns"]["name"]["null_percent"] == 0.0
    assert result["profiling"]["html_report_path"].endswith("wf-exec-1_profile_report.html")
    assert result["validation_results"]["validation.record_count"]["success"] is True
    assert result["validation_results"]["validation.data_comparison"]["success"] is True
    assert result["validation_results"]["validation.great_expectations"]["success"] is True
    assert result["validation_results"]["validation.great_expectations"]["details"]["suite_id"] == "wf-exec-1-suite"
    assert result["validation_results"]["validation.great_expectations"]["details"]["suite_version"] == "1.0.0"
    assert result["validation_results"]["validation.isolation_forest"]["success"] is True
    assert result["validation_results"]["validation.isolation_forest"]["details"]["model"] == "one_class_svm"
    assert "validation.isolation_forest" in result["anomaly_visualizations"]
    assert "scatter" in result["anomaly_visualizations"]["validation.isolation_forest"]
    assert result["result_storage"]["stored_in_database"] is True
    assert "json" in result["result_storage"]["artifacts"]
    assert "csv" in result["result_storage"]["artifacts"]
    assert "html" in result["result_storage"]["artifacts"]
    assert result["result_storage"]["allow_download"] is True
    assert "reports" in result
    assert "html" in result["reports"]["artifacts"]
    assert "json" in result["reports"]["artifacts"]
    assert result["reports"]["email"]["queued"] is True


def test_yaml_workflow_scheduled_job_lifecycle(tmp_path) -> None:  # noqa: ANN001
    service = YamlWorkflowService()

    config = WorkflowConfig.model_validate(
        {
            "workflow_id": "wf-scheduled-1",
            "version": "1.0.0",
            "source": {"inline_rows": [{"id": 1, "name": "Alice"}]},
            "target": {"inline_rows": [{"id": 1, "name": "Alice"}]},
            "primary_keys": ["id"],
            "join_keys": ["id"],
            "validation_selection": ["validation.record_count"],
            "scheduling": {
                "mode": "immediate",
                "max_retries": 1,
                "priority": 5,
                "queue": "default",
                "concurrency_key": "wf-scheduled-1",
                "notification_channel": "email",
            },
            "output_location": {"provider": "local", "path": str(tmp_path), "format": "json"},
            "result_storage": {
                "formats": ["database", "json"],
                "allow_download": True,
                "retention_days": 30,
                "archive_enabled": False,
                "archive_path": str(tmp_path / "archive"),
            },
            "reporting": {"enabled": False, "formats": ["json"], "report_types": ["executive_summary"]},
        }
    )

    queued = service.submit_scheduled_job(config, auto_process=False)
    paused = service.pause_scheduled_job(queued["job_id"])
    resumed = service.resume_scheduled_job(queued["job_id"])
    stats = service.dispatch_scheduled_jobs(queue_name="default")

    jobs = service.list_scheduled_jobs()
    history = service.list_schedule_history(queued["job_id"])
    notifications = service.list_schedule_notifications(queued["job_id"])

    queued_status = [item for item in jobs if item["job_id"] == queued["job_id"]][0]

    assert paused["status"] == "paused"
    assert resumed["status"] == "queued"
    assert stats["completed"] == 1
    assert queued_status["status"] == "succeeded"
    assert len(history) >= 4
    assert notifications[0]["channel"] == "email"

    canceled = service.cancel_scheduled_job(queued["job_id"])
    assert canceled["status"] == "canceled"
