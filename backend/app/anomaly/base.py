from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AnomalyDetectionResult:
    model: str
    success: bool
    anomaly_count: int
    total_rows: int
    anomaly_indices: list[int] = field(default_factory=list)
    anomaly_scores: list[float] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    visualizations: dict[str, Any] = field(default_factory=dict)


class BaseAnomalyDetector(ABC):
    model_name: str

    @abstractmethod
    def detect(
        self,
        rows: list[dict[str, Any]],
        feature_columns: list[str],
        config: dict[str, Any] | None = None,
    ) -> AnomalyDetectionResult:
        raise NotImplementedError
