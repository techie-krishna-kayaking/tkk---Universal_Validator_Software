# YAML Workflow Engine

## Overview
The YAML Workflow Engine enables declarative execution pipelines for validation workflows.

## Supported YAML Sections
- Source
- Target
- Primary Keys
- Join Keys
- Filters
- Transformations
- SQL Queries
- SQL Transformations (Views, Temporary Tables, CTEs, Stored Procedures, Parameters)
- Spark SQL
- Python Transformations
- Great Expectations
- Anomaly Detection
- Result Storage
- Reporting
- Validation Selection
- Sampling
- Scheduling
- Output Location

Additional scheduler orchestration fields are supported for the `scheduling` section:
- `interval_seconds`
- `max_retries`
- `priority`
- `queue`
- `concurrency_key`
- `notification_channel`

## Schema Validation
- YAML payloads are validated through pydantic models.
- Semantic version format is required for `version`.
- Scheduling constraints are validated (`cron` mode requires cron expression, `once` mode requires run_at).
- Recurring constraints are validated (`recurring` mode requires positive `interval_seconds`).
- Retry and queue metadata are validated (`max_retries >= 0`, queue non-empty, priority between 1 and 1000).

## Auto-Complete Templates
`YamlTemplateService` provides:
- `base_template()` for standard scaffold generation.
- `autocomplete(partial)` for merging partial YAML and filling defaults.

## Versioning
`WorkflowVersionService` provides in-memory semantic version tracking:
- Duplicate version save attempts auto-bump patch version.
- Version history is available per workflow_id.

`ExpectationService` provides Great Expectations suite lifecycle management:
- automatic expectation generation from dataset metadata
- editable expectation suites via YAML (`editable_expectations`)
- expectation suite execution and result storage
- suite versioning with semantic patch bumping

`AnomalyDetectionService` provides anomaly model orchestration:
- implemented model: Isolation Forest
- future-ready detector interface for: One-Class SVM, Autoencoder, Prophet, Seasonal Detection
- visualization payloads for anomaly scatter plots and anomaly-score histograms

`ResultStorageService` provides multi-target result persistence:
- Database-style result records (in-memory repository)
- File exports: CSV, JSON, Parquet, HTML, Excel
- Download support per stored format
- Retention policy execution
- Automatic archival for expired results

`ReportService` provides report generation and delivery:
- output formats: HTML, PDF, Excel, CSV, JSON
- report types: Executive Summary, Detailed Report, Comparison Report, Trend Report
- email report outbox queue for configured recipients
- report download support per generated format

## Execution
`YamlWorkflowExecutor` orchestrates:
- Source/target data extraction from YAML inline rows.
- Filter and transformation application.
- SQL/Spark SQL plan construction.
- SQL transformation compilation:
	- Source SQL and Target SQL
	- Views and Temporary Tables as pre-SQL setup statements
	- CTE injection into source/target SQL
	- Stored Procedure invocation via explicit `call_sql` or generated `CALL proc(...)`
	- Parameterized query rendering using `:param` or `{{param}}` placeholders
- Engine execution via ExecutionService.
- Great Expectations integration:
	- auto-generate expectation suites (`great_expectations.auto_generate`)
	- allow editing via `great_expectations.editable_expectations`
	- run expectation suites using `validation.great_expectations`
	- store run results and suite versions in in-memory expectation repository
- Anomaly detection integration:
	- run `validation.isolation_forest` using configurable detector model (`anomaly_detection.model`)
	- generate chart-ready anomaly visualizations in `anomaly_visualizations`
	- pass detector tuning options using `anomaly_detection.options`
- Result storage integration:
	- store execution outcomes in database and selected file formats using `result_storage.formats`
	- enable artifact download with `result_storage.allow_download`
	- enforce retention and archive behavior using `result_storage.retention_days` and `result_storage.archive_enabled`
- Reporting integration:
	- generate reports using `reporting.formats` and `reporting.report_types`
	- queue email report notifications with `reporting.email_recipients`
	- include report artifacts metadata under `reports` in workflow output
- Automatic dataset profiling for transformed source and target datasets:
	- schema
	- null %
	- uniqueness
	- min/max
	- averages
	- histograms
	- top values
	- cardinality
	- distributions
- HTML profile report generation at `<output_location.path>/<workflow_id>_profile_report.html`.
- Validation execution via ValidationService after transformation output is produced.
- Scheduling and output-location metadata propagation in result payload.

`YamlWorkflowService` also provides scheduler orchestration APIs for submit, dispatch, pause, resume, cancel, history, and notifications.

## Notes
- This module establishes YAML orchestration and schema controls.
- For scheduler lifecycle semantics and queue orchestration details, see `docs/SCHEDULER_ORCHESTRATION.md`.
