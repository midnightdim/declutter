from __future__ import annotations

import sqlite3
from pathlib import Path

from declutter.config import DB_FILE, VERSION
from declutter.migrations import run as run_migrations


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_db():
    # Ensure folder exists
    Path(Path(DB_FILE).parent).mkdir(parents=True, exist_ok=True)
    with get_conn() as conn:
        # Run migrations to bring DB to latest schema
        run_migrations(conn)
        # Store current app version (informational)
        conn.execute(
            "INSERT INTO settings(key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            ("version", f"\"{VERSION}\""),
        )
        conn.commit()
