from __future__ import annotations

import sqlite3
from pathlib import Path
import shutil
import os
import time
import json
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
    db_dir = Path(DB_FILE).parent
    db_dir.mkdir(parents=True, exist_ok=True)

    # Capture whether the DB file existed before this call
    pre_existing_file = Path(DB_FILE).exists()

    with get_conn() as conn:
        # Decide current schema version from DB (may be missing on fresh DB)
        try:
            cur = conn.execute("SELECT value FROM settings WHERE key='db_schema_version'")
            row = cur.fetchone()
            current_version = int(json.loads(row["value"])) if row else 1
        except Exception:
            current_version = 1

        # Import here to avoid circular import at module load
        from declutter.migrations import LATEST_SCHEMA_VERSION

        # Backup only if:
        # - DB file already existed before this call (not first run)
        # - And an upgrade is actually needed
        if pre_existing_file and current_version < LATEST_SCHEMA_VERSION:
            try:
                ts = time.strftime("%Y%m%d-%H%M%S")
                backup_path = f"{DB_FILE}.backup-{ts}"
                if not os.path.exists(backup_path):
                    shutil.copy2(DB_FILE, backup_path)
            except Exception:
                pass  # best-effort backup

        # Run migrations to bring DB to latest schema (safe on first run too)
        run_migrations(conn)

        # Store current app version (informational)
        conn.execute(
            "INSERT INTO settings(key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            ("version", f"\"{VERSION}\""),
        )
        conn.commit()
