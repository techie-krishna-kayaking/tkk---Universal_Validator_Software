from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class ReportRecord:
    report_id: str
    workflow_id: str
    result_id: str
    created_at: datetime
    payload: dict[str, Any]
    artifacts: dict[str, str] = field(default_factory=dict)


@dataclass
class EmailReportEvent:
    event_id: str
    workflow_id: str
    report_id: str
    recipients: list[str]
    subject: str
    body: str
    created_at: datetime


@dataclass
class InMemoryReportRepository:
    reports: dict[str, ReportRecord] = field(default_factory=dict)
    email_outbox: list[EmailReportEvent] = field(default_factory=list)

    def add_report(self, report: ReportRecord) -> ReportRecord:
        self.reports[report.report_id] = report
        return report

    def get_report(self, report_id: str) -> ReportRecord | None:
        return self.reports.get(report_id)

    def list_by_workflow(self, workflow_id: str) -> list[ReportRecord]:
        return [record for record in self.reports.values() if record.workflow_id == workflow_id]

    def queue_email(self, event: EmailReportEvent) -> None:
        self.email_outbox.append(event)
