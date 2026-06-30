from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class WorkflowVersionRecord:
    workflow_id: str
    version: str
    payload: dict
    created_at: datetime


@dataclass
class InMemoryYamlWorkflowRepository:
    records: dict[str, list[WorkflowVersionRecord]] = field(default_factory=dict)

    def add_version(self, workflow_id: str, version: str, payload: dict) -> WorkflowVersionRecord:
        record = WorkflowVersionRecord(
            workflow_id=workflow_id,
            version=version,
            payload=payload,
            created_at=datetime.now(UTC),
        )
        self.records.setdefault(workflow_id, []).append(record)
        return record

    def list_versions(self, workflow_id: str) -> list[WorkflowVersionRecord]:
        return list(self.records.get(workflow_id, []))

    def latest(self, workflow_id: str) -> WorkflowVersionRecord | None:
        versions = self.records.get(workflow_id, [])
        if not versions:
            return None
        return versions[-1]
