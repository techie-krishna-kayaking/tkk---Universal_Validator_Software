from pathlib import Path

from app.services.scheduler_service import SchedulerService
from app.services.expectation_service import ExpectationService
from app.services.report_service import ReportService
from app.services.result_storage_service import ResultStorageService
from app.repositories.yaml_workflow_repository import InMemoryYamlWorkflowRepository
from app.workflows.yaml_executor import YamlWorkflowExecutor
from app.workflows.yaml_schema import WorkflowConfig, YamlWorkflowLoader
from app.workflows.yaml_templates import YamlTemplateService
from app.workflows.yaml_versioning import WorkflowVersionService


class YamlWorkflowService:
    def __init__(self, repository: InMemoryYamlWorkflowRepository | None = None) -> None:
        self.repository = repository or InMemoryYamlWorkflowRepository()
        self.versioning = WorkflowVersionService(self.repository)
        self.expectations = ExpectationService()
        self.result_storage = ResultStorageService()
        self.reports = ReportService()
        self.scheduler = SchedulerService()
        self.executor = YamlWorkflowExecutor(
            expectation_service=self.expectations,
            result_storage_service=self.result_storage,
            report_service=self.reports,
        )
        self.templates = YamlTemplateService()

    def load_from_file(self, path: str | Path) -> WorkflowConfig:
        return YamlWorkflowLoader.from_file(path)

    def validate_schema(self, payload: dict) -> WorkflowConfig:
        return YamlWorkflowLoader.from_dict(payload)

    def autocomplete_template(self, partial: dict, available_validations: list[str] | None = None) -> dict:
        return self.templates.autocomplete(partial, available_validations=available_validations)

    def save_versioned(self, config: WorkflowConfig) -> str:
        return self.versioning.save(config)

    def list_versions(self, workflow_id: str) -> list[str]:
        return self.versioning.list_versions(workflow_id)

    def execute(self, config: WorkflowConfig) -> dict:
        return self.executor.execute(config)

    def submit_scheduled_job(self, config: WorkflowConfig, auto_process: bool = True) -> dict:
        job = self.scheduler.schedule_job(
            workflow_id=config.workflow_id,
            config_payload=config.model_dump(mode="python"),
            scheduling=config.scheduling.model_dump(),
        )
        if auto_process:
            self.dispatch_scheduled_jobs()
        return job

    def dispatch_scheduled_jobs(self, queue_name: str | None = None) -> dict:
        return self.scheduler.process_queue(execute_job=self._execute_job_payload, queue_name=queue_name)

    def pause_scheduled_job(self, job_id: str) -> dict:
        return self.scheduler.pause_job(job_id)

    def resume_scheduled_job(self, job_id: str) -> dict:
        return self.scheduler.resume_job(job_id)

    def cancel_scheduled_job(self, job_id: str) -> dict:
        return self.scheduler.cancel_job(job_id)

    def list_scheduled_jobs(self) -> list[dict]:
        return self.scheduler.list_jobs()

    def list_schedule_history(self, job_id: str | None = None) -> list[dict]:
        return self.scheduler.get_history(job_id)

    def list_schedule_notifications(self, job_id: str | None = None) -> list[dict]:
        return self.scheduler.get_notifications(job_id)

    def generate_expectation_suite(self, suite_id: str, rows: list[dict], primary_keys: list[str] | None = None) -> dict:
        return self.expectations.generate_suite(suite_id=suite_id, rows=rows, primary_keys=primary_keys)

    def edit_expectation_suite(self, suite_id: str, expectations: list[dict], requested_version: str | None = None) -> dict:
        return self.expectations.edit_suite(
            suite_id=suite_id,
            expectations=expectations,
            requested_version=requested_version,
        )

    def run_expectation_suite(
        self,
        suite_id: str,
        rows: list[dict],
        expectations: list[dict] | None = None,
        auto_generate: bool = False,
        primary_keys: list[str] | None = None,
    ) -> dict:
        return self.expectations.run_suite(
            suite_id=suite_id,
            rows=rows,
            expectations=expectations,
            auto_generate=auto_generate,
            primary_keys=primary_keys,
        )

    def list_expectation_versions(self, suite_id: str) -> list[str]:
        return self.expectations.list_suite_versions(suite_id)

    def list_expectation_results(self, suite_id: str) -> list[dict]:
        return self.expectations.list_run_results(suite_id)

    def download_result(self, result_id: str, format_name: str) -> dict:
        return self.result_storage.download_result(result_id=result_id, format_name=format_name)

    def apply_result_retention_policy(self, retention_days: int, archive_enabled: bool, archive_dir: str) -> dict:
        return self.result_storage.apply_retention_policy(
            retention_days=retention_days,
            archive_enabled=archive_enabled,
            archive_dir=archive_dir,
        )

    def download_report(self, report_id: str, format_name: str) -> dict:
        return self.reports.download_report(report_id=report_id, format_name=format_name)

    def _execute_job_payload(self, config_payload: dict) -> dict:
        config = WorkflowConfig.model_validate(config_payload)
        return self.execute(config)
