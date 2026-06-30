# Universal Validation Framework

## Overview
This module implements a plugin-based validation engine where each validation rule is a plugin implementing a common validator interface.

## Architecture
- Validator SDK: typed validation specs, context, and result contracts.
- Base Validator: common abstract class for all validators.
- Validator Registry: plugin registration and lookup.
- Validator Loader: plugin discovery from packages, file paths, and entry points.
- Validator Factory: default validator registration plus plugin discovery orchestrator.
- Validation Pipeline Runner: parallel execution, dependency ordering, retries, and templates.

## Supported Validators
- Record Count
- Column Count
- Metadata Validation
- Duplicate Detection
- Null Analysis
- Empty String Detection
- Data Comparison
- Column Order
- Precision
- Scale
- Length
- Distinct Count
- Date Range
- Case Sensitivity
- Leading Zeros
- Special Characters
- Row Checksum
- Symmetric Difference
- Great Expectations
- Isolation Forest
- Custom SQL Validators
- Custom Python Validators
- Custom Spark Validators

## Pipeline Features
- Parallel execution with configurable worker limits.
- Configurable validation task pipelines.
- Validation template execution.
- Dependency ordering between validation tasks.
- Per-task retries.
- Plugin discovery and runtime loading.

## Notes
- This milestone provides validation framework and plugin SDK.
- No external execution engine integration is required yet.
