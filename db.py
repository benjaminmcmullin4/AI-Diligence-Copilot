"""SQLite database for storing analyses and loading demo samples."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import DB_PATH, DEMO_DIR, DEMO_FILES


# ── Private helpers ────────────────────────────────────────────────────────

def _connect(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Open a WAL-mode SQLite connection with Row factory."""
    path = str(db_path or DB_PATH)
    # Ensure parent directory exists
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


# ── Public API ─────────────────────────────────────────────────────────────

def init_db(db_path: str | Path | None = None) -> None:
    """Create tables if they don't exist."""
    conn = _connect(db_path)
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


def save_analysis(
    analysis_id: str,
    data: dict[str, Any],
    db_path: str | Path | None = None,
) -> None:
    """Insert or update an analysis record."""
    conn = _connect(db_path)
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
        conn.execute(
            f"INSERT INTO analyses ({cols}) VALUES ({placeholders})",
            list(data.values()),
        )
    conn.commit()
    conn.close()


def get_analysis(
    analysis_id: str,
    db_path: str | Path | None = None,
) -> dict[str, Any] | None:
    """Fetch a single analysis by ID."""
    conn = _connect(db_path)
    row = conn.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)


def list_analyses(
    include_demo: bool = True,
    db_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """List all analyses ordered by creation date."""
    conn = _connect(db_path)
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


def delete_analysis(
    analysis_id: str,
    db_path: str | Path | None = None,
) -> None:
    """Delete an analysis by ID."""
    conn = _connect(db_path)
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


# ── Demo sample loader ─────────────────────────────────────────────────────

def load_demo_samples(db_path: str | Path | None = None) -> None:
    """Load demo analyses from JSON files into DB if they don't already exist."""
    resolved_path = db_path or DB_PATH
    init_db(resolved_path)

    for filename in DEMO_FILES:
        filepath = DEMO_DIR / filename
        if not filepath.exists():
            continue

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        analysis_id = data.get("id", filename.replace(".json", ""))
        if get_analysis(analysis_id, db_path=resolved_path) is not None:
            continue

        save_analysis(
            analysis_id,
            {
                "company_name": data["company_name"],
                "business_model": data["business_model"],
                "status": "completed",
                "request_json": json.dumps(data.get("request", {})),
                "condensed_json": json.dumps(data.get("condensed", {})),
                "analysis_json": json.dumps(data.get("analysis", {})),
                "memo_json": json.dumps(data.get("memo", {})),
                "memo_markdown": data.get("memo_markdown", ""),
                "is_demo": 1,
            },
            db_path=resolved_path,
        )
