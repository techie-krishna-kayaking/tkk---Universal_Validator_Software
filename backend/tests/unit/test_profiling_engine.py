from pathlib import Path

from app.profiling.engine import DataProfilingEngine
from app.profiling.reporter import HtmlProfileReporter
from app.services.profiling_service import ProfilingService


def test_profiling_engine_generates_required_metrics() -> None:
    rows = [
        {"id": 1, "score": 10.0, "status": "active"},
        {"id": 2, "score": 20.0, "status": "inactive"},
        {"id": 3, "score": None, "status": "active"},
    ]

    profile = DataProfilingEngine().profile_dataset(rows, dataset_name="source")

    assert profile["schema"]["id"] == "int"
    assert round(profile["columns"]["score"]["null_percent"], 4) == 33.3333
    assert profile["columns"]["status"]["unique_count"] == 2
    assert profile["columns"]["score"]["min"] == 10.0
    assert profile["columns"]["score"]["max"] == 20.0
    assert profile["columns"]["score"]["average"] == 15.0
    assert len(profile["columns"]["score"]["histogram"]) >= 1
    assert len(profile["columns"]["status"]["top_values"]) >= 1
    assert len(profile["columns"]["status"]["distribution"]) >= 1
    assert profile["columns"]["status"]["cardinality"] == 2


def test_html_profile_report_is_created(tmp_path: Path) -> None:
    service = ProfilingService()
    source_rows = [{"id": 1, "status": "active"}]
    target_rows = [{"id": 1, "status": "active"}]

    result = service.profile_pair(
        workflow_id="wf-profile",
        source_rows=source_rows,
        target_rows=target_rows,
        output_dir=str(tmp_path),
    )

    report_path = Path(result["html_report_path"])
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "Data Profile Report" in content
    assert "wf-profile" in content


def test_html_reporter_renders_dataset_sections() -> None:
    reporter = HtmlProfileReporter()
    source_profile = {
        "dataset_name": "source",
        "row_count": 1,
        "column_count": 1,
        "columns": {
            "id": {
                "inferred_type": "int",
                "null_percent": 0.0,
                "uniqueness_percent": 100.0,
                "min": 1,
                "max": 1,
                "average": 1.0,
                "cardinality": 1,
                "histogram": [],
                "top_values": [{"value": 1, "count": 1}],
                "distribution": [{"value": 1, "count": 1, "percent": 100.0}],
            }
        },
    }
    target_profile = {
        "dataset_name": "target",
        "row_count": 1,
        "column_count": 1,
        "columns": source_profile["columns"],
    }

    html = reporter.render_report("wf-sample", source_profile, target_profile)
    assert "<h2>source</h2>" in html
    assert "<h2>target</h2>" in html
    assert "wf-sample" in html
