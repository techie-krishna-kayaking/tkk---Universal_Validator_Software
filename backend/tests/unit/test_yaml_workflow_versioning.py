from app.repositories.yaml_workflow_repository import InMemoryYamlWorkflowRepository
from app.workflows.yaml_schema import WorkflowConfig
from app.workflows.yaml_versioning import WorkflowVersionService


def _config(version: str) -> WorkflowConfig:
    return WorkflowConfig.model_validate(
        {
            "workflow_id": "wf-versioned",
            "version": version,
            "source": {"inline_rows": [{"id": 1}]},
            "target": {"inline_rows": [{"id": 1}]},
        }
    )


def test_workflow_versioning_patch_bump_on_duplicate_version() -> None:
    repository = InMemoryYamlWorkflowRepository()
    service = WorkflowVersionService(repository)

    v1 = service.save(_config("1.0.0"))
    v2 = service.save(_config("1.0.0"))

    assert v1 == "1.0.0"
    assert v2 == "1.0.1"
    assert service.list_versions("wf-versioned") == ["1.0.0", "1.0.1"]
