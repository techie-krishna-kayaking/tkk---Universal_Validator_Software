# Scheduler and Job Orchestration

## Overview
The scheduler subsystem provides in-memory job orchestration for YAML workflows with support for one-time, recurring, and cron execution models.

## Features
- Schedule modes:
  - `immediate`
  - `once` / `one_time`
  - `recurring`
  - `cron`
- Queueing and priority ordering
- Retry handling with exponential backoff
- Concurrency controls:
  - global `max_concurrency` in `SchedulerService`
  - per-workflow serialization via `concurrency_key`
- Job controls:
  - pause
  - resume
  - cancel
- History tracking for state transitions
- Notification outbox events for lifecycle states

## Scheduling Fields
Add these under `scheduling` in workflow YAML:
- `mode`
- `cron`
- `run_at`
- `interval_seconds`
- `max_retries`
- `priority`
- `queue`
- `concurrency_key`
- `notification_channel`

## Service Integration
`YamlWorkflowService` now exposes:
- `submit_scheduled_job(config, auto_process=True)`
- `dispatch_scheduled_jobs(queue_name=None)`
- `pause_scheduled_job(job_id)`
- `resume_scheduled_job(job_id)`
- `cancel_scheduled_job(job_id)`
- `list_scheduled_jobs()`
- `list_schedule_history(job_id=None)`
- `list_schedule_notifications(job_id=None)`

## Notes
- This scheduler is intentionally in-memory for deterministic testability.
- Persistence and distributed workers can be layered in without changing the public service interface.
