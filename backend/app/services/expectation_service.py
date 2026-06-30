from datetime import UTC, datetime
from typing import Any

from app.expectations.engine import ExpectationEngine
from app.repositories.expectation_repository import InMemoryExpectationRepository


class ExpectationService:
    def __init__(
        self,
        repository: InMemoryExpectationRepository | None = None,
        engine: ExpectationEngine | None = None,
    ) -> None:
        self.repository = repository or InMemoryExpectationRepository()
        self.engine = engine or ExpectationEngine()

    def generate_suite(
        self,
        suite_id: str,
        rows: list[dict[str, Any]],
        primary_keys: list[str] | None = None,
        base_version: str = "1.0.0",
    ) -> dict[str, Any]:
        expectations = self.engine.auto_generate(rows=rows, primary_keys=primary_keys)
        version = self._next_version(suite_id, requested=base_version)
        self.repository.add_suite_version(suite_id=suite_id, version=version, expectations=expectations)
        return {"suite_id": suite_id, "version": version, "expectations": expectations}

    def edit_suite(
        self,
        suite_id: str,
        expectations: list[dict[str, Any]],
        requested_version: str | None = None,
    ) -> dict[str, Any]:
        version = self._next_version(suite_id, requested=requested_version)
        self.repository.add_suite_version(suite_id=suite_id, version=version, expectations=expectations)
        return {"suite_id": suite_id, "version": version, "expectations": expectations}

    def run_suite(
        self,
        suite_id: str,
        rows: list[dict[str, Any]],
        expectations: list[dict[str, Any]] | None = None,
        auto_generate: bool = False,
        primary_keys: list[str] | None = None,
    ) -> dict[str, Any]:
        suite = self.repository.latest_suite(suite_id)

        if expectations:
            suite_payload = self.edit_suite(suite_id=suite_id, expectations=expectations)
            suite = self.repository.latest_suite(suite_id)
        elif suite is None and auto_generate:
            self.generate_suite(suite_id=suite_id, rows=rows, primary_keys=primary_keys)
            suite = self.repository.latest_suite(suite_id)

        if suite is None:
            return {
                "success": False,
                "suite_id": suite_id,
                "error": "suite_not_found",
                "results": [],
            }

        run_result = self.engine.run(rows=rows, expectations=suite.expectations)
        run_id = f"{suite_id}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}"
        self.repository.add_run_result(
            suite_id=suite_id,
            suite_version=suite.version,
            run_id=run_id,
            result=run_result,
        )

        return {
            "suite_id": suite_id,
            "suite_version": suite.version,
            "run_id": run_id,
            **run_result,
        }

    def list_suite_versions(self, suite_id: str) -> list[str]:
        return [record.version for record in self.repository.list_suite_versions(suite_id)]

    def list_run_results(self, suite_id: str) -> list[dict[str, Any]]:
        return [
            {
                "run_id": record.run_id,
                "suite_version": record.suite_version,
                "created_at": record.created_at.isoformat(),
                "result": record.result,
            }
            for record in self.repository.list_run_results(suite_id)
        ]

    def _next_version(self, suite_id: str, requested: str | None) -> str:
        latest = self.repository.latest_suite(suite_id)
        if requested and (latest is None or requested != latest.version):
            return requested
        if latest is None:
            return requested or "1.0.0"
        return self._bump_patch(latest.version)

    def _bump_patch(self, version: str) -> str:
        major, minor, patch = version.split(".")
        return f"{major}.{minor}.{int(patch) + 1}"
