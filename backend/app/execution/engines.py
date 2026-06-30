import importlib.util
from typing import Any

from app.execution.base import BaseExecutionEngine
from app.execution.errors import EngineExecutionError, EngineUnavailableError
from app.execution.sdk import EngineType, ExecutionOperation, ExecutionPlan, ExecutionResult


def _format_sql_literal(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def _render_sql(query: str, parameters: dict[str, Any]) -> str:
    rendered = query
    for key, value in parameters.items():
        literal = _format_sql_literal(value)
        rendered = rendered.replace(f":{key}", literal)
        rendered = rendered.replace(f"{{{{{key}}}}}", literal)
    return rendered


def _execute_basic(plan: ExecutionPlan) -> Any:
    if plan.operation == ExecutionOperation.IDENTITY:
        return plan.rows
    if plan.operation == ExecutionOperation.COUNT:
        return len(plan.rows)
    if plan.operation == ExecutionOperation.SELECT_COLUMNS:
        return [{column: row.get(column) for column in plan.columns} for row in plan.rows]
    if plan.operation == ExecutionOperation.SQL:
        raise EngineExecutionError("SQL operation requires a SQL-capable engine")
    raise EngineExecutionError(f"Unsupported operation: {plan.operation.value}")


class PandasExecutionEngine(BaseExecutionEngine):
    engine_type = EngineType.PANDAS

    def is_available(self) -> bool:
        return importlib.util.find_spec("pandas") is not None

    def execute(self, plan: ExecutionPlan) -> ExecutionResult:
        if not self.is_available():
            raise EngineUnavailableError("pandas is not installed")

        import pandas as pd  # type: ignore

        if plan.operation == ExecutionOperation.SQL:
            raise EngineExecutionError("Pandas engine does not execute SQL directly")

        df = pd.DataFrame(plan.rows)
        if plan.operation == ExecutionOperation.IDENTITY:
            data = df.to_dict(orient="records")
        elif plan.operation == ExecutionOperation.COUNT:
            data = int(df.shape[0])
        elif plan.operation == ExecutionOperation.SELECT_COLUMNS:
            data = df[plan.columns].to_dict(orient="records")
        else:
            data = _execute_basic(plan)

        return ExecutionResult(engine=self.engine_type, success=True, data=data)


class PySparkExecutionEngine(BaseExecutionEngine):
    engine_type = EngineType.PYSPARK

    def is_available(self) -> bool:
        return importlib.util.find_spec("pyspark") is not None

    def execute(self, plan: ExecutionPlan) -> ExecutionResult:
        if not self.is_available():
            raise EngineUnavailableError("pyspark is not installed")

        from pyspark.sql import SparkSession  # type: ignore

        spark = SparkSession.builder.master("local[1]").appName("tkk-uv-execution-engine").getOrCreate()
        try:
            dataframe = spark.createDataFrame(plan.rows)
            dataframe.createOrReplaceTempView("dataset")

            for sql in plan.pre_sql:
                spark.sql(_render_sql(sql, plan.parameters))

            if plan.operation == ExecutionOperation.SQL:
                if not plan.sql_query:
                    raise EngineExecutionError("sql_query is required for SQL operation")
                result = spark.sql(_render_sql(plan.sql_query, plan.parameters))
                data = [row.asDict() for row in result.collect()]
            else:
                if plan.operation == ExecutionOperation.IDENTITY:
                    data = [row.asDict() for row in dataframe.collect()]
                elif plan.operation == ExecutionOperation.COUNT:
                    data = int(dataframe.count())
                elif plan.operation == ExecutionOperation.SELECT_COLUMNS:
                    data = [row.asDict() for row in dataframe.select(*plan.columns).collect()]
                else:
                    data = _execute_basic(plan)
            return ExecutionResult(engine=self.engine_type, success=True, data=data)
        finally:
            spark.stop()


class PolarsExecutionEngine(BaseExecutionEngine):
    engine_type = EngineType.POLARS

    def is_available(self) -> bool:
        return importlib.util.find_spec("polars") is not None

    def execute(self, plan: ExecutionPlan) -> ExecutionResult:
        if not self.is_available():
            raise EngineUnavailableError("polars is not installed")

        import polars as pl  # type: ignore

        if plan.operation == ExecutionOperation.SQL:
            raise EngineExecutionError("Polars engine does not execute SQL directly")

        frame = pl.DataFrame(plan.rows)
        if plan.operation == ExecutionOperation.IDENTITY:
            data = frame.to_dicts()
        elif plan.operation == ExecutionOperation.COUNT:
            data = int(frame.height)
        elif plan.operation == ExecutionOperation.SELECT_COLUMNS:
            data = frame.select(plan.columns).to_dicts()
        else:
            data = _execute_basic(plan)

        return ExecutionResult(engine=self.engine_type, success=True, data=data)


class DuckDBExecutionEngine(BaseExecutionEngine):
    engine_type = EngineType.DUCKDB

    def is_available(self) -> bool:
        return importlib.util.find_spec("duckdb") is not None

    def execute(self, plan: ExecutionPlan) -> ExecutionResult:
        if not self.is_available():
            raise EngineUnavailableError("duckdb is not installed")

        import duckdb  # type: ignore

        con = duckdb.connect(database=":memory:")
        try:
            if plan.rows:
                columns = list(plan.rows[0].keys())
                con.execute(
                    f"create table dataset ({', '.join(f'{name} varchar' for name in columns)})"
                )
                for row in plan.rows:
                    values = [str(row.get(column)) if row.get(column) is not None else None for column in columns]
                    placeholders = ",".join(["?"] * len(values))
                    con.execute(f"insert into dataset values ({placeholders})", values)
            else:
                con.execute("create table dataset (__empty integer)")

            for sql in plan.pre_sql:
                con.execute(_render_sql(sql, plan.parameters))

            if plan.operation == ExecutionOperation.SQL:
                if not plan.sql_query:
                    raise EngineExecutionError("sql_query is required for SQL operation")
                query_result = con.execute(_render_sql(plan.sql_query, plan.parameters))
                columns = [column[0] for column in (query_result.description or [])]
                rows = query_result.fetchall()
                data = [dict(zip(columns, row)) for row in rows] if columns else rows
            elif plan.operation == ExecutionOperation.COUNT:
                data = int(con.execute("select count(*) from dataset").fetchone()[0])
            elif plan.operation == ExecutionOperation.SELECT_COLUMNS:
                query = f"select {', '.join(plan.columns)} from dataset"
                rows = con.execute(query).fetchall()
                data = [dict(zip(plan.columns, row)) for row in rows]
            elif plan.operation == ExecutionOperation.IDENTITY:
                if not plan.rows:
                    data = []
                else:
                    columns = list(plan.rows[0].keys())
                    rows = con.execute(f"select {', '.join(columns)} from dataset").fetchall()
                    data = [dict(zip(columns, row)) for row in rows]
            else:
                data = _execute_basic(plan)

            return ExecutionResult(engine=self.engine_type, success=True, data=data)
        finally:
            con.close()
