from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.services.result_storage_service import ResultStorageService


def _payload() -> dict:
    return {
        "workflow_id": "wf-result",
        "validation_results": {
            "validation.record_count": {
                "success": True,
                "score": 1.0,
                "message": "ok",
            }
        },
        "success": True,
    }


def test_store_result_writes_database_csv_json_html_and_download(tmp_path: Path) -> None:
    service = ResultStorageService()

    stored = service.store_result(
        workflow_id="wf-result",
        payload=_payload(),
        output_dir=str(tmp_path),
        formats=["database", "csv", "json", "html"],
        retention_days=30,
        archive_enabled=True,
    )

    assert stored["stored_in_database"] is True
    assert "csv" in stored["artifacts"]
    assert "json" in stored["artifacts"]
    assert "html" in stored["artifacts"]
    assert Path(stored["artifacts"]["csv"]).exists()
    assert Path(stored["artifacts"]["json"]).exists()
    assert Path(stored["artifacts"]["html"]).exists()

    download = service.download_result(stored["result_id"], "json")
    assert download["success"] is True
    assert download["filename"].endswith(".json")
    assert len(download["content"]) > 0


def test_retention_archives_expired_results(tmp_path: Path) -> None:
    service = ResultStorageService()
    stored = service.store_result(
        workflow_id="wf-old",
        payload=_payload(),
        output_dir=str(tmp_path),
        formats=["database", "json"],
        retention_days=30,
        archive_enabled=True,
        archive_dir=str(tmp_path / "archive"),
    )

    record = service.repository.get(stored["result_id"])
    assert record is not None
    record.created_at = datetime.now(UTC) - timedelta(days=90)

    outcome = service.apply_retention_policy(
        retention_days=30,
        archive_enabled=True,
        archive_dir=str(tmp_path / "archive"),
    )

    assert outcome["archived"] >= 1
    updated = service.repository.get(stored["result_id"])
    assert updated is not None
    assert updated.archived is True
    for artifact in updated.artifacts.values():
        assert str(tmp_path / "archive") in artifact
