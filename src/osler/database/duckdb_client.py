from pathlib import Path

import duckdb

from osler.config import get_default_database_path

from .base import Database


class DuckDB(Database):
    def __init__(self, db_path=None):
        self.db_path = db_path or get_default_database_path("tuva-project-demo")

        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"DuckDB database not found: {self.db_path}")

    def _conn(self):
        return duckdb.connect(self.db_path)

    def execute_query(self, sql_query: str) -> str:
        conn = self._conn()
        try:
            df = conn.execute(sql_query).df()
            if df.empty:
                return "No results found"
            if len(df) > 50:
                return df.head(50).to_string(index=False) + f"\n... ({len(df)} rows)"
            return df.to_string(index=False)
        finally:
            conn.close()

    def get_schema(self) -> list[str]:
        conn = self._conn()
        results = []
        try:
            schemas = conn.execute("SELECT schema_name FROM information_schema.schemata").fetchall()
            for (schema,) in schemas:
                tables = conn.execute(
                    f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'"
                ).fetchall()
                for (table,) in tables:
                    results.append(f"{schema}.{table}")
            return results
        finally:
            conn.close()

    def get_table_info(self, table_name: str, show_sample: bool = True) -> str:
        conn = self._conn()
        try:
            col_info = conn.execute(f"PRAGMA table_info({table_name})").df()
            result = f"Table: {table_name}\n\nColumns:\n{col_info.to_string(index=False)}"

            if show_sample:
                sample = conn.execute(f"SELECT * FROM {table_name} LIMIT 3").df()
                result += f"\n\nSample:\n{sample.to_string(index=False)}"
            return result
        finally:
            conn.close()
