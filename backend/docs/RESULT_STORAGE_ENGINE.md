# Result Storage Engine

## Overview
The Result Storage Engine persists workflow outputs to both database-style records and downloadable files.

## Supported Targets
- Database (in-memory repository)
- CSV
- JSON
- Parquet
- HTML
- Excel

## Download Support
`ResultStorageService.download_result(result_id, format_name)` returns byte content and filename metadata for the requested stored format.

## Retention Policy
- Configurable `retention_days`
- Expired records can be archived or deleted

## Archiving
- Controlled by `archive_enabled`
- Artifacts are moved into configured `archive_path`
- Record metadata is updated with archive state and timestamp

## Workflow Integration
`YamlWorkflowExecutor` automatically invokes `ResultStorageService.store_result(...)` at the end of every workflow run.
The result payload includes `result_storage` metadata:
- `result_id`
- `stored_in_database`
- `formats`
- `artifacts`
- `warnings`
- retention and archive settings

## Notes
Parquet and Excel exports require compatible runtime dependencies. If unavailable, the engine reports a warning and continues without failing the workflow.
