from app.anomaly.service import AnomalyDetectionService


def test_isolation_forest_detection_returns_visualizations() -> None:
    service = AnomalyDetectionService()
    rows = [
        {"x": 1.0, "y": 1.0},
        {"x": 1.2, "y": 1.1},
        {"x": 0.9, "y": 1.0},
        {"x": 10.0, "y": 10.0},
    ]

    result = service.detect(rows=rows, feature_columns=["x", "y"], model="isolation_forest")

    assert result.model == "isolation_forest"
    assert result.total_rows == 4
    assert "scatter" in result.visualizations
    assert "score_histogram" in result.visualizations


def test_future_model_interfaces_are_available() -> None:
    service = AnomalyDetectionService()
    rows = [{"x": 1.0}]

    one_class = service.detect(rows=rows, feature_columns=["x"], model="one_class_svm")
    autoencoder = service.detect(rows=rows, feature_columns=["x"], model="autoencoder")
    prophet = service.detect(rows=rows, feature_columns=["x"], model="prophet")
    seasonal = service.detect(rows=rows, feature_columns=["x"], model="seasonal_detection")

    assert one_class.success is True
    assert autoencoder.success is True
    assert prophet.success is True
    assert seasonal.success is True
    assert "model_not_implemented_yet" in one_class.warnings
    assert "model_not_implemented_yet" in autoencoder.warnings
    assert "model_not_implemented_yet" in prophet.warnings
    assert "model_not_implemented_yet" in seasonal.warnings
