from collections import Counter
from datetime import date, datetime
from decimal import Decimal
from typing import Any


class DataProfilingEngine:
    def profile_dataset(self, rows: list[dict[str, Any]], dataset_name: str) -> dict[str, Any]:
        columns = self._discover_columns(rows)
        row_count = len(rows)

        column_profiles: dict[str, dict[str, Any]] = {}
        for column in columns:
            values = [row.get(column) for row in rows]
            column_profiles[column] = self._profile_column(values, row_count)

        return {
            "dataset_name": dataset_name,
            "row_count": row_count,
            "column_count": len(columns),
            "schema": {column: profile["inferred_type"] for column, profile in column_profiles.items()},
            "columns": column_profiles,
        }

    def _discover_columns(self, rows: list[dict[str, Any]]) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for row in rows:
            for key in row.keys():
                if key not in seen:
                    seen.add(key)
                    ordered.append(key)
        return ordered

    def _profile_column(self, values: list[Any], row_count: int) -> dict[str, Any]:
        null_count = sum(1 for value in values if value is None)
        null_percent = (null_count / row_count * 100.0) if row_count else 0.0

        non_null_values = [value for value in values if value is not None]
        unique_count = len(set(self._stable_key(value) for value in non_null_values))
        non_null_count = len(non_null_values)
        uniqueness_percent = (unique_count / non_null_count * 100.0) if non_null_count else 0.0

        inferred_type = self._infer_type(non_null_values)
        numeric_values = self._to_numeric(non_null_values)

        min_value, max_value = self._safe_min_max(non_null_values)
        average_value = (sum(numeric_values) / len(numeric_values)) if numeric_values else None

        histogram = self._build_histogram(numeric_values)
        top_values = self._top_values(non_null_values)
        distribution = self._distribution(non_null_values)

        return {
            "null_percent": round(null_percent, 4),
            "null_count": null_count,
            "uniqueness_percent": round(uniqueness_percent, 4),
            "unique_count": unique_count,
            "cardinality": unique_count,
            "min": min_value,
            "max": max_value,
            "average": round(average_value, 6) if average_value is not None else None,
            "histogram": histogram,
            "top_values": top_values,
            "distribution": distribution,
            "inferred_type": inferred_type,
        }

    def _infer_type(self, values: list[Any]) -> str:
        if not values:
            return "unknown"

        type_names = {self._type_name(value) for value in values}
        if len(type_names) == 1:
            return next(iter(type_names))
        return f"mixed[{','.join(sorted(type_names))}]"

    def _type_name(self, value: Any) -> str:
        if isinstance(value, bool):
            return "bool"
        if isinstance(value, int):
            return "int"
        if isinstance(value, float):
            return "float"
        if isinstance(value, Decimal):
            return "decimal"
        if isinstance(value, datetime):
            return "datetime"
        if isinstance(value, date):
            return "date"
        if isinstance(value, str):
            return "str"
        if isinstance(value, (list, tuple)):
            return "array"
        if isinstance(value, dict):
            return "object"
        return type(value).__name__

    def _to_numeric(self, values: list[Any]) -> list[float]:
        numeric: list[float] = []
        for value in values:
            if isinstance(value, bool):
                continue
            if isinstance(value, (int, float, Decimal)):
                numeric.append(float(value))
        return numeric

    def _build_histogram(self, numeric_values: list[float], bins: int = 10) -> list[dict[str, Any]]:
        if not numeric_values:
            return []

        min_value = min(numeric_values)
        max_value = max(numeric_values)
        if min_value == max_value:
            return [{"range": f"{min_value}", "count": len(numeric_values)}]

        width = (max_value - min_value) / bins
        counts = [0 for _ in range(bins)]

        for value in numeric_values:
            index = int((value - min_value) / width)
            if index == bins:
                index = bins - 1
            counts[index] += 1

        histogram: list[dict[str, Any]] = []
        for idx, count in enumerate(counts):
            start = min_value + idx * width
            end = start + width
            histogram.append({
                "range": f"{round(start, 4)}-{round(end, 4)}",
                "count": count,
            })

        return histogram

    def _top_values(self, values: list[Any], limit: int = 5) -> list[dict[str, Any]]:
        if not values:
            return []

        counter = Counter(self._stable_key(value) for value in values)
        lookup: dict[str, Any] = {}
        for value in values:
            lookup.setdefault(self._stable_key(value), value)

        top = counter.most_common(limit)
        return [{"value": lookup[key], "count": count} for key, count in top]

    def _distribution(self, values: list[Any], limit: int = 20) -> list[dict[str, Any]]:
        if not values:
            return []

        total = len(values)
        counter = Counter(self._stable_key(value) for value in values)
        lookup: dict[str, Any] = {}
        for value in values:
            lookup.setdefault(self._stable_key(value), value)

        top_items = counter.most_common(limit)
        return [
            {
                "value": lookup[key],
                "count": count,
                "percent": round((count / total) * 100.0, 4),
            }
            for key, count in top_items
        ]

    def _safe_min_max(self, values: list[Any]) -> tuple[Any, Any]:
        if not values:
            return None, None

        try:
            return min(values), max(values)
        except TypeError:
            comparable = sorted((str(value) for value in values))
            return comparable[0], comparable[-1]

    def _stable_key(self, value: Any) -> str:
        return f"{type(value).__name__}:{repr(value)}"
