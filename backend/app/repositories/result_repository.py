from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class ResultRecord:
    result_id: str
    workflow_id: str
    created_at: datetime
    payload: dict[str, Any]
    artifacts: dict[str, str] = field(default_factory=dict)
    archived: bool = False
    archived_at: datetime | None = None


@dataclass
class InMemoryResultRepository:
    records: dict[str, ResultRecord] = field(default_factory=dict)

    def add(self, record: ResultRecord) -> ResultRecord:
        self.records[record.result_id] = record
        return record

    def get(self, result_id: str) -> ResultRecord | None:
        return self.records.get(result_id)

    def list_by_workflow(self, workflow_id: str) -> list[ResultRecord]:
        return [record for record in self.records.values() if record.workflow_id == workflow_id]

    def list_all(self) -> list[ResultRecord]:
        return list(self.records.values())

    def delete(self, result_id: str) -> None:
        self.records.pop(result_id, None)

    def mark_archived(self, result_id: str) -> None:
        record = self.records.get(result_id)
        if record is None:
            return
        record.archived = True
        record.archived_at = datetime.now(UTC)
