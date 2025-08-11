from __future__ import annotations

import json
import logging
import os
import sqlite3
import time

from declutter.config import SETTINGS_FILE

# Increment when adding a new migration module (v3, v4, ...)
LATEST_SCHEMA_VERSION = 2


def run(conn: sqlite3.Connection):
    # Ensure core tables exist to hold settings and legacy tags
    _create_core_tables(conn)
    current = _get_schema_version(conn)
    if current < 2:
        from .v2 import migration_2
        migration_2(conn)
        current = 2

    if current != LATEST_SCHEMA_VERSION:
        logging.info(f"DB schema at version {current}, expected {LATEST_SCHEMA_VERSION}.")

    # Ensure version key exists at least (value will be overwritten by db.ensure_db)
    conn.execute(
        "INSERT INTO settings(key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO NOTHING",
        ("version", json.dumps("")),
    )
    conn.commit()


def _create_core_tables(conn: sqlite3.Connection):
    c = conn.cursor()
    # Legacy tag tables (idempotent)
    c.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            filepath TEXT NOT NULL UNIQUE
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            list_order INTEGER NOT NULL DEFAULT 1,
            color INTEGER,
            group_id INTEGER NOT NULL DEFAULT 1
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS file_tags (
            file_id INTEGER,
            tag_id INTEGER,
            timestamp INTEGER
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tag_groups (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            list_order INTEGER NOT NULL,
            widget_type INTEGER NOT NULL DEFAULT 0,
            name_shown INTEGER DEFAULT 1
        )
    """)
    # Seed default tag group if empty
    row = c.execute("SELECT COUNT(1) AS cnt FROM tag_groups").fetchone()
    if (row["cnt"] if row else 0) == 0:
        c.execute("INSERT INTO tag_groups VALUES (1, 'Default', 1, 0, 0)")

    # Settings table (for schema version and app settings)
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()


def _get_schema_version(conn: sqlite3.Connection) -> int:
    try:
        cur = conn.execute("SELECT value FROM settings WHERE key='db_schema_version'")
        row = cur.fetchone()
        if not row:
            return 1
        # value stored as JSON text
        val = json.loads(row["value"])
        return int(val)
    except Exception:
        return 1


def set_schema_version(conn: sqlite3.Connection, v: int):
    conn.execute(
        "INSERT INTO settings(key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        ('db_schema_version', json.dumps(v)),
    )
    conn.commit()
