import logging
import re
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Manages SQLAlchemy engine and sessions.
    Supports read-only mode and query timeouts for safety.
    """

    def __init__(
        self,
        database_url: Optional[str] = None,
        read_only: bool = True,
        query_timeout: int = 30,
    ):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self.read_only = read_only
        self.query_timeout = query_timeout

        if not self.database_url:
            raise ValueError(
                "DATABASE_URL not set. Add it to your .env file.\n"
                "Example: postgresql://user:password@localhost:5432/dbname"
            )

        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(bind=self.engine)
        logger.info(f"Connected to database: {self._safe_url()}")

    def _create_engine(self):
        engine = create_engine(
            self.database_url,
            pool_pre_ping=True,         # test connection before use
            pool_size=5,
            max_overflow=10,
            echo=False,
        )

        # Set statement timeout for every connection (PostgreSQL only)
        if self.database_url.startswith("postgres"):
            @event.listens_for(engine, "connect")
            def set_timeout(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute(
                    f"SET statement_timeout = {self.query_timeout * 1000}"
                )
                cursor.close()

        return engine

    def _safe_url(self) -> str:
        """Hide password from logs."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(self.database_url)
            return f"{parsed.scheme}://{parsed.hostname}:{parsed.port}{parsed.path}"
        except Exception:
            return "****"

    def test_connection(self) -> bool:
        """Ping the database to verify connectivity."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def execute_query(self, sql: str, max_rows: int = 500):
        """
        Execute a SQL query safely.
        - Blocks write operations in read_only mode
        - Limits result rows to max_rows
        - Returns (columns, rows) tuple
        """
        # Safety check: block write operations in read-only mode.
        # Splits on semicolons to catch multi-statement injections like "SELECT 1; DELETE ..."
        if self.read_only:
            banned = ["insert", "update", "delete", "drop", "truncate", "alter", "create"]
            # Split on semicolons and check each individual statement
            statements = [s.strip() for s in re.split(r";+", sql) if s.strip()]
            for stmt in statements:
                stmt_lower = stmt.lower()
                for keyword in banned:
                    # Match keyword at start of statement (ignoring leading whitespace/comments)
                    if re.match(rf"^\s*{keyword}\b", stmt_lower):
                        raise PermissionError(
                            f"Write operation blocked: '{keyword.upper()}' is not allowed in read-only mode."
                        )

        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            columns = list(result.keys())
            rows = result.fetchmany(max_rows)

        return columns, [list(row) for row in rows]

    def get_engine(self):
        return self.engine


# Singleton
_db_instance: Optional[DatabaseConnection] = None


def get_db_connection(database_url: Optional[str] = None) -> DatabaseConnection:
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseConnection(
            database_url=database_url,
            read_only=os.getenv("READ_ONLY", "true").lower() == "true",
            query_timeout=int(os.getenv("QUERY_TIMEOUT", "30")),
        )
    return _db_instance


def reset_db_connection() -> None:
    """Clear the cached singleton so the next call to get_db_connection() creates a fresh one."""
    global _db_instance
    _db_instance = None
