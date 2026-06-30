import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Callable

from app.anomaly.service import AnomalyDetectionService
from app.validators.base import BaseValidator
from app.validators.sdk import ValidationContext, ValidationResult, ValidationType


def _normalize_row(row: dict[str, Any]) -> str:
    return json.dumps(row, sort_keys=True, default=str)


def _row_key(row: dict[str, Any], primary_keys: list[str]) -> str:
    if not primary_keys:
        return _normalize_row(row)
    key_parts = [str(row.get(key, "")) for key in primary_keys]
    return "|".join(key_parts)


def _columns_from_rows(rows: list[dict[str, Any]]) -> list[str]:
    columns: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                columns.append(key)
    return columns


def _to_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return Decimal(text)
        except InvalidOperation:
            return None
    return None


def _parse_date(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


class BuiltinValidator(BaseValidator):
    def validate(self, context: ValidationContext) -> ValidationResult:
        handlers: dict[ValidationType, Callable[[ValidationContext], ValidationResult]] = {
            ValidationType.RECORD_COUNT: self._record_count,
            ValidationType.COLUMN_COUNT: self._column_count,
            ValidationType.METADATA_VALIDATION: self._metadata_validation,
            ValidationType.DUPLICATE_DETECTION: self._duplicate_detection,
            ValidationType.NULL_ANALYSIS: self._null_analysis,
            ValidationType.EMPTY_STRING_DETECTION: self._empty_string_detection,
            ValidationType.DATA_COMPARISON: self._data_comparison,
            ValidationType.COLUMN_ORDER: self._column_order,
            ValidationType.PRECISION: self._precision,
            ValidationType.SCALE: self._scale,
            ValidationType.LENGTH: self._length,
            ValidationType.DISTINCT_COUNT: self._distinct_count,
            ValidationType.DATE_RANGE: self._date_range,
            ValidationType.CASE_SENSITIVITY: self._case_sensitivity,
            ValidationType.LEADING_ZEROS: self._leading_zeros,
            ValidationType.SPECIAL_CHARACTERS: self._special_characters,
            ValidationType.ROW_CHECKSUM: self._row_checksum,
            ValidationType.SYMMETRIC_DIFFERENCE: self._symmetric_difference,
            ValidationType.GREAT_EXPECTATIONS: self._great_expectations,
            ValidationType.ISOLATION_FOREST: self._isolation_forest,
            ValidationType.CUSTOM_SQL: self._custom_sql,
            ValidationType.CUSTOM_PYTHON: self._custom_python,
            ValidationType.CUSTOM_SPARK: self._custom_spark,
        }
        handler = handlers[self.spec.validation_type]
        return handler(context)

    def _record_count(self, context: ValidationContext) -> ValidationResult:
        source_count = len(context.source_rows)
        target_count = len(context.target_rows)
        success = source_count == target_count
        return ValidationResult(
            success=success,
            score=1.0 if success else 0.0,
            message="Record count validation completed",
            details={"source_count": source_count, "target_count": target_count},
        )

    def _column_count(self, context: ValidationContext) -> ValidationResult:
        source_cols = context.source_column_order or list(context.source_schema.keys()) or _columns_from_rows(context.source_rows)
        target_cols = context.target_column_order or list(context.target_schema.keys()) or _columns_from_rows(context.target_rows)
        success = len(source_cols) == len(target_cols)
        return ValidationResult(
            success=success,
            score=1.0 if success else 0.0,
            message="Column count validation completed",
            details={"source_columns": len(source_cols), "target_columns": len(target_cols)},
        )

    def _metadata_validation(self, context: ValidationContext) -> ValidationResult:
        mismatches = []
        for column, source_type in context.source_schema.items():
            target_type = context.target_schema.get(column)
            if target_type is None:
                mismatches.append({"column": column, "issue": "missing_in_target"})
            elif str(source_type).lower() != str(target_type).lower():
                mismatches.append({"column": column, "source_type": source_type, "target_type": target_type})
        success = len(mismatches) == 0
        return ValidationResult(
            success=success,
            score=1.0 if success else 0.0,
            message="Metadata validation completed",
            details={"mismatches": mismatches},
        )

    def _duplicate_detection(self, context: ValidationContext) -> ValidationResult:
        pk = context.primary_keys
        source_keys = [_row_key(row, pk) for row in context.source_rows]
        target_keys = [_row_key(row, pk) for row in context.target_rows]
        source_dupes = [item for item, count in Counter(source_keys).items() if count > 1]
        target_dupes = [item for item, count in Counter(target_keys).items() if count > 1]
        success = not source_dupes and not target_dupes
        return ValidationResult(
            success=success,
            score=1.0 if success else 0.0,
            message="Duplicate detection completed",
            details={"source_duplicates": source_dupes, "target_duplicates": target_dupes},
        )

    def _null_analysis(self, context: ValidationContext) -> ValidationResult:
        columns = context.source_column_order or _columns_from_rows(context.source_rows)
        source_nulls = {col: sum(1 for row in context.source_rows if row.get(col) is None) for col in columns}
        target_nulls = {col: sum(1 for row in context.target_rows if row.get(col) is None) for col in columns}
        success = source_nulls == target_nulls
        return ValidationResult(
            success=success,
            score=1.0 if success else 0.0,
            message="Null analysis completed",
            details={"source_nulls": source_nulls, "target_nulls": target_nulls},
        )

    def _empty_string_detection(self, context: ValidationContext) -> ValidationResult:
        columns = context.source_column_order or _columns_from_rows(context.source_rows)
        source_counts = {
            col: sum(1 for row in context.source_rows if isinstance(row.get(col), str) and row.get(col, "").strip() == "")
            for col in columns
        }
        target_counts = {
            col: sum(1 for row in context.target_rows if isinstance(row.get(col), str) and row.get(col, "").strip() == "")
            for col in columns
        }
        success = source_counts == target_counts
        return ValidationResult(
            success=success,
            score=1.0 if success else 0.0,
            message="Empty string detection completed",
            details={"source_empty_strings": source_counts, "target_empty_strings": target_counts},
        )

    def _data_comparison(self, context: ValidationContext) -> ValidationResult:
        pk = context.primary_keys
        if pk:
            source_map = {_row_key(row, pk): row for row in context.source_rows}
            target_map = {_row_key(row, pk): row for row in context.target_rows}
            mismatches = []
            for key in sorted(set(source_map) | set(target_map)):
                if key not in source_map or key not in target_map:
                    mismatches.append({"key": key, "issue": "missing_row"})
                elif _normalize_row(source_map[key]) != _normalize_row(target_map[key]):
                    mismatches.append({"key": key, "issue": "value_mismatch"})
        else:
            source_rows = sorted(_normalize_row(row) for row in context.source_rows)
            target_rows = sorted(_normalize_row(row) for row in context.target_rows)
            mismatches = [] if source_rows == target_rows else [{"issue": "row_set_mismatch"}]
        success = len(mismatches) == 0
        return ValidationResult(success=success, score=1.0 if success else 0.0, message="Data comparison completed", details={"mismatches": mismatches})

    def _column_order(self, context: ValidationContext) -> ValidationResult:
        source = context.source_column_order or list(context.source_schema.keys()) or _columns_from_rows(context.source_rows)
        target = context.target_column_order or list(context.target_schema.keys()) or _columns_from_rows(context.target_rows)
        success = source == target
        return ValidationResult(success=success, score=1.0 if success else 0.0, message="Column order validation completed", details={"source_order": source, "target_order": target})

    def _precision(self, context: ValidationContext) -> ValidationResult:
        source_precision = self._numeric_profile(context.source_rows, metric="precision")
        target_precision = self._numeric_profile(context.target_rows, metric="precision")
        success = source_precision == target_precision
        return ValidationResult(success=success, score=1.0 if success else 0.0, message="Precision validation completed", details={"source": source_precision, "target": target_precision})

    def _scale(self, context: ValidationContext) -> ValidationResult:
        source_scale = self._numeric_profile(context.source_rows, metric="scale")
        target_scale = self._numeric_profile(context.target_rows, metric="scale")
        success = source_scale == target_scale
        return ValidationResult(success=success, score=1.0 if success else 0.0, message="Scale validation completed", details={"source": source_scale, "target": target_scale})

    def _length(self, context: ValidationContext) -> ValidationResult:
        source_length = self._length_profile(context.source_rows)
        target_length = self._length_profile(context.target_rows)
        success = source_length == target_length
        return ValidationResult(success=success, score=1.0 if success else 0.0, message="Length validation completed", details={"source": source_length, "target": target_length})

    def _distinct_count(self, context: ValidationContext) -> ValidationResult:
        source_distinct = self._distinct_profile(context.source_rows)
        target_distinct = self._distinct_profile(context.target_rows)
        success = source_distinct == target_distinct
        return ValidationResult(success=success, score=1.0 if success else 0.0, message="Distinct count validation completed", details={"source": source_distinct, "target": target_distinct})

    def _date_range(self, context: ValidationContext) -> ValidationResult:
        source_range = self._date_profile(context.source_rows)
        target_range = self._date_profile(context.target_rows)
        success = source_range == target_range
        return ValidationResult(success=success, score=1.0 if success else 0.0, message="Date range validation completed", details={"source": source_range, "target": target_range})

    def _case_sensitivity(self, context: ValidationContext) -> ValidationResult:
        pk = context.primary_keys
        if not pk:
            return ValidationResult(success=True, score=1.0, message="Case sensitivity validation skipped", warnings=["primary_keys_not_provided"])

        source_map = {_row_key(row, pk): row for row in context.source_rows}
        target_map = {_row_key(row, pk): row for row in context.target_rows}
        differences = []
        for key in sorted(set(source_map) & set(target_map)):
            s_row = source_map[key]
            t_row = target_map[key]
            for column in set(s_row.keys()) & set(t_row.keys()):
                s_val = s_row.get(column)
                t_val = t_row.get(column)
                if isinstance(s_val, str) and isinstance(t_val, str):
                    if s_val.lower() == t_val.lower() and s_val != t_val:
                        differences.append({"key": key, "column": column, "source": s_val, "target": t_val})
        success = len(differences) == 0
        return ValidationResult(success=success, score=1.0 if success else 0.0, message="Case sensitivity validation completed", details={"differences": differences})

    def _leading_zeros(self, context: ValidationContext) -> ValidationResult:
        pk = context.primary_keys
        if not pk:
            return ValidationResult(success=True, score=1.0, message="Leading zeros validation skipped", warnings=["primary_keys_not_provided"])

        source_map = {_row_key(row, pk): row for row in context.source_rows}
        target_map = {_row_key(row, pk): row for row in context.target_rows}
        differences = []
        for key in sorted(set(source_map) & set(target_map)):
            for column in set(source_map[key].keys()) & set(target_map[key].keys()):
                s_val = source_map[key].get(column)
                t_val = target_map[key].get(column)
                if isinstance(s_val, str) and isinstance(t_val, str):
                    if s_val.isdigit() and t_val.isdigit() and s_val.lstrip("0") == t_val.lstrip("0") and s_val != t_val:
                        differences.append({"key": key, "column": column, "source": s_val, "target": t_val})
        success = len(differences) == 0
        return ValidationResult(success=success, score=1.0 if success else 0.0, message="Leading zeros validation completed", details={"differences": differences})

    def _special_characters(self, context: ValidationContext) -> ValidationResult:
        pattern = re.compile(r"[^\w\s]")

        def count_special(rows: list[dict[str, Any]]) -> int:
            total = 0
            for row in rows:
                for value in row.values():
                    if isinstance(value, str):
                        total += len(pattern.findall(value))
            return total

        source_total = count_special(context.source_rows)
        target_total = count_special(context.target_rows)
        success = source_total == target_total
        return ValidationResult(success=success, score=1.0 if success else 0.0, message="Special character validation completed", details={"source_special_characters": source_total, "target_special_characters": target_total})

    def _row_checksum(self, context: ValidationContext) -> ValidationResult:
        source_checksums = sorted(hashlib.sha256(_normalize_row(row).encode("utf-8")).hexdigest() for row in context.source_rows)
        target_checksums = sorted(hashlib.sha256(_normalize_row(row).encode("utf-8")).hexdigest() for row in context.target_rows)
        success = source_checksums == target_checksums
        return ValidationResult(success=success, score=1.0 if success else 0.0, message="Row checksum validation completed", details={"source_checksum_count": len(source_checksums), "target_checksum_count": len(target_checksums)})

    def _symmetric_difference(self, context: ValidationContext) -> ValidationResult:
        source_set = {_normalize_row(row) for row in context.source_rows}
        target_set = {_normalize_row(row) for row in context.target_rows}
        only_source = sorted(source_set - target_set)
        only_target = sorted(target_set - source_set)
        success = not only_source and not only_target
        return ValidationResult(success=success, score=1.0 if success else 0.0, message="Symmetric difference validation completed", details={"source_only_count": len(only_source), "target_only_count": len(only_target)})

    def _great_expectations(self, context: ValidationContext) -> ValidationResult:
        runner = context.options.get("great_expectations_runner") or self.config.get("great_expectations_runner")
        if callable(runner):
            result = runner(context)
            if isinstance(result, dict):
                success = bool(result.get("success", False))
                details = dict(result)
                return ValidationResult(
                    success=success,
                    score=1.0 if success else 0.0,
                    message="Great Expectations validation completed",
                    details=details,
                )

            success = bool(result)
            return ValidationResult(
                success=success,
                score=1.0 if success else 0.0,
                message="Great Expectations validation completed",
                details={},
            )

        warnings = ["great_expectations_runner_not_configured"]
        try:
            import great_expectations  # type: ignore  # noqa: F401
            warnings.append("great_expectations_dependency_available")
        except ImportError:
            warnings.append("great_expectations_dependency_not_installed")

        return ValidationResult(success=True, score=1.0, message="Great Expectations validation skipped", warnings=warnings)

    def _isolation_forest(self, context: ValidationContext) -> ValidationResult:
        runner = context.options.get("anomaly_detection_runner") or self.config.get("anomaly_detection_runner")

        if callable(runner):
            payload = runner(context)
            if isinstance(payload, dict):
                success = bool(payload.get("success", False))
                score = float(payload.get("score", 1.0 if success else 0.0))
                warnings = list(payload.get("warnings", []))
                details = dict(payload)
                return ValidationResult(
                    success=success,
                    score=score,
                    message="Isolation Forest validation completed",
                    details=details,
                    warnings=warnings,
                )

            success = bool(payload)
            return ValidationResult(
                success=success,
                score=1.0 if success else 0.0,
                message="Isolation Forest validation completed",
                details={},
            )

        model = str(context.options.get("anomaly_model") or self.config.get("anomaly_model") or "isolation_forest")
        feature_columns = list(context.options.get("anomaly_features") or self.config.get("anomaly_features") or [])
        if not feature_columns:
            feature_columns = [
                column
                for column in _columns_from_rows(context.source_rows)
                if any(_to_decimal(row.get(column)) is not None for row in context.source_rows)
            ]

        service = AnomalyDetectionService()
        result = service.detect(
            rows=context.source_rows,
            feature_columns=feature_columns,
            model=model,
            config=dict(context.options.get("anomaly_config") or self.config.get("anomaly_config") or {}),
        )

        score = max(0.0, 1.0 - (result.anomaly_count / max(1, result.total_rows)))
        return ValidationResult(
            success=result.success,
            score=score,
            message="Isolation Forest validation completed",
            details={
                "model": result.model,
                "anomaly_count": result.anomaly_count,
                "total_rows": result.total_rows,
                "anomaly_indices": result.anomaly_indices,
                "anomaly_scores": result.anomaly_scores,
                "visualizations": result.visualizations,
            },
            warnings=result.warnings,
        )

    def _custom_sql(self, context: ValidationContext) -> ValidationResult:
        runner = context.options.get("custom_sql_runner") or self.config.get("custom_sql_runner")
        if not callable(runner):
            return ValidationResult(success=False, score=0.0, message="custom_sql_runner not configured")
        result = runner(context)
        if isinstance(result, ValidationResult):
            return result
        ok = bool(result)
        return ValidationResult(success=ok, score=1.0 if ok else 0.0, message="Custom SQL validation completed")

    def _custom_python(self, context: ValidationContext) -> ValidationResult:
        runner = context.options.get("custom_python_runner") or self.config.get("custom_python_runner")
        if not callable(runner):
            return ValidationResult(success=False, score=0.0, message="custom_python_runner not configured")
        result = runner(context)
        if isinstance(result, ValidationResult):
            return result
        ok = bool(result)
        return ValidationResult(success=ok, score=1.0 if ok else 0.0, message="Custom Python validation completed")

    def _custom_spark(self, context: ValidationContext) -> ValidationResult:
        runner = context.options.get("custom_spark_runner") or self.config.get("custom_spark_runner")
        if not callable(runner):
            return ValidationResult(success=False, score=0.0, message="custom_spark_runner not configured")
        result = runner(context)
        if isinstance(result, ValidationResult):
            return result
        ok = bool(result)
        return ValidationResult(success=ok, score=1.0 if ok else 0.0, message="Custom Spark validation completed")

    def _numeric_profile(self, rows: list[dict[str, Any]], metric: str) -> dict[str, int]:
        profile: dict[str, int] = {}
        for column in _columns_from_rows(rows):
            values = [_to_decimal(row.get(column)) for row in rows]
            numeric_values = [value for value in values if value is not None]
            if not numeric_values:
                continue
            if metric == "precision":
                max_precision = 0
                for value in numeric_values:
                    sign, digits, exponent = value.as_tuple()
                    precision = len(digits)
                    _ = sign
                    if exponent > 0:
                        precision += exponent
                    max_precision = max(max_precision, precision)
                profile[column] = max_precision
            elif metric == "scale":
                max_scale = 0
                for value in numeric_values:
                    exponent = value.as_tuple().exponent
                    if exponent < 0:
                        max_scale = max(max_scale, abs(exponent))
                profile[column] = max_scale
        return profile

    def _length_profile(self, rows: list[dict[str, Any]]) -> dict[str, int]:
        profile: dict[str, int] = {}
        for column in _columns_from_rows(rows):
            lengths = [len(str(row.get(column))) for row in rows if row.get(column) is not None]
            if lengths:
                profile[column] = max(lengths)
        return profile

    def _distinct_profile(self, rows: list[dict[str, Any]]) -> dict[str, int]:
        profile: dict[str, int] = {}
        for column in _columns_from_rows(rows):
            values = {_normalize_row({column: row.get(column)}) for row in rows}
            profile[column] = len(values)
        return profile

    def _date_profile(self, rows: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
        profile: dict[str, dict[str, str]] = {}
        for column in _columns_from_rows(rows):
            parsed_values = [_parse_date(row.get(column)) for row in rows]
            dates = sorted([value for value in parsed_values if value is not None])
            if dates:
                profile[column] = {"min": dates[0].isoformat(), "max": dates[-1].isoformat()}
        return profile
