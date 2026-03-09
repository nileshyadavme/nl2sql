import logging
from sqlalchemy import inspect, text
from typing import Dict, List
from app.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class SchemaInspector:
    """
    Extracts database schema information to inject into the LLM prompt.
    This is the KEY to schema-aware SQL generation — the LLM needs to
    know table names, column names, types, and relationships.
    """

    def __init__(self, db: DatabaseConnection):
        self.db = db
        self._schema_cache: Dict = {}

    def get_schema(self, refresh: bool = False) -> Dict:
        """Return full schema as a dictionary (cached)."""
        if self._schema_cache and not refresh:
            return self._schema_cache

        inspector = inspect(self.db.get_engine())
        schema = {}

        for table_name in inspector.get_table_names():
            columns = []
            for col in inspector.get_columns(table_name):
                columns.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True),
                })

            # Get foreign keys
            fkeys = []
            for fk in inspector.get_foreign_keys(table_name):
                fkeys.append({
                    "constrained_columns": fk["constrained_columns"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"],
                })

            # Get primary key
            pk = inspector.get_pk_constraint(table_name)

            schema[table_name] = {
                "columns": columns,
                "primary_key": pk.get("constrained_columns", []),
                "foreign_keys": fkeys,
            }

        self._schema_cache = schema
        logger.info(f"Schema loaded: {len(schema)} tables found")
        return schema

    def get_schema_prompt(self) -> str:
        """
        Format schema as a clean text block for LLM system prompt.
        Example output:
            Table: orders
              - id (INTEGER, NOT NULL) [PK]
              - customer_id (INTEGER) → customers.id
              - total_amount (NUMERIC)
        """
        schema = self.get_schema()
        lines = ["DATABASE SCHEMA:", "=" * 50]

        for table_name, info in schema.items():
            lines.append(f"\nTable: {table_name}")

            pk_cols = info.get("primary_key", [])
            fk_map = {}
            for fk in info.get("foreign_keys", []):
                for col in fk["constrained_columns"]:
                    ref_table = fk["referred_table"]
                    ref_col = fk["referred_columns"][0]
                    fk_map[col] = f"{ref_table}.{ref_col}"

            for col in info["columns"]:
                name = col["name"]
                col_type = col["type"]
                flags = []

                if name in pk_cols:
                    flags.append("PK")
                if name in fk_map:
                    flags.append(f"FK → {fk_map[name]}")
                if not col["nullable"]:
                    flags.append("NOT NULL")

                flag_str = f"  [{', '.join(flags)}]" if flags else ""
                lines.append(f"  - {name} ({col_type}){flag_str}")

        lines.append("\n" + "=" * 50)
        return "\n".join(lines)

    def get_sample_values(self, table_name: str, column_name: str, limit: int = 5) -> List:
        """Get sample values for a column (useful for enum-like fields)."""
        try:
            cols, rows = self.db.execute_query(
                f"SELECT DISTINCT {column_name} FROM {table_name} LIMIT {limit}"
            )
            return [row[0] for row in rows]
        except Exception as e:
            logger.warning(f"Could not get sample values for {table_name}.{column_name}: {e}")
            return []

    def get_table_row_counts(self) -> Dict[str, int]:
        """Return approximate row counts per table."""
        counts = {}
        schema = self.get_schema()
        for table_name in schema:
            try:
                _, rows = self.db.execute_query(
                    f"SELECT COUNT(*) FROM {table_name}"
                )
                counts[table_name] = rows[0][0] if rows else 0
            except Exception:
                counts[table_name] = -1
        return counts
