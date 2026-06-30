from datetime import UTC, datetime

from app.services.scheduler_service import SchedulerService


def test_scheduler_priority_and_queue_dispatch_order() -> None:
    service = SchedulerService(max_concurrency=5)

    first = service.schedule_job(
        workflow_id="wf-low",
        config_payload={"workflow_id": "wf-low"},
        scheduling={"mode": "immediate", "priority": 200, "queue": "default"},
    )
    second = service.schedule_job(
        workflow_id="wf-high",
        config_payload={"workflow_id": "wf-high"},
        scheduling={"mode": "immediate", "priority": 10, "queue": "default"},
    )

    order: list[str] = []

    def _runner(payload: dict) -> dict:
        order.append(payload["workflow_id"])
        return {"success": True}

    stats = service.process_queue(_runner, queue_name="default")

    assert stats["completed"] == 2
    assert first["job_id"] != second["job_id"]
    assert order == ["wf-high", "wf-low"]


def test_scheduler_retry_transitions_to_retry_state() -> None:
    service = SchedulerService(max_concurrency=2)
    job = service.schedule_job(
        workflow_id="wf-retry",
        config_payload={"workflow_id": "wf-retry"},
        scheduling={"mode": "immediate", "max_retries": 1, "priority": 1},
    )

    def _runner(_payload: dict) -> dict:
        raise RuntimeError("temporary failure")

    stats = service.process_queue(_runner)
    snapshot = [item for item in service.list_jobs() if item["job_id"] == job["job_id"]][0]

    assert stats["retried"] == 1
    assert snapshot["status"] == "retry"
    assert snapshot["retries_attempted"] == 1


def test_scheduler_pause_resume_and_cancel() -> None:
    service = SchedulerService(max_concurrency=2)
    created = service.schedule_job(
        workflow_id="wf-control",
        config_payload={"workflow_id": "wf-control"},
        scheduling={"mode": "immediate", "priority": 100},
    )

    paused = service.pause_job(created["job_id"])
    resumed = service.resume_job(created["job_id"])
    canceled = service.cancel_job(created["job_id"])

    assert paused["status"] == "paused"
    assert resumed["status"] == "queued"
    assert canceled["status"] == "canceled"


def test_scheduler_recurring_job_requeues_after_success() -> None:
    service = SchedulerService(max_concurrency=2)
    created = service.schedule_job(
        workflow_id="wf-recurring",
        config_payload={"workflow_id": "wf-recurring"},
        scheduling={"mode": "recurring", "interval_seconds": 1, "priority": 1},
    )

    job_record = service.repository.get_job(created["job_id"])
    assert job_record is not None
    job_record.next_run_at = datetime.now(UTC)
    service.repository.update_job(job_record)

    stats = service.process_queue(lambda _payload: {"success": True})
    snapshot = [item for item in service.list_jobs() if item["job_id"] == created["job_id"]][0]

    assert stats["completed"] == 1
    assert snapshot["status"] == "queued"
    assert snapshot["next_run_at"] is not None


def test_scheduler_records_notifications_and_history() -> None:
    service = SchedulerService(max_concurrency=2)
    created = service.schedule_job(
        workflow_id="wf-observe",
        config_payload={"workflow_id": "wf-observe"},
        scheduling={"mode": "immediate", "notification_channel": "email"},
    )

    service.process_queue(lambda _payload: {"success": True})

    history = service.get_history(created["job_id"])
    notifications = service.get_notifications(created["job_id"])

    assert len(history) >= 3
    assert history[0]["status"] == "queued"
    assert len(notifications) >= 3
    assert notifications[0]["channel"] == "email"
