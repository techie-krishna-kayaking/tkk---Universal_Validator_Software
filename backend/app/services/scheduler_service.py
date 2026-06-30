from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import Any, Callable
from uuid import uuid4

from app.repositories.scheduler_repository import (
    InMemorySchedulerRepository,
    JobHistoryEvent,
    JobNotificationEvent,
    ScheduledJobRecord,
)


class SchedulerService:
    def __init__(
        self,
        repository: InMemorySchedulerRepository | None = None,
        max_concurrency: int = 3,
    ) -> None:
        self.repository = repository or InMemorySchedulerRepository()
        self.max_concurrency = max(1, max_concurrency)

    def schedule_job(self, workflow_id: str, config_payload: dict[str, Any], scheduling: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(UTC)
        mode = self._normalize_mode(str(scheduling.get("mode", "immediate")))
        run_at = self._parse_datetime(scheduling.get("run_at"))
        cron = scheduling.get("cron")
        interval_seconds = scheduling.get("interval_seconds")

        next_run_at = self._compute_next_run(
            mode=mode,
            now=now,
            run_at=run_at,
            cron=cron,
            interval_seconds=interval_seconds,
        )

        job = ScheduledJobRecord(
            job_id=str(uuid4()),
            workflow_id=workflow_id,
            config_payload=config_payload,
            schedule_mode=mode,
            priority=int(scheduling.get("priority", 100)),
            max_retries=int(scheduling.get("max_retries", 0)),
            retries_attempted=0,
            concurrency_key=str(scheduling.get("concurrency_key", workflow_id)),
            queue_name=str(scheduling.get("queue", "default")),
            status="queued",
            created_at=now,
            updated_at=now,
            next_run_at=next_run_at,
            cron=cron,
            run_at=run_at,
            interval_seconds=interval_seconds,
            paused=False,
            canceled=False,
        )
        self.repository.add_job(job)
        self._add_history(job.job_id, "queued", "job_scheduled", {"next_run_at": str(next_run_at), "mode": mode})
        self._notify(job, "queued", f"Job queued for workflow {workflow_id}", channel=scheduling.get("notification_channel", "system"))

        return {
            "job_id": job.job_id,
            "workflow_id": job.workflow_id,
            "status": job.status,
            "next_run_at": job.next_run_at.isoformat() if job.next_run_at else None,
            "mode": job.schedule_mode,
        }

    def process_queue(
        self,
        execute_job: Callable[[dict[str, Any]], dict[str, Any]],
        queue_name: str | None = None,
    ) -> dict[str, int]:
        now = datetime.now(UTC)
        queued = [
            job
            for job in self.repository.list_jobs()
            if job.status in ("queued", "retry")
            and not job.paused
            and not job.canceled
            and self._is_due(job, now)
            and (queue_name is None or job.queue_name == queue_name)
        ]
        queued.sort(key=lambda item: (item.priority, item.created_at))

        running_by_key: dict[str, int] = defaultdict(int)
        completed = 0
        failed = 0
        retried = 0

        for job in queued:
            if sum(running_by_key.values()) >= self.max_concurrency:
                break
            if running_by_key[job.concurrency_key] >= 1:
                continue

            running_by_key[job.concurrency_key] += 1
            job.status = "running"
            self.repository.update_job(job)
            self._add_history(job.job_id, "running", "job_started", {})
            self._notify(job, "running", f"Job started for workflow {job.workflow_id}")

            try:
                payload = execute_job(job.config_payload)
                job.status = "succeeded"
                self.repository.update_job(job)
                completed += 1
                self._add_history(job.job_id, "succeeded", "job_completed", {"success": payload.get("success")})
                self._notify(job, "succeeded", f"Job completed for workflow {job.workflow_id}", payload=payload)
                self._schedule_next(job)
            except Exception as exc:  # pragma: no cover
                if job.retries_attempted < job.max_retries:
                    job.retries_attempted += 1
                    job.status = "retry"
                    job.next_run_at = datetime.now(UTC) + timedelta(seconds=self._retry_delay(job.retries_attempted))
                    self.repository.update_job(job)
                    retried += 1
                    self._add_history(
                        job.job_id,
                        "retry",
                        "job_retry_scheduled",
                        {"error": str(exc), "retry_attempt": job.retries_attempted},
                    )
                    self._notify(job, "retry", f"Job retry scheduled for workflow {job.workflow_id}")
                else:
                    job.status = "failed"
                    self.repository.update_job(job)
                    failed += 1
                    self._add_history(job.job_id, "failed", "job_failed", {"error": str(exc)})
                    self._notify(job, "failed", f"Job failed for workflow {job.workflow_id}", payload={"error": str(exc)})
            finally:
                running_by_key[job.concurrency_key] = max(0, running_by_key[job.concurrency_key] - 1)

        return {"completed": completed, "failed": failed, "retried": retried}

    def pause_job(self, job_id: str) -> dict[str, Any]:
        job = self._require_job(job_id)
        job.paused = True
        job.status = "paused"
        self.repository.update_job(job)
        self._add_history(job_id, "paused", "job_paused", {})
        self._notify(job, "paused", f"Job paused for workflow {job.workflow_id}")
        return {"job_id": job_id, "status": job.status}

    def resume_job(self, job_id: str) -> dict[str, Any]:
        job = self._require_job(job_id)
        job.paused = False
        if not job.canceled and job.status in ("paused", "canceled"):
            job.status = "queued"
        if job.next_run_at is None:
            job.next_run_at = datetime.now(UTC)
        self.repository.update_job(job)
        self._add_history(job_id, "queued", "job_resumed", {})
        self._notify(job, "queued", f"Job resumed for workflow {job.workflow_id}")
        return {"job_id": job_id, "status": job.status}

    def cancel_job(self, job_id: str) -> dict[str, Any]:
        job = self._require_job(job_id)
        job.canceled = True
        job.status = "canceled"
        self.repository.update_job(job)
        self._add_history(job_id, "canceled", "job_canceled", {})
        self._notify(job, "canceled", f"Job canceled for workflow {job.workflow_id}")
        return {"job_id": job_id, "status": job.status}

    def list_jobs(self) -> list[dict[str, Any]]:
        return [
            {
                "job_id": job.job_id,
                "workflow_id": job.workflow_id,
                "mode": job.schedule_mode,
                "priority": job.priority,
                "status": job.status,
                "next_run_at": job.next_run_at.isoformat() if job.next_run_at else None,
                "paused": job.paused,
                "canceled": job.canceled,
                "retries_attempted": job.retries_attempted,
                "max_retries": job.max_retries,
            }
            for job in self.repository.list_jobs()
        ]

    def get_history(self, job_id: str | None = None) -> list[dict[str, Any]]:
        return [
            {
                "event_id": item.event_id,
                "job_id": item.job_id,
                "status": item.status,
                "message": item.message,
                "timestamp": item.timestamp.isoformat(),
                "details": item.details,
            }
            for item in self.repository.list_history(job_id)
        ]

    def get_notifications(self, job_id: str | None = None) -> list[dict[str, Any]]:
        return [
            {
                "notification_id": item.notification_id,
                "job_id": item.job_id,
                "channel": item.channel,
                "message": item.message,
                "timestamp": item.timestamp.isoformat(),
                "payload": item.payload,
            }
            for item in self.repository.list_notifications(job_id)
        ]

    def _schedule_next(self, job: ScheduledJobRecord) -> None:
        if job.canceled:
            return
        now = datetime.now(UTC)
        if job.schedule_mode == "cron":
            job.status = "queued"
            job.next_run_at = self._next_cron_time(job.cron or "* * * * *", now)
            self.repository.update_job(job)
            self._add_history(job.job_id, "queued", "next_cron_run_scheduled", {"next_run_at": job.next_run_at.isoformat()})
            return
        if job.schedule_mode == "recurring":
            step = max(1, int(job.interval_seconds or 60))
            job.status = "queued"
            job.next_run_at = now + timedelta(seconds=step)
            self.repository.update_job(job)
            self._add_history(job.job_id, "queued", "next_recurring_run_scheduled", {"next_run_at": job.next_run_at.isoformat()})
            return
        if job.schedule_mode in ("once", "one_time", "immediate"):
            # terminal after single run
            return

    def _compute_next_run(
        self,
        mode: str,
        now: datetime,
        run_at: datetime | None,
        cron: str | None,
        interval_seconds: int | None,
    ) -> datetime:
        mode_lower = (mode or "immediate").lower()
        if mode_lower == "cron":
            return self._next_cron_time(cron or "* * * * *", now)
        if mode_lower in ("once", "one_time"):
            return run_at or now
        if mode_lower == "recurring":
            step = max(1, int(interval_seconds or 60))
            return now + timedelta(seconds=step)
        return now

    def _normalize_mode(self, mode: str) -> str:
        lowered = mode.lower().strip()
        if lowered in ("one-time", "one_time"):
            return "one_time"
        return lowered

    def _next_cron_time(self, expression: str, now: datetime) -> datetime:
        fields = expression.split()
        if len(fields) != 5:
            return now + timedelta(minutes=1)

        minute_expr, hour_expr, _, _, _ = fields
        cursor = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        for _ in range(60 * 24 * 31):
            if self._match_field(cursor.minute, minute_expr) and self._match_field(cursor.hour, hour_expr):
                return cursor
            cursor += timedelta(minutes=1)
        return now + timedelta(minutes=1)

    def _match_field(self, value: int, expression: str) -> bool:
        if expression == "*":
            return True
        if expression.startswith("*/"):
            try:
                step = int(expression[2:])
            except ValueError:
                return False
            return step > 0 and value % step == 0
        try:
            return value == int(expression)
        except ValueError:
            return False

    def _retry_delay(self, attempt: int) -> int:
        return min(300, 2 ** max(0, attempt))

    def _is_due(self, job: ScheduledJobRecord, now: datetime) -> bool:
        if job.next_run_at is None:
            return True
        return job.next_run_at <= now

    def _add_history(self, job_id: str, status: str, message: str, details: dict[str, Any]) -> None:
        self.repository.add_history(
            JobHistoryEvent(
                event_id=str(uuid4()),
                job_id=job_id,
                status=status,
                message=message,
                timestamp=datetime.now(UTC),
                details=details,
            )
        )

    def _notify(self, job: ScheduledJobRecord, status: str, message: str, channel: str | None = None, payload: dict[str, Any] | None = None) -> None:
        self.repository.add_notification(
            JobNotificationEvent(
                notification_id=str(uuid4()),
                job_id=job.job_id,
                channel=channel or "system",
                message=message,
                timestamp=datetime.now(UTC),
                payload={"status": status, **(payload or {})},
            )
        )

    def _parse_datetime(self, value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=UTC)
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return None
            try:
                parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
                return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
            except ValueError:
                return None
        return None

    def _require_job(self, job_id: str) -> ScheduledJobRecord:
        job = self.repository.get_job(job_id)
        if job is None:
            raise ValueError("job_not_found")
        return job
