import pytest
from unittest.mock import MagicMock, patch


# ── Schema Inspector ─────────────────────────────────────────────────

def test_schema_prompt_format():
    """Schema prompt should contain table names and column info."""
    from app.database.schema_inspector import SchemaInspector

    mock_db = MagicMock()
    inspector = SchemaInspector(mock_db)

    # Inject fake schema cache
    inspector._schema_cache = {
        "customers": {
            "columns": [
                {"name": "id", "type": "INTEGER", "nullable": False},
                {"name": "email", "type": "VARCHAR", "nullable": False},
            ],
            "primary_key": ["id"],
            "foreign_keys": [],
        }
    }

    prompt = inspector.get_schema_prompt()
    assert "customers" in prompt
    assert "id" in prompt
    assert "email" in prompt
    assert "PK" in prompt


# ── Database Connection ──────────────────────────────────────────────

def test_read_only_blocks_insert():
    """Read-only mode should raise PermissionError on INSERT."""
    from app.database.connection import DatabaseConnection

    with patch("app.database.connection.create_engine") as mock_engine:
        mock_engine.return_value = MagicMock()
        db = DatabaseConnection.__new__(DatabaseConnection)
        db.read_only = True
        db.query_timeout = 30
        db.database_url = "postgresql://test"
        db.engine = MagicMock()

        with pytest.raises(PermissionError):
            db.execute_query("INSERT INTO users VALUES (1, 'test')")


def test_read_only_blocks_delete():
    """Read-only mode should raise PermissionError on DELETE."""
    from app.database.connection import DatabaseConnection

    db = DatabaseConnection.__new__(DatabaseConnection)
    db.read_only = True
    db.engine = MagicMock()

    with pytest.raises(PermissionError):
        db.execute_query("DELETE FROM orders WHERE id = 1")


def test_select_passes_read_only():
    """SELECT queries should not be blocked by read-only mode."""
    from app.database.connection import DatabaseConnection

    db = DatabaseConnection.__new__(DatabaseConnection)
    db.read_only = True
    db.engine = MagicMock()

    mock_result = MagicMock()
    mock_result.keys.return_value = ["id", "name"]
    mock_result.fetchmany.return_value = [(1, "Alice"), (2, "Bob")]

    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.execute.return_value = mock_result
    db.engine.connect.return_value = mock_conn

    cols, rows = db.execute_query("SELECT id, name FROM customers")
    assert cols == ["id", "name"]
    assert len(rows) == 2


# ── Chart Renderer ───────────────────────────────────────────────────

def test_bar_chart_text_plus_numeric():
    """Text + numeric columns should produce a bar chart."""
    from app.utils.chart_renderer import render_chart

    cols = ["category", "revenue"]
    rows = [["Electronics", 50000], ["Books", 12000], ["Fitness", 8000]]
    fig = render_chart(cols, rows)
    assert fig is not None
    assert fig.data[0].type == "bar"


def test_no_chart_single_column():
    """Single column results should not produce a chart."""
    from app.utils.chart_renderer import render_chart

    cols = ["customer_name"]
    rows = [["Alice"], ["Bob"]]
    fig = render_chart(cols, rows)
    assert fig is None


# ── Query History ────────────────────────────────────────────────────

def test_save_and_load_history(tmp_path, monkeypatch):
    """Saved queries should be retrievable from history."""
    import app.utils.query_history as qh

    monkeypatch.setattr(qh, "HISTORY_FILE", tmp_path / "history.json")

    qh.save_query("How many orders?", "SELECT COUNT(*) FROM orders", "42 orders", True)
    history = qh.load_history()

    assert len(history) == 1
    assert history[0]["question"] == "How many orders?"
    assert history[0]["success"] is True


def test_clear_history(tmp_path, monkeypatch):
    """Clear history should remove all entries."""
    import app.utils.query_history as qh

    monkeypatch.setattr(qh, "HISTORY_FILE", tmp_path / "history.json")
    qh.save_query("Test?", "SELECT 1", "1", True)
    qh.clear_history()

    assert qh.load_history() == []
