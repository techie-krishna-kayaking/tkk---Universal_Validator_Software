# Plugin SDK — tkk-UniversalValidator

This guide covers developing custom connectors and custom validators using the tkk-UniversalValidator Plugin SDK.

---

## Overview

Both connector and validator plugins follow the same lifecycle:
1. Define a `Spec` describing identity and capabilities.
2. Implement the abstract `Base` class.
3. Register the implementation with the platform's `Registry`.
4. The `Factory` instantiates and resolves your plugin at runtime.

---

## Connector Plugin SDK

### 1. Define your ConnectorSpec

```python
from app.connectors.sdk import (
    ConnectorCapability,
    ConnectorCategory,
    ConnectorSpec,
)

MY_CONNECTOR_SPEC = ConnectorSpec(
    key="my_custom_db",
    display_name="My Custom Database",
    category=ConnectorCategory.DATABASES,
    provider="my-company",
    capabilities=(
        ConnectorCapability.CONNECTION_TEST,
        ConnectorCapability.AUTHENTICATION,
        ConnectorCapability.SCHEMA_DISCOVERY,
        ConnectorCapability.SAMPLE_DATA,
        ConnectorCapability.PAGINATION,
    ),
)
```

---

### 2. Implement BaseConnector

```python
from typing import Any
from app.connectors.base import BaseConnector
from app.connectors.sdk import (
    ConnectionTestResult,
    ConnectorContext,
    ConnectorReadResult,
    MetadataResult,
    PrimaryKeyResult,
    SampleDataResult,
    SchemaResult,
)


class MyCustomDbConnector(BaseConnector):

    def authenticate(self, context: ConnectorContext) -> None:
        # Initialise connection using self.config
        host = self.config["host"]
        # ... establish connection pool

    def test_connection(self, context: ConnectorContext) -> ConnectionTestResult:
        try:
            # ... ping the database
            return ConnectionTestResult(success=True, message="Connection successful")
        except Exception as exc:
            return ConnectionTestResult(success=False, message=str(exc))

    def discover_metadata(self, context: ConnectorContext) -> MetadataResult:
        # Return list of tables/objects
        return MetadataResult(objects=[{"name": "my_table", "type": "table"}])

    def discover_schema(
        self,
        context: ConnectorContext,
        object_name: str | None = None,
    ) -> SchemaResult:
        return SchemaResult(columns=[{"name": "id", "type": "integer"}])

    def discover_primary_keys(
        self,
        context: ConnectorContext,
        object_name: str | None = None,
    ) -> PrimaryKeyResult:
        return PrimaryKeyResult(keys=["id"])

    def sample_data(
        self,
        context: ConnectorContext,
        object_name: str | None = None,
        limit: int = 10,
    ) -> SampleDataResult:
        return SampleDataResult(rows=[{"id": 1}])

    def read_page(
        self,
        context: ConnectorContext,
        object_name: str | None = None,
        cursor: str | None = None,
        page_size: int = 100,
    ) -> ConnectorReadResult:
        return ConnectorReadResult(rows=[], next_cursor=None)

    def stream_data(
        self,
        context: ConnectorContext,
        object_name: str | None = None,
    ) -> ConnectorReadResult:
        return ConnectorReadResult(rows=[])

    def incremental_read(
        self,
        context: ConnectorContext,
        object_name: str | None = None,
        since: str | None = None,
    ) -> ConnectorReadResult:
        return ConnectorReadResult(rows=[])
```

---

### 3. Register the connector

```python
from app.connectors.registry import ConnectorRegistry

ConnectorRegistry.register(
    spec=MY_CONNECTOR_SPEC,
    implementation=MyCustomDbConnector,
)
```

Place this registration call in your plugin's `__init__.py` under `backend/app/connectors/plugins/`.

---

### 4. Connector config schema

Your connector receives user-supplied config as a `dict[str, Any]`. Document the expected keys:

```python
# Example config for MyCustomDbConnector
{
    "host": "db.example.com",
    "port": 5432,
    "database": "my_db",
    "username": "user",
    "password": "<encrypted-by-platform>",
    "ssl": True,
}
```

Passwords and API keys are decrypted by the platform's `SecretCrypto` before passing to the connector. Never store plaintext credentials in the connector itself.

---

## Validator Plugin SDK

### 1. Define your ValidatorSpec

```python
from app.validators.sdk import ValidationType, ValidatorSpec

MY_VALIDATOR_SPEC = ValidatorSpec(
    key="my_custom_null_check",
    display_name="Custom Null Check",
    validation_type=ValidationType.NULL_ANALYSIS,
    description="Validates that specified columns have zero nulls.",
)
```

---

### 2. Implement BaseValidator

```python
from typing import Any
from app.validators.base import BaseValidator
from app.validators.sdk import ValidationContext, ValidationResult


class MyCustomNullCheckValidator(BaseValidator):

    def validate(self, context: ValidationContext) -> ValidationResult:
        target_columns: list[str] = self.config.get("columns", [])
        errors: list[str] = []
        total_rows = len(context.source_rows)

        for col in target_columns:
            null_count = sum(
                1 for row in context.source_rows if row.get(col) is None
            )
            if null_count > 0:
                errors.append(f"Column '{col}' has {null_count} null values")

        success = len(errors) == 0
        score = 1.0 if success else 0.0

        return ValidationResult(
            success=success,
            score=score,
            message="No nulls found" if success else f"{len(errors)} column(s) have nulls",
            details={"target_columns": target_columns, "total_rows": total_rows},
            errors=errors,
        )
```

---

### 3. Register the validator

```python
from app.validators.registry import ValidatorRegistry

ValidatorRegistry.register(
    spec=MY_VALIDATOR_SPEC,
    implementation=MyCustomNullCheckValidator,
)
```

Place this in `backend/app/validators/plugins/__init__.py`.

---

### 4. Using custom validators in YAML workflows

Reference your validator by its `key` in a YAML workflow:

```yaml
validations:
  - type: my_custom_null_check
    config:
      columns:
        - customer_id
        - order_date
```

---

## Plugin Discovery

The platform auto-loads plugins from:
- `backend/app/connectors/plugins/`
- `backend/app/validators/plugins/`

Any module in these directories that calls `Registry.register()` at import time will be available to the platform. Loader scans are triggered during application startup.

---

## Testing Your Plugin

Write unit tests in `backend/tests/unit/`:

```python
from app.connectors.sdk import ConnectorContext
from app.connectors.plugins.my_custom_db import MyCustomDbConnector, MY_CONNECTOR_SPEC


def test_connection_returns_success_on_valid_host() -> None:
    connector = MyCustomDbConnector(
        spec=MY_CONNECTOR_SPEC,
        config={"host": "localhost", "port": 5432, "database": "test"},
    )
    context = ConnectorContext(tenant_id="test-tenant")
    result = connector.test_connection(context)
    assert result.success is True
```

---

## SDK Dataclass Reference

### ConnectorContext

| Field | Type | Description |
|---|---|---|
| `tenant_id` | `str` | Tenant issuing the request |
| `user_id` | `str \| None` | Acting user (optional) |
| `request_id` | `str \| None` | Correlating request ID |

### ConnectionTestResult

| Field | Type |
|---|---|
| `success` | `bool` |
| `message` | `str` |
| `details` | `dict` |

### ValidationResult

| Field | Type | Description |
|---|---|---|
| `success` | `bool` | True if validation passed |
| `score` | `float` | 0.0–1.0 quality score |
| `message` | `str` | Human-readable summary |
| `details` | `dict` | Detailed metrics and metadata |
| `metrics` | `dict` | Numeric performance metrics |
| `warnings` | `list[str]` | Non-fatal issues |
| `errors` | `list[str]` | Fatal validation failures |

---

## Packaging and Distribution

A connector or validator plugin can be distributed as a standalone Python package:

```
my-tkk-connector/
├── pyproject.toml
├── README.md
└── my_tkk_connector/
    ├── __init__.py        # calls Registry.register()
    ├── connector.py
    └── tests/
```

Install it into the backend virtual environment:

```bash
cd backend
poetry add my-tkk-connector
```

The platform's loader will discover it at next startup.
