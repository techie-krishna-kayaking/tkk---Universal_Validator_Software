from html import escape
from pathlib import Path
from typing import Any


class HtmlProfileReporter:
    def render_report(self, workflow_id: str, source_profile: dict[str, Any], target_profile: dict[str, Any]) -> str:
        source_html = self._render_dataset(source_profile)
        target_html = self._render_dataset(target_profile)

        return f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Data Profile Report - {escape(workflow_id)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 24px; color: #1f2937; }}
    h1 {{ margin-bottom: 8px; }}
    h2 {{ margin-top: 28px; border-bottom: 1px solid #e5e7eb; padding-bottom: 6px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 12px; margin-bottom: 20px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 8px; text-align: left; font-size: 13px; vertical-align: top; }}
    th {{ background: #f3f4f6; font-weight: 600; }}
    code {{ background: #f9fafb; padding: 1px 4px; border-radius: 4px; }}
    .meta {{ color: #6b7280; font-size: 13px; }}
  </style>
</head>
<body>
  <h1>Data Profile Report</h1>
  <div class=\"meta\">Workflow: <code>{escape(workflow_id)}</code></div>
  {source_html}
  {target_html}
</body>
</html>
""".strip()

    def write_report(self, html_content: str, output_path: str | Path) -> str:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html_content, encoding="utf-8")
        return str(path)

    def _render_dataset(self, profile: dict[str, Any]) -> str:
        rows = []
        for column_name, stats in profile.get("columns", {}).items():
            rows.append(
                "<tr>"
                f"<td>{escape(str(column_name))}</td>"
                f"<td>{escape(str(stats.get('inferred_type')))}</td>"
                f"<td>{escape(str(stats.get('null_percent')))}</td>"
                f"<td>{escape(str(stats.get('uniqueness_percent')))}</td>"
                f"<td>{escape(str(stats.get('min')))}</td>"
                f"<td>{escape(str(stats.get('max')))}</td>"
                f"<td>{escape(str(stats.get('average')))}</td>"
                f"<td>{escape(str(stats.get('cardinality')))}</td>"
                f"<td>{escape(str(stats.get('histogram')))}</td>"
                f"<td>{escape(str(stats.get('top_values')))}</td>"
                f"<td>{escape(str(stats.get('distribution')))}</td>"
                "</tr>"
            )

        table = (
            "<table>"
            "<thead><tr>"
            "<th>Column</th><th>Schema</th><th>Null %</th><th>Uniqueness %</th>"
            "<th>Min</th><th>Max</th><th>Average</th><th>Cardinality</th>"
            "<th>Histogram</th><th>Top Values</th><th>Distribution</th>"
            "</tr></thead>"
            f"<tbody>{''.join(rows)}</tbody>"
            "</table>"
        )

        return (
            f"<h2>{escape(str(profile.get('dataset_name', 'dataset')))}</h2>"
            f"<div class=\"meta\">Rows: {escape(str(profile.get('row_count')))} | Columns: {escape(str(profile.get('column_count')))}</div>"
            + table
        )
