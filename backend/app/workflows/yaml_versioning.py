from app.repositories.yaml_workflow_repository import InMemoryYamlWorkflowRepository
from app.workflows.yaml_schema import WorkflowConfig


class WorkflowVersionService:
    def __init__(self, repository: InMemoryYamlWorkflowRepository | None = None) -> None:
        self.repository = repository or InMemoryYamlWorkflowRepository()

    def save(self, config: WorkflowConfig) -> str:
        latest = self.repository.latest(config.workflow_id)
        version = config.version

        if latest and version == latest.version:
            version = self._bump_patch(version)

        payload = config.model_dump()
        payload["version"] = version
        self.repository.add_version(config.workflow_id, version, payload)
        return version

    def list_versions(self, workflow_id: str) -> list[str]:
        return [record.version for record in self.repository.list_versions(workflow_id)]

    def latest_payload(self, workflow_id: str) -> dict | None:
        latest = self.repository.latest(workflow_id)
        return latest.payload if latest else None

    @staticmethod
    def _bump_patch(version: str) -> str:
        major, minor, patch = version.split(".")
        return f"{major}.{minor}.{int(patch) + 1}"
