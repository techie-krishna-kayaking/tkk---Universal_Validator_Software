from __future__ import annotations

from statistics import mean, pstdev
from typing import Any

from app.anomaly.base import AnomalyDetectionResult, BaseAnomalyDetector


class IsolationForestDetector(BaseAnomalyDetector):
    model_name = "isolation_forest"

    def detect(
        self,
        rows: list[dict[str, Any]],
        feature_columns: list[str],
        config: dict[str, Any] | None = None,
    ) -> AnomalyDetectionResult:
        config = config or {}
        matrix = _build_matrix(rows, feature_columns)
        if not matrix:
            return AnomalyDetectionResult(
                model=self.model_name,
                success=True,
                anomaly_count=0,
                total_rows=len(rows),
                warnings=["no_numeric_data"],
                visualizations=_build_visualizations(rows, feature_columns, [], []),
            )

        try:
            from sklearn.ensemble import IsolationForest  # type: ignore

            model = IsolationForest(
                random_state=int(config.get("random_state", 42)),
                contamination=config.get("contamination", "auto"),
            )
            predictions = model.fit_predict(matrix)
            scores = list((-model.score_samples(matrix)).tolist())
            anomaly_indices = [idx for idx, pred in enumerate(predictions) if pred == -1]
            return AnomalyDetectionResult(
                model=self.model_name,
                success=len(anomaly_indices) == 0,
                anomaly_count=len(anomaly_indices),
                total_rows=len(rows),
                anomaly_indices=anomaly_indices,
                anomaly_scores=scores,
                visualizations=_build_visualizations(rows, feature_columns, anomaly_indices, scores),
            )
        except ImportError:
            # Lightweight fallback keeps behavior available in minimal environments.
            anomaly_indices, scores = _zscore_anomalies(matrix, threshold=float(config.get("zscore_threshold", 3.0)))
            return AnomalyDetectionResult(
                model=self.model_name,
                success=len(anomaly_indices) == 0,
                anomaly_count=len(anomaly_indices),
                total_rows=len(rows),
                anomaly_indices=anomaly_indices,
                anomaly_scores=scores,
                warnings=["sklearn_not_installed_using_zscore_fallback"],
                visualizations=_build_visualizations(rows, feature_columns, anomaly_indices, scores),
            )


class OneClassSVMDetector(BaseAnomalyDetector):
    model_name = "one_class_svm"

    def detect(self, rows: list[dict[str, Any]], feature_columns: list[str], config: dict[str, Any] | None = None) -> AnomalyDetectionResult:
        return AnomalyDetectionResult(
            model=self.model_name,
            success=True,
            anomaly_count=0,
            total_rows=len(rows),
            warnings=["model_not_implemented_yet"],
            visualizations=_build_visualizations(rows, feature_columns, [], []),
        )


class AutoencoderDetector(BaseAnomalyDetector):
    model_name = "autoencoder"

    def detect(self, rows: list[dict[str, Any]], feature_columns: list[str], config: dict[str, Any] | None = None) -> AnomalyDetectionResult:
        return AnomalyDetectionResult(
            model=self.model_name,
            success=True,
            anomaly_count=0,
            total_rows=len(rows),
            warnings=["model_not_implemented_yet"],
            visualizations=_build_visualizations(rows, feature_columns, [], []),
        )


class ProphetDetector(BaseAnomalyDetector):
    model_name = "prophet"

    def detect(self, rows: list[dict[str, Any]], feature_columns: list[str], config: dict[str, Any] | None = None) -> AnomalyDetectionResult:
        return AnomalyDetectionResult(
            model=self.model_name,
            success=True,
            anomaly_count=0,
            total_rows=len(rows),
            warnings=["model_not_implemented_yet"],
            visualizations=_build_visualizations(rows, feature_columns, [], []),
        )


class SeasonalDetector(BaseAnomalyDetector):
    model_name = "seasonal_detection"

    def detect(self, rows: list[dict[str, Any]], feature_columns: list[str], config: dict[str, Any] | None = None) -> AnomalyDetectionResult:
        return AnomalyDetectionResult(
            model=self.model_name,
            success=True,
            anomaly_count=0,
            total_rows=len(rows),
            warnings=["model_not_implemented_yet"],
            visualizations=_build_visualizations(rows, feature_columns, [], []),
        )


def _build_matrix(rows: list[dict[str, Any]], feature_columns: list[str]) -> list[list[float]]:
    matrix: list[list[float]] = []
    for row in rows:
        vector: list[float] = []
        for column in feature_columns:
            value = _to_float(row.get(column))
            vector.append(0.0 if value is None else value)
        if vector:
            matrix.append(vector)
    return matrix


def _to_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None
    return None


def _zscore_anomalies(matrix: list[list[float]], threshold: float = 3.0) -> tuple[list[int], list[float]]:
    if not matrix:
        return [], []

    columns = list(zip(*matrix))
    means = [mean(column) for column in columns]
    stds = [pstdev(column) or 1.0 for column in columns]

    anomaly_indices: list[int] = []
    scores: list[float] = []
    for idx, row in enumerate(matrix):
        row_score = 0.0
        for value, avg, std in zip(row, means, stds):
            row_score = max(row_score, abs((value - avg) / std))
        scores.append(row_score)
        if row_score >= threshold:
            anomaly_indices.append(idx)
    return anomaly_indices, scores


def _build_visualizations(
    rows: list[dict[str, Any]],
    feature_columns: list[str],
    anomaly_indices: list[int],
    scores: list[float],
) -> dict[str, Any]:
    highlighted = set(anomaly_indices)
    scatter_points = []
    x_key = feature_columns[0] if feature_columns else None
    y_key = feature_columns[1] if len(feature_columns) > 1 else x_key

    for idx, row in enumerate(rows):
        scatter_points.append(
            {
                "index": idx,
                "x": row.get(x_key) if x_key else idx,
                "y": row.get(y_key) if y_key else 0,
                "anomaly": idx in highlighted,
            }
        )

    histogram = []
    if scores:
        max_score = max(scores)
        bucket_count = 8
        if max_score <= 0:
            histogram = [{"bucket": "0", "count": len(scores)}]
        else:
            width = max_score / bucket_count
            counts = [0 for _ in range(bucket_count)]
            for score in scores:
                bucket = int(score / width) if width else 0
                if bucket >= bucket_count:
                    bucket = bucket_count - 1
                counts[bucket] += 1
            for idx, count in enumerate(counts):
                start = round(idx * width, 4)
                end = round((idx + 1) * width, 4)
                histogram.append({"bucket": f"{start}-{end}", "count": count})

    return {
        "scatter": {
            "x_axis": x_key or "row_index",
            "y_axis": y_key or "value",
            "points": scatter_points,
        },
        "score_histogram": histogram,
    }
