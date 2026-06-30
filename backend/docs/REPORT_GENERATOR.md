# Report Generator

## Overview
The Report Generator creates multi-format validation reports from workflow execution results.

## Formats
- HTML
- PDF
- Excel
- CSV
- JSON

## Report Types
- Executive Summary
- Detailed Report
- Comparison Report
- Trend Report

## Email Reports
When recipients are configured, report metadata is queued into an in-memory email outbox.

## Comparison and Trend
- Comparison Report contrasts current run status against the previous run for the same workflow.
- Trend Report summarizes recent workflow outcomes over a rolling history window.

## Workflow Integration
`YamlWorkflowExecutor` invokes `ReportService` after result storage. The execution response includes:
- `reports.report_id`
- `reports.artifacts`
- `reports.email`
- `reports.warnings`

## Download API Surface
`YamlWorkflowService.download_report(report_id, format_name)` returns report bytes and filename metadata.

## Notes
PDF and Excel generation may require optional runtime dependencies (`reportlab`, `pandas` + excel backend). If unavailable, the report service returns non-fatal warnings.
