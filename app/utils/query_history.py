import json
import os
from datetime import datetime
from typing import List, Dict
from pathlib import Path

HISTORY_FILE = Path(".nl2sql_history.json")
MAX_HISTORY = 50


def save_query(question: str, sql: str, answer: str, success: bool):
    """Append a query result to the local history file."""
    history = load_history()

    entry = {
        "id": len(history) + 1,
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "sql": sql,
        "answer": answer[:300] + "..." if len(answer) > 300 else answer,
        "success": success,
    }

    history.insert(0, entry)          # newest first
    history = history[:MAX_HISTORY]   # keep last N

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def load_history() -> List[Dict]:
    """Load query history from disk."""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def clear_history():
    """Delete all query history."""
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
