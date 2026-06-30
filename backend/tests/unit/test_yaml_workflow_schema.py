import pytest

from app.workflows.yaml_schema import WorkflowConfig, YamlWorkflowLoader
from app.workflows.yaml_templates import YamlTemplateService


def _minimal_payload() -> dict:
    return {
        "workflow_id": "wf-yaml-1",
        "version": "1.0.0",
        "source": {"inline_rows": [{"id": 1, "name": "Alice"}]},
        "target": {"inline_rows": [{"id": 1, "name": "Alice"}]},
    }


def test_yaml_schema_validation_success() -> None:
    config = YamlWorkflowLoader.from_dict(_minimal_payload())
    assert isinstance(config, WorkflowConfig)
    assert config.workflow_id == "wf-yaml-1"


def test_yaml_schema_validation_semver_failure() -> None:
    payload = _minimal_payload()
    payload["version"] = "1.0"
    with pytest.raises(ValueError):
        YamlWorkflowLoader.from_dict(payload)


def test_yaml_schema_validation_requires_recurring_interval() -> None:
    payload = _minimal_payload()
    payload["scheduling"] = {"mode": "recurring", "interval_seconds": 0}
    with pytest.raises(ValueError):
        YamlWorkflowLoader.from_dict(payload)


def test_yaml_schema_validation_scheduling_orchestration_fields() -> None:
    payload = _minimal_payload()
    payload["scheduling"] = {
        "mode": "one_time",
        "run_at": "2026-07-01T10:00:00Z",
        "max_retries": 2,
        "priority": 20,
        "queue": "critical",
        "concurrency_key": "wf-yaml-1",
        "notification_channel": "email",
    }
    config = YamlWorkflowLoader.from_dict(payload)
    assert config.scheduling.mode == "one_time"
    assert config.scheduling.max_retries == 2
    assert config.scheduling.priority == 20
    assert config.scheduling.queue == "critical"


def test_yaml_template_autocomplete() -> None:
    partial = {
        "workflow_id": "wf-template",
        "source": {"inline_rows": [{"id": 1}]},
        "target": {"inline_rows": [{"id": 1}]},
        "validation_selection": [],
    }
    completed = YamlTemplateService.autocomplete(
        partial,
        available_validations=["validation.record_count", "validation.data_comparison"],
    )
    assert completed["workflow_id"] == "wf-template"
    assert completed["validation_selection"] == ["validation.record_count", "validation.data_comparison"]
    assert completed["output_location"]["path"] == "./results"
