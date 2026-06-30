from typing import Any


class ExpectationEngine:
    def auto_generate(self, rows: list[dict[str, Any]], primary_keys: list[str] | None = None) -> list[dict[str, Any]]:
        primary_keys = primary_keys or []
        columns = self._columns(rows)
        expectations: list[dict[str, Any]] = []

        expectations.append(
            {
                "expectation_type": "expect_table_row_count_to_be_between",
                "kwargs": {"min_value": 0, "max_value": max(0, len(rows))},
            }
        )

        for column in columns:
            expectations.append(
                {
                    "expectation_type": "expect_column_to_exist",
                    "kwargs": {"column": column},
                }
            )

            if all(row.get(column) is not None for row in rows):
                expectations.append(
                    {
                        "expectation_type": "expect_column_values_to_not_be_null",
                        "kwargs": {"column": column},
                    }
                )

            numeric_values = [self._to_float(row.get(column)) for row in rows if row.get(column) is not None]
            numeric_values = [value for value in numeric_values if value is not None]
            if numeric_values:
                expectations.append(
                    {
                        "expectation_type": "expect_column_values_to_be_between",
                        "kwargs": {
                            "column": column,
                            "min_value": min(numeric_values),
                            "max_value": max(numeric_values),
                        },
                    }
                )

            if column in primary_keys:
                expectations.append(
                    {
                        "expectation_type": "expect_column_values_to_be_unique",
                        "kwargs": {"column": column},
                    }
                )

        return expectations

    def run(self, rows: list[dict[str, Any]], expectations: list[dict[str, Any]]) -> dict[str, Any]:
        results: list[dict[str, Any]] = []

        for expectation in expectations:
            expectation_type = expectation.get("expectation_type")
            kwargs = expectation.get("kwargs", {})

            handler = getattr(self, f"_run_{expectation_type}", None)
            if handler is None:
                results.append(
                    {
                        "expectation_type": expectation_type,
                        "success": False,
                        "message": "unsupported_expectation",
                    }
                )
                continue

            ok, details = handler(rows, kwargs)
            results.append(
                {
                    "expectation_type": expectation_type,
                    "success": ok,
                    "kwargs": kwargs,
                    "details": details,
                }
            )

        success_count = sum(1 for item in results if item.get("success"))
        failure_count = len(results) - success_count

        return {
            "success": failure_count == 0,
            "success_count": success_count,
            "failure_count": failure_count,
            "results": results,
        }

    def _run_expect_table_row_count_to_be_between(self, rows: list[dict[str, Any]], kwargs: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        row_count = len(rows)
        min_value = kwargs.get("min_value")
        max_value = kwargs.get("max_value")
        ok = (min_value is None or row_count >= min_value) and (max_value is None or row_count <= max_value)
        return ok, {"row_count": row_count}

    def _run_expect_column_to_exist(self, rows: list[dict[str, Any]], kwargs: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        column = kwargs.get("column")
        columns = set(self._columns(rows))
        return bool(column in columns), {"columns": sorted(columns)}

    def _run_expect_column_values_to_not_be_null(self, rows: list[dict[str, Any]], kwargs: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        column = kwargs.get("column")
        null_count = sum(1 for row in rows if row.get(column) is None)
        return null_count == 0, {"null_count": null_count}

    def _run_expect_column_values_to_be_unique(self, rows: list[dict[str, Any]], kwargs: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        column = kwargs.get("column")
        seen: set[str] = set()
        duplicate_count = 0
        for row in rows:
            key = repr(row.get(column))
            if key in seen:
                duplicate_count += 1
            seen.add(key)
        return duplicate_count == 0, {"duplicate_count": duplicate_count}

    def _run_expect_column_values_to_be_between(self, rows: list[dict[str, Any]], kwargs: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        column = kwargs.get("column")
        min_value = kwargs.get("min_value")
        max_value = kwargs.get("max_value")
        out_of_range = 0

        for row in rows:
            value = row.get(column)
            numeric = self._to_float(value)
            if numeric is None:
                continue
            if min_value is not None and numeric < float(min_value):
                out_of_range += 1
            if max_value is not None and numeric > float(max_value):
                out_of_range += 1

        return out_of_range == 0, {"out_of_range": out_of_range}

    def _columns(self, rows: list[dict[str, Any]]) -> list[str]:
        ordered: list[str] = []
        seen: set[str] = set()
        for row in rows:
            for key in row.keys():
                if key not in seen:
                    seen.add(key)
                    ordered.append(key)
        return ordered

    def _to_float(self, value: Any) -> float | None:
        if isinstance(value, bool) or value is None:
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
