# Universal Connector Framework

## Overview
This module introduces a plugin-based connector framework for the tkk-UniversalValidator backend.

## Architecture Components
- Plugin SDK: connector contracts, spec metadata, capabilities, and typed results.
- Connector Base Classes: abstract interface for all connector operations.
- Connector Registry: in-memory registration and lookup for connector plugins.
- Connector Loader: discovery from packages, file paths, and Python entry points.
- Connector Factory: creation and plugin discovery façade.
- Pipeline Runner: parallel execution, dependency ordering, and retry control.

## Supported Connector Categories and Providers
### Files
CSV, TSV, TXT, Excel, JSON, XML, Parquet, Avro, ORC, Feather, Arrow, Delta, Iceberg, Hudi, Tableau Hyper, Tableau TWB, Tableau TWBX, Power BI exports

### Databases
Oracle, SQL Server, PostgreSQL, MySQL, MariaDB, SQLite, Snowflake, Redshift, Databricks SQL, BigQuery, Hive, Impala, ClickHouse, DuckDB, DB2, Teradata, Vertica

### Cloud Storage
Amazon S3, Azure Blob, Azure Data Lake, Google Cloud Storage, Databricks Volumes, SharePoint, OneDrive, Google Drive, FTP, SFTP, NAS

### Big Data
Spark, Hive, Delta Lake, Iceberg, Hudi, Kafka

### APIs
REST, SOAP, GraphQL, OpenAPI, JSON API

## Capability Contract
Every connector plugin exposes the complete operation surface:
- Connection Test
- Authentication
- Metadata Discovery
- Schema Discovery
- Primary Key Discovery
- Sample Data
- Pagination
- Streaming
- Incremental Read
- Pushdown Filters
- Parallel Read
- Connection Pooling
- Retry Logic
- Timeout
- Error Handling
- Metrics
- Logging

## Pipeline Features
The pipeline runner supports:
- Parallel task execution with bounded concurrency
- Configurable task pipelines
- Pipeline templates
- Dependency ordering
- Per-task retries
- Plugin-based connector invocation

## Notes
- This milestone builds connector framework and SDK only.
- Validation logic is intentionally excluded.
