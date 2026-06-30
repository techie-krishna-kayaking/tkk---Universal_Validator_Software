import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.repositories.report_repository import EmailReportEvent, InMemoryReportRepository, ReportRecord
from app.repositories.result_repository import ResultRecord


class ReportService:
    def __init__(self, repository: InMemoryReportRepository | None = None) -> None:
        self.repository = repository or InMemoryReportRepository()

    def generate_reports(
        self,
        workflow_id: str,
        result_id: str,
        result_payload: dict[str, Any],
        output_dir: str,
        formats: list[str],
        report_types: list[str],
        history: list[ResultRecord],
        email_recipients: list[str] | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        report_id = f"{workflow_id}-report-{now.strftime('%Y%m%d%H%M%S%f')}"
        directory = Path(output_dir)
        directory.mkdir(parents=True, exist_ok=True)

        report_payload = self._build_report_payload(
            workflow_id=workflow_id,
            result_id=result_id,
            result_payload=result_payload,
            report_types=report_types,
            history=history,
        )

        artifacts: dict[str, str] = {}
        warnings: list[str] = []
        normalized_formats = [item.lower() for item in formats]
        for fmt in normalized_formats:
            if fmt == "html":
                artifacts[fmt] = self._write_html(directory, report_id, report_payload)
            elif fmt == "json":
                artifacts[fmt] = self._write_json(directory, report_id, report_payload)
            elif fmt == "csv":
                artifacts[fmt] = self._write_csv(directory, report_id, report_payload)
            elif fmt == "excel":
                path, warning = self._write_excel(directory, report_id, report_payload)
                if path:
                    artifacts[fmt] = path
                if warning:
                    warnings.append(warning)
            elif fmt == "pdf":
                path, warning = self._write_pdf(directory, report_id, report_payload)
                if path:
                    artifacts[fmt] = path
                if warning:
                    warnings.append(warning)
            else:
                warnings.append(f"unsupported_report_format:{fmt}")

        record = ReportRecord(
            report_id=report_id,
            workflow_id=workflow_id,
            result_id=result_id,
            created_at=now,
            payload=report_payload,
            artifacts=artifacts,
        )
        self.repository.add_report(record)

        email_result = self._send_email_report(
            workflow_id=workflow_id,
            report_id=report_id,
            recipients=email_recipients or [],
            summary=report_payload.get("executive_summary", {}),
        )

        return {
            "report_id": report_id,
            "formats": normalized_formats,
            "report_types": report_types,
            "artifacts": artifacts,
            "warnings": warnings,
            "email": email_result,
        }

    def download_report(self, report_id: str, format_name: str) -> dict[str, Any]:
        report = self.repository.get_report(report_id)
        if report is None:
            return {"success": False, "error": "report_not_found"}

        fmt = format_name.lower()
        path = report.artifacts.get(fmt)
        if not path:
            return {"success": False, "error": "format_not_available"}

        file_path = Path(path)
        if not file_path.exists():
            return {"success": False, "error": "artifact_missing"}

        return {
            "success": True,
            "format": fmt,
            "filename": file_path.name,
            "content": file_path.read_bytes(),
        }

    def _build_report_payload(
        self,
        workflow_id: str,
        result_id: str,
        result_payload: dict[str, Any],
        report_types: list[str],
        history: list[ResultRecord],
    ) -> dict[str, Any]:
        selected = {item.lower() for item in report_types}
        payload: dict[str, Any] = {
            "workflow_id": workflow_id,
            "result_id": result_id,
            "generated_at": datetime.now(UTC).isoformat(),
        }

        validation = result_payload.get("validation_results", {})
        total = len(validation)
        passed = sum(1 for value in validation.values() if value.get("success"))
        failed = total - passed

        if "executive_summary" in selected:
            payload["executive_summary"] = {
                "overall_success": bool(result_payload.get("success")),
                "total_validations": total,
                "passed_validations": passed,
                "failed_validations": failed,
                "success_rate": round((passed / total) * 100.0, 2) if total else 100.0,
            }

        if "detailed_report" in selected:
            payload["detailed_report"] = {
                "execution": result_payload.get("execution", {}),
                "profiling": result_payload.get("profiling", {}),
                "validation_results": validation,
                "anomaly_visualizations": result_payload.get("anomaly_visualizations", {}),
            }

        sorted_history = sorted(history, key=lambda record: record.created_at)
        previous = [record for record in sorted_history if record.result_id != result_id]

        if "comparison_report" in selected:
            baseline = previous[-1] if previous else None
            comparison = {
                "baseline_result_id": baseline.result_id if baseline else None,
                "current_result_id": result_id,
                "baseline_success": baseline.payload.get("success") if baseline else None,
                "current_success": result_payload.get("success"),
                "delta_passed_validations": self._delta_passed(validation, baseline.payload.get("validation_results", {}) if baseline else {}),
            }
            payload["comparison_report"] = comparison

        if "trend_report" in selected:
            trend_points = []
            for record in sorted_history[-20:]:
                record_validation = record.payload.get("validation_results", {})
                total_count = len(record_validation)
                pass_count = sum(1 for value in record_validation.values() if value.get("success"))
                trend_points.append(
                    {
                        "result_id": record.result_id,
                        "timestamp": record.created_at.isoformat(),
                        "overall_success": bool(record.payload.get("success")),
                        "success_rate": round((pass_count / total_count) * 100.0, 2) if total_count else 100.0,
                    }
                )
            payload["trend_report"] = {
                "points": trend_points,
                "window_size": len(trend_points),
            }

        return payload

    def _delta_passed(self, current: dict[str, Any], baseline: dict[str, Any]) -> int:
        current_passed = sum(1 for value in current.values() if value.get("success"))
        baseline_passed = sum(1 for value in baseline.values() if value.get("success"))
        return current_passed - baseline_passed

    def _send_email_report(self, workflow_id: str, report_id: str, recipients: list[str], summary: dict[str, Any]) -> dict[str, Any]:
        if not recipients:
            return {"queued": False, "reason": "no_recipients"}

        subject = f"Validation Report for {workflow_id}"
        body = (
            f"Report ID: {report_id}\n"
            f"Overall Success: {summary.get('overall_success')}\n"
            f"Success Rate: {summary.get('success_rate')}\n"
            f"Passed: {summary.get('passed_validations')}\n"
            f"Failed: {summary.get('failed_validations')}\n"
        )

        event = EmailReportEvent(
            event_id=str(uuid4()),
            workflow_id=workflow_id,
            report_id=report_id,
            recipients=recipients,
            subject=subject,
            body=body,
            created_at=datetime.now(UTC),
        )
        self.repository.queue_email(event)
        return {
            "queued": True,
            "event_id": event.event_id,
            "recipients": recipients,
        }

    def _write_json(self, directory: Path, report_id: str, payload: dict[str, Any]) -> str:
        path = directory / f"{report_id}.json"
        path.write_text(json.dumps(payload, default=str, indent=2), encoding="utf-8")
        return str(path)

    def _write_csv(self, directory: Path, report_id: str, payload: dict[str, Any]) -> str:
        path = directory / f"{report_id}.csv"
        rows = []
        details = payload.get("detailed_report", {}).get("validation_results", {})
        for key, value in details.items():
            rows.append(
                {
                    "validator": key,
                    "success": value.get("success"),
                    "score": value.get("score"),
                    "message": value.get("message"),
                }
            )

        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["validator", "success", "score", "message"])
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return str(path)

    def _write_html(self, directory: Path, report_id: str, payload: dict[str, Any]) -> str:
        path = directory / f"{report_id}.html"
        summary = payload.get("executive_summary", {})
        details = payload.get("detailed_report", {}).get("validation_results", {})
        rows = "".join(
            f"<tr><td>{key}</td><td>{value.get('success')}</td><td>{value.get('score')}</td><td>{value.get('message')}</td></tr>"
            for key, value in details.items()
        )
        trend_points = payload.get("trend_report", {}).get("points", [])
        trend_rows = "".join(
            f"<tr><td>{point.get('timestamp')}</td><td>{point.get('overall_success')}</td><td>{point.get('success_rate')}</td></tr>"
            for point in trend_points
        )

        html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Validation Report</title></head><body>"
            f"<h1>Validation Report: {payload.get('workflow_id')}</h1>"
            "<h2>Executive Summary</h2>"
            f"<p>Overall Success: {summary.get('overall_success')}</p>"
            f"<p>Success Rate: {summary.get('success_rate')}</p>"
            "<h2>Detailed Report</h2>"
            "<table border='1' cellpadding='6' cellspacing='0'>"
            "<thead><tr><th>Validator</th><th>Success</th><th>Score</th><th>Message</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>"
            "<h2>Trend Report</h2>"
            "<table border='1' cellpadding='6' cellspacing='0'>"
            "<thead><tr><th>Timestamp</th><th>Success</th><th>Success Rate</th></tr></thead>"
            f"<tbody>{trend_rows}</tbody></table>"
            "</body></html>"
        )
        path.write_text(html, encoding="utf-8")
        return str(path)

    def _write_excel(self, directory: Path, report_id: str, payload: dict[str, Any]) -> tuple[str | None, str | None]:
        try:
            import pandas as pd  # type: ignore
        except ImportError:
            return None, "excel_report_skipped_pandas_not_installed"

        details = payload.get("detailed_report", {}).get("validation_results", {})
        rows = []
        for key, value in details.items():
            rows.append(
                {
                    "validator": key,
                    "success": value.get("success"),
                    "score": value.get("score"),
                    "message": value.get("message"),
                }
            )

        path = directory / f"{report_id}.xlsx"
        try:
            pd.DataFrame(rows).to_excel(path, index=False)
        except Exception:
            return None, "excel_report_skipped_openpyxl_not_installed"
        return str(path), None

    def _write_pdf(self, directory: Path, report_id: str, payload: dict[str, Any]) -> tuple[str | None, str | None]:
        path = directory / f"{report_id}.pdf"
        summary = payload.get("executive_summary", {})
        try:
            from reportlab.lib.pagesizes import letter  # type: ignore
            from reportlab.pdfgen import canvas  # type: ignore

            pdf = canvas.Canvas(str(path), pagesize=letter)
            y = 750
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(50, y, f"Validation Report: {payload.get('workflow_id')}")
            y -= 30
            pdf.setFont("Helvetica", 10)
            for line in [
                f"Result ID: {payload.get('result_id')}",
                f"Overall Success: {summary.get('overall_success')}",
                f"Success Rate: {summary.get('success_rate')}",
                f"Passed: {summary.get('passed_validations')}",
                f"Failed: {summary.get('failed_validations')}",
            ]:
                pdf.drawString(50, y, line)
                y -= 16
            pdf.showPage()
            pdf.save()
            return str(path), None
        except ImportError:
            return None, "pdf_report_skipped_reportlab_not_installed"
