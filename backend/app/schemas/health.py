from pydantic import BaseModel


class ComponentStatus(BaseModel):
    initialized: bool
    healthy: bool
    required: bool
    detail: str | None = None


class HealthPayload(BaseModel):
    status: str
    service: str
    version: str


class ReadinessPayload(BaseModel):
    status: str
    database: ComponentStatus
    redis: ComponentStatus
    celery: ComponentStatus
