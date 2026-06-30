import csv
import json
import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from app.repositories.result_repository import InMemoryResultRepository, ResultRecord


class ResultStorageService:
    def __init__(self, repository: InMemoryResultRepository | None = None) -> None:
        self.repository = repository or InMemoryResultRepository()

    def store_result(
        self,
        workflow_id: str,
        payload: dict[str, Any],
        output_dir: str,
        formats: list[str],
        retention_days: int = 30,
        archive_enabled: bool = True,
        archive_dir: str | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        stamp = now.strftime("%Y%m%d%H%M%S%f")
        result_id = f"{workflow_id}-{stamp}"

        directory = Path(output_dir)
        directory.mkdir(parents=True, exist_ok=True)

        warnings: list[str] = []
        artifacts: dict[str, str] = {}
        normalized_formats = [fmt.lower() for fmt in formats]

        for fmt in normalized_formats:
            if fmt == "database":
                continue
            if fmt == "json":
                artifacts[fmt] = self._write_json(directory, result_id, payload)
            elif fmt == "csv":
                artifacts[fmt] = self._write_csv(directory, result_id, payload)
            elif fmt == "html":
                artifacts[fmt] = self._write_html(directory, result_id, payload)
            elif fmt == "parquet":
                path, warning = self._write_parquet(directory, result_id, payload)
                if path:
                    artifacts[fmt] = path
                if warning:
                    warnings.append(warning)
            elif fmt == "excel":
                path, warning = self._write_excel(directory, result_id, payload)
                if path:
                    artifacts[fmt] = path
                if warning:
                    warnings.append(warning)
            else:
                warnings.append(f"unsupported_result_format:{fmt}")

        record = ResultRecord(
            result_id=result_id,
            workflow_id=workflow_id,
            created_at=now,
            payload=payload,
            artifacts=artifacts,
        )
        self.repository.add(record)

        retention = max(0, int(retention_days))
        archive_path = archive_dir or str(directory / "archive")
        self.apply_retention_policy(
            retention_days=retention,
            archive_enabled=archive_enabled,
            archive_dir=archive_path,
        )

        return {
            "result_id": result_id,
            "stored_in_database": "database" in normalized_formats,
            "formats": normalized_formats,
            "artifacts": artifacts,
            "warnings": warnings,
            "retention_days": retention,
            "archive_enabled": archive_enabled,
            "archive_dir": archive_path,
        }

    def download_result(self, result_id: str, format_name: str) -> dict[str, Any]:
        record = self.repository.get(result_id)
        if record is None:
            return {"success": False, "error": "result_not_found"}

        fmt = format_name.lower()
        if fmt == "database":
            content = json.dumps(record.payload, default=str, indent=2).encode("utf-8")
            return {
                "success": True,
                "format": "database",
                "filename": f"{result_id}.json",
                "content": content,
            }

        path = record.artifacts.get(fmt)
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

    def apply_retention_policy(self, retention_days: int, archive_enabled: bool, archive_dir: str) -> dict[str, int]:
        cutoff = datetime.now(UTC) - timedelta(days=retention_days)
        archived_count = 0
        deleted_count = 0

        for record in list(self.repository.list_all()):
            if record.created_at >= cutoff:
                continue
            if archive_enabled:
                if self.archive_result(record.result_id, archive_dir=archive_dir):
                    archived_count += 1
            else:
                self.delete_result(record.result_id)
                deleted_count += 1

        return {"archived": archived_count, "deleted": deleted_count}

    def archive_result(self, result_id: str, archive_dir: str) -> bool:
        record = self.repository.get(result_id)
        if record is None:
            return False
        if record.archived:
            return True

        archive_path = Path(archive_dir)
        archive_path.mkdir(parents=True, exist_ok=True)
        updated_artifacts: dict[str, str] = {}

        for fmt, artifact in record.artifacts.items():
            source = Path(artifact)
            if not source.exists():
                continue
            destination = archive_path / source.name
            shutil.move(str(source), str(destination))
            updated_artifacts[fmt] = str(destination)

        record.artifacts = updated_artifacts
        self.repository.mark_archived(result_id)
        return True

    def delete_result(self, result_id: str) -> None:
        record = self.repository.get(result_id)
        if record is None:
            return
        for artifact in record.artifacts.values():
            path = Path(artifact)
            if path.exists():
                path.unlink()
        self.repository.delete(result_id)

    def _write_json(self, directory: Path, result_id: str, payload: dict[str, Any]) -> str:
        path = directory / f"{result_id}.json"
        path.write_text(json.dumps(payload, default=str, indent=2), encoding="utf-8")
        return str(path)

    def _write_csv(self, directory: Path, result_id: str, payload: dict[str, Any]) -> str:
        path = directory / f"{result_id}.csv"
        rows = []
        validation = payload.get("validation_results", {})
        for key, value in validation.items():
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

    def _write_html(self, directory: Path, result_id: str, payload: dict[str, Any]) -> str:
        path = directory / f"{result_id}.html"
        validation_rows = "".join(
            f"<tr><td>{key}</td><td>{value.get('success')}</td><td>{value.get('score')}</td><td>{value.get('message')}</td></tr>"
            for key, value in payload.get("validation_results", {}).items()
        )
        html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Validation Result</title></head><body>"
            f"<h1>Workflow Result: {payload.get('workflow_id')}</h1>"
            f"<p>Overall Success: {payload.get('success')}</p>"
            "<table border='1' cellpadding='6' cellspacing='0'>"
            "<thead><tr><th>Validator</th><th>Success</th><th>Score</th><th>Message</th></tr></thead>"
            f"<tbody>{validation_rows}</tbody>"
            "</table></body></html>"
        )
        path.write_text(html, encoding="utf-8")
        return str(path)

    def _write_parquet(self, directory: Path, result_id: str, payload: dict[str, Any]) -> tuple[str | None, str | None]:
        try:
            import pandas as pd  # type: ignore
        except ImportError:
            return None, "parquet_export_skipped_pandas_not_installed"

        rows = []
        validation = payload.get("validation_results", {})
        for key, value in validation.items():
            rows.append(
                {
                    "validator": key,
                    "success": value.get("success"),
                    "score": value.get("score"),
                    "message": value.get("message"),
                }
            )
        df = pd.DataFrame(rows)
        path = directory / f"{result_id}.parquet"
        try:
            df.to_parquet(path, index=False)
        except Exception:
            return None, "parquet_export_skipped_missing_parquet_engine"
        return str(path), None

    def _write_excel(self, directory: Path, result_id: str, payload: dict[str, Any]) -> tuple[str | None, str | None]:
        try:
            import pandas as pd  # type: ignore
        except ImportError:
            return None, "excel_export_skipped_pandas_not_installed"

        rows = []
        validation = payload.get("validation_results", {})
        for key, value in validation.items():
            rows.append(
                {
                    "validator": key,
                    "success": value.get("success"),
                    "score": value.get("score"),
                    "message": value.get("message"),
                }
            )
        df = pd.DataFrame(rows)
        path = directory / f"{result_id}.xlsx"
        try:
            df.to_excel(path, index=False)
        except Exception:
            return None, "excel_export_skipped_openpyxl_not_installed"
        return str(path), None
