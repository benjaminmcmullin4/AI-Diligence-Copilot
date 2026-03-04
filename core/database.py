"""SQLite database for storing analyses."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _get_connection(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db(db_path: str | Path) -> None:
    """Create tables if they don't exist."""
    conn = _get_connection(db_path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS analyses (
            id TEXT PRIMARY KEY,
            company_name TEXT NOT NULL,
            business_model TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            request_json TEXT NOT NULL,
            condensed_json TEXT,
            analysis_json TEXT,
            memo_json TEXT,
            memo_markdown TEXT,
            error_message TEXT,
            is_demo INTEGER NOT NULL DEFAULT 0
        );
    """)
    conn.close()


def save_analysis(db_path: str | Path, analysis_id: str, data: dict[str, Any]) -> None:
    """Insert or update an analysis record."""
    conn = _get_connection(db_path)
    now = datetime.now(timezone.utc).isoformat()

    existing = conn.execute("SELECT id FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
    if existing:
        sets = ", ".join(f"{k} = ?" for k in data)
        vals = list(data.values()) + [now, analysis_id]
        conn.execute(f"UPDATE analyses SET {sets}, updated_at = ? WHERE id = ?", vals)
    else:
        data["id"] = analysis_id
        data.setdefault("created_at", now)
        data["updated_at"] = now
        cols = ", ".join(data.keys())
        placeholders = ", ".join("?" for _ in data)
        conn.execute(f"INSERT INTO analyses ({cols}) VALUES ({placeholders})", list(data.values()))
    conn.commit()
    conn.close()


def get_analysis(db_path: str | Path, analysis_id: str) -> dict[str, Any] | None:
    """Fetch a single analysis by ID."""
    conn = _get_connection(db_path)
    row = conn.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)


def list_analyses(db_path: str | Path, include_demo: bool = True) -> list[dict[str, Any]]:
    """List all analyses ordered by creation date."""
    conn = _get_connection(db_path)
    if include_demo:
        rows = conn.execute(
            "SELECT id, company_name, business_model, status, created_at, is_demo "
            "FROM analyses ORDER BY created_at DESC"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, company_name, business_model, status, created_at, is_demo "
            "FROM analyses WHERE is_demo = 0 ORDER BY created_at DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_analysis(db_path: str | Path, analysis_id: str) -> None:
    """Delete an analysis by ID."""
    conn = _get_connection(db_path)
    conn.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
    conn.commit()
    conn.close()


def parse_json_field(value: str | None) -> dict | list | None:
    """Safely parse a JSON string field from the database."""
    if value is None:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None
