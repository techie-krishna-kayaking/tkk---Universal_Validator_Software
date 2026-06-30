from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class ExpectationSuiteRecord:
    suite_id: str
    version: str
    expectations: list[dict[str, Any]]
    created_at: datetime


@dataclass
class ExpectationRunRecord:
    suite_id: str
    suite_version: str
    run_id: str
    result: dict[str, Any]
    created_at: datetime


@dataclass
class InMemoryExpectationRepository:
    suites: dict[str, list[ExpectationSuiteRecord]] = field(default_factory=dict)
    runs: dict[str, list[ExpectationRunRecord]] = field(default_factory=dict)

    def add_suite_version(self, suite_id: str, version: str, expectations: list[dict[str, Any]]) -> ExpectationSuiteRecord:
        record = ExpectationSuiteRecord(
            suite_id=suite_id,
            version=version,
            expectations=expectations,
            created_at=datetime.now(UTC),
        )
        self.suites.setdefault(suite_id, []).append(record)
        return record

    def list_suite_versions(self, suite_id: str) -> list[ExpectationSuiteRecord]:
        return list(self.suites.get(suite_id, []))

    def latest_suite(self, suite_id: str) -> ExpectationSuiteRecord | None:
        versions = self.suites.get(suite_id, [])
        return versions[-1] if versions else None

    def add_run_result(self, suite_id: str, suite_version: str, run_id: str, result: dict[str, Any]) -> ExpectationRunRecord:
        record = ExpectationRunRecord(
            suite_id=suite_id,
            suite_version=suite_version,
            run_id=run_id,
            result=result,
            created_at=datetime.now(UTC),
        )
        self.runs.setdefault(suite_id, []).append(record)
        return record

    def list_run_results(self, suite_id: str) -> list[ExpectationRunRecord]:
        return list(self.runs.get(suite_id, []))
