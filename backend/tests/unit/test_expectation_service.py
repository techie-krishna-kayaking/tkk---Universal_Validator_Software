from app.services.expectation_service import ExpectationService


def _rows() -> list[dict]:
    return [
        {"id": 1, "amount": 10.0, "status": "active"},
        {"id": 2, "amount": 20.0, "status": "active"},
    ]


def test_expectation_suite_auto_generation_and_versioning() -> None:
    service = ExpectationService()

    suite = service.generate_suite(suite_id="suite-a", rows=_rows(), primary_keys=["id"])
    assert suite["version"] == "1.0.0"
    assert len(suite["expectations"]) > 0

    edited = service.edit_suite(
        suite_id="suite-a",
        expectations=[
            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "id"},
            }
        ],
    )
    assert edited["version"] == "1.0.1"
    assert service.list_suite_versions("suite-a") == ["1.0.0", "1.0.1"]


def test_expectation_suite_run_and_result_storage() -> None:
    service = ExpectationService()
    service.generate_suite(suite_id="suite-run", rows=_rows(), primary_keys=["id"])

    run = service.run_suite(suite_id="suite-run", rows=_rows())
    assert run["success"] is True
    assert run["suite_version"] == "1.0.0"
    assert run["success_count"] >= 1

    stored = service.list_run_results("suite-run")
    assert len(stored) == 1
    assert stored[0]["suite_version"] == "1.0.0"


def test_expectation_suite_run_with_editable_expectations() -> None:
    service = ExpectationService()

    run = service.run_suite(
        suite_id="suite-edit",
        rows=_rows(),
        expectations=[
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "amount", "min_value": 0, "max_value": 30},
            }
        ],
    )

    assert run["success"] is True
    assert run["suite_version"] == "1.0.0"
    assert service.list_suite_versions("suite-edit") == ["1.0.0"]
