from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.repositories.result_repository import ResultRecord
from app.services.report_service import ReportService


def _payload(success: bool, score: float = 1.0) -> dict:
    return {
        "workflow_id": "wf-report",
        "success": success,
        "execution": {"source_success": success, "target_success": success},
        "profiling": {"source": {}, "target": {}},
        "validation_results": {
            "validation.record_count": {
                "success": success,
                "score": score,
                "message": "ok" if success else "failed",
            }
        },
        "anomaly_visualizations": {},
    }


def test_generate_reports_all_formats_and_email(tmp_path: Path) -> None:
    service = ReportService()

    history = [
        ResultRecord(
            result_id="old-1",
            workflow_id="wf-report",
            created_at=datetime.now(UTC) - timedelta(days=1),
            payload=_payload(success=True),
        )
    ]

    report = service.generate_reports(
        workflow_id="wf-report",
        result_id="new-1",
        result_payload=_payload(success=False, score=0.0),
        output_dir=str(tmp_path),
        formats=["html", "pdf", "excel", "csv", "json"],
        report_types=["executive_summary", "detailed_report", "comparison_report", "trend_report"],
        history=history,
        email_recipients=["qa@example.com"],
    )

    assert "html" in report["artifacts"]
    assert "csv" in report["artifacts"]
    assert "json" in report["artifacts"]
    assert report["email"]["queued"] is True
    assert Path(report["artifacts"]["html"]).exists()
    assert Path(report["artifacts"]["csv"]).exists()
    assert Path(report["artifacts"]["json"]).exists()
    assert ("pdf" in report["artifacts"]) or any("pdf_report_skipped" in warning for warning in report["warnings"])


def test_report_download(tmp_path: Path) -> None:
    service = ReportService()
    report = service.generate_reports(
        workflow_id="wf-report",
        result_id="new-2",
        result_payload=_payload(success=True),
        output_dir=str(tmp_path),
        formats=["json"],
        report_types=["executive_summary"],
        history=[],
        email_recipients=[],
    )

    download = service.download_report(report_id=report["report_id"], format_name="json")
    assert download["success"] is True
    assert download["filename"].endswith(".json")
    assert len(download["content"]) > 0
