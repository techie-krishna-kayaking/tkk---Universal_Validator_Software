from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class ScheduledJobRecord:
    job_id: str
    workflow_id: str
    config_payload: dict[str, Any]
    schedule_mode: str
    priority: int
    max_retries: int
    retries_attempted: int
    concurrency_key: str
    queue_name: str
    status: str
    created_at: datetime
    updated_at: datetime
    next_run_at: datetime | None = None
    cron: str | None = None
    run_at: datetime | None = None
    interval_seconds: int | None = None
    paused: bool = False
    canceled: bool = False


@dataclass
class JobHistoryEvent:
    event_id: str
    job_id: str
    status: str
    message: str
    timestamp: datetime
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class JobNotificationEvent:
    notification_id: str
    job_id: str
    channel: str
    message: str
    timestamp: datetime
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class InMemorySchedulerRepository:
    jobs: dict[str, ScheduledJobRecord] = field(default_factory=dict)
    history: list[JobHistoryEvent] = field(default_factory=list)
    notifications: list[JobNotificationEvent] = field(default_factory=list)

    def add_job(self, job: ScheduledJobRecord) -> ScheduledJobRecord:
        self.jobs[job.job_id] = job
        return job

    def get_job(self, job_id: str) -> ScheduledJobRecord | None:
        return self.jobs.get(job_id)

    def list_jobs(self) -> list[ScheduledJobRecord]:
        return list(self.jobs.values())

    def update_job(self, job: ScheduledJobRecord) -> ScheduledJobRecord:
        job.updated_at = datetime.now(UTC)
        self.jobs[job.job_id] = job
        return job

    def add_history(self, event: JobHistoryEvent) -> None:
        self.history.append(event)

    def list_history(self, job_id: str | None = None) -> list[JobHistoryEvent]:
        if job_id is None:
            return list(self.history)
        return [item for item in self.history if item.job_id == job_id]

    def add_notification(self, event: JobNotificationEvent) -> None:
        self.notifications.append(event)

    def list_notifications(self, job_id: str | None = None) -> list[JobNotificationEvent]:
        if job_id is None:
            return list(self.notifications)
        return [item for item in self.notifications if item.job_id == job_id]
