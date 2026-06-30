from typing import Any

from app.anomaly.base import AnomalyDetectionResult, BaseAnomalyDetector
from app.anomaly.detectors import (
    AutoencoderDetector,
    IsolationForestDetector,
    OneClassSVMDetector,
    ProphetDetector,
    SeasonalDetector,
)


class AnomalyDetectionService:
    def __init__(self, detectors: dict[str, BaseAnomalyDetector] | None = None) -> None:
        self.detectors = detectors or {
            "isolation_forest": IsolationForestDetector(),
            "one_class_svm": OneClassSVMDetector(),
            "autoencoder": AutoencoderDetector(),
            "prophet": ProphetDetector(),
            "seasonal_detection": SeasonalDetector(),
        }

    def list_models(self) -> list[str]:
        return sorted(self.detectors.keys())

    def detect(
        self,
        rows: list[dict[str, Any]],
        feature_columns: list[str],
        model: str = "isolation_forest",
        config: dict[str, Any] | None = None,
    ) -> AnomalyDetectionResult:
        detector = self.detectors.get(model)
        if detector is None:
            return AnomalyDetectionResult(
                model=model,
                success=False,
                anomaly_count=0,
                total_rows=len(rows),
                warnings=["unsupported_model"],
                visualizations={"scatter": {"points": []}, "score_histogram": []},
            )
        return detector.detect(rows=rows, feature_columns=feature_columns, config=config)
