from pathlib import Path
from typing import Any

from app.profiling.engine import DataProfilingEngine
from app.profiling.reporter import HtmlProfileReporter


class ProfilingService:
    def __init__(
        self,
        engine: DataProfilingEngine | None = None,
        reporter: HtmlProfileReporter | None = None,
    ) -> None:
        self.engine = engine or DataProfilingEngine()
        self.reporter = reporter or HtmlProfileReporter()

    def profile_pair(
        self,
        workflow_id: str,
        source_rows: list[dict[str, Any]],
        target_rows: list[dict[str, Any]],
        output_dir: str,
    ) -> dict[str, Any]:
        source_profile = self.engine.profile_dataset(source_rows, dataset_name="source")
        target_profile = self.engine.profile_dataset(target_rows, dataset_name="target")

        report_path = Path(output_dir) / f"{workflow_id}_profile_report.html"
        html = self.reporter.render_report(workflow_id, source_profile, target_profile)
        written_path = self.reporter.write_report(html, report_path)

        return {
            "source": source_profile,
            "target": target_profile,
            "html_report_path": written_path,
        }
