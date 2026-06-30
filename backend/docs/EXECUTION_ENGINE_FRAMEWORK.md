# Universal Data Execution Engine

## Overview
This module provides pluggable execution engines for:
- Pandas
- PySpark
- Polars
- DuckDB

It automatically selects the best engine using workload characteristics and supports fallback when an engine fails or is unavailable.

## Selection Inputs
- file size (bytes)
- row count
- available memory (MB)
- cluster availability
- user preference

## Selection Heuristics
- User preference takes highest priority when available.
- Large workloads with cluster availability prefer PySpark.
- SQL operations prefer DuckDB.
- Lower memory profiles prefer Polars and DuckDB.
- Medium to large workloads prioritize Polars/DuckDB before Pandas.

## Automatic Fallback
ExecutionOrchestrator tries engines in ranked order.
- On engine unavailability or execution failure, it falls back to the next candidate.
- Fallback can be disabled per profile.
- Failure chain is included in result details for observability.

## Public Components
- app/execution/sdk.py: data contracts for plans, profiles, and results.
- app/execution/base.py: abstract execution engine interface.
- app/execution/engines.py: concrete Pandas, PySpark, Polars, DuckDB adapters.
- app/execution/selector.py: engine ranking strategy.
- app/execution/orchestrator.py: selection + fallback orchestration.
- app/services/execution_service.py: service facade.
