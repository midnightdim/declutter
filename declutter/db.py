from __future__ import annotations

import os
import sqlite3
import json
import time
from pathlib import Path
import logging

from declutter.config import DB_FILE, SETTINGS_FILE, VERSION

SCHEMA_VERSION = 2  # current DB schema version


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_db():
    Path(Path(DB_FILE).parent).mkdir(parents=True, exist_ok=True)
    with get_conn() as conn:
        c = conn.cursor()
        _create_legacy_tag_tables(c)
        c.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        conn.commit()
        current = _get_schema_version(conn)
        if current < 2:
            _migration_2(conn)
            current = 2
        if current != SCHEMA_VERSION:
            logging.info(f"DB schema at version {current}, expected {SCHEMA_VERSION}. No further migrations implemented yet.")
        _set_setting(conn, 'version', VERSION)


def _create_legacy_tag_tables(c: sqlite3.Cursor):
    c.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            filepath VARCHAR NOT NULL UNIQUE
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL UNIQUE,
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
            name VARCHAR NOT NULL UNIQUE,
            list_order INTEGER NOT NULL,
            widget_type INTEGER NOT NULL DEFAULT 0,
            name_shown INTEGER DEFAULT 1
        )
    """)
    c.execute("SELECT COUNT(1) FROM tag_groups")
    row = c.fetchone()
    count = row[0] if row else 0
    if count == 0:
        c.execute("INSERT INTO tag_groups VALUES (1, 'Default', 1, 0, 0)")


def _get_setting(conn: sqlite3.Connection, key: str, default=None):
    cur = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cur.fetchone()
    if not row:
        return default
    try:
        return json.loads(row["value"])
    except Exception:
        return row["value"]


def _set_setting(conn: sqlite3.Connection, key: str, value):
    payload = json.dumps(value)
    conn.execute(
        "INSERT INTO settings(key,value) VALUES(?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, payload),
    )
    conn.commit()


def _get_schema_version(conn: sqlite3.Connection) -> int:
    v = _get_setting(conn, 'db_schema_version', None)
    if v is None:
        return 1  # legacy or uninitialized
    try:
        return int(v)
    except Exception:
        return 1


def _migration_2(conn: sqlite3.Connection):
    c = conn.cursor()
    logging.info("Running migration to schema v2")

    c.execute("""
        CREATE TABLE IF NOT EXISTS file_types (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            patterns TEXT NOT NULL,
            list_order INTEGER NOT NULL DEFAULT 1
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS recent_folders (
            id INTEGER PRIMARY KEY,
            path TEXT UNIQUE NOT NULL,
            added_at INTEGER,
            list_order INTEGER NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1,
            action TEXT NOT NULL,
            recursive INTEGER NOT NULL DEFAULT 0,
            condition_switch TEXT NOT NULL DEFAULT 'all',
            keep_tags INTEGER NOT NULL DEFAULT 0,
            keep_folder_structure INTEGER NOT NULL DEFAULT 0,
            target_folder TEXT,
            target_subfolder TEXT,
            name_pattern TEXT,
            overwrite_switch TEXT NOT NULL DEFAULT 'increment name',
            ignore_newest INTEGER NOT NULL DEFAULT 0,
            ignore_N TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS rule_folders (
            id INTEGER PRIMARY KEY,
            rule_id INTEGER NOT NULL REFERENCES rules(id) ON DELETE CASCADE,
            folder TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS rule_conditions (
            id INTEGER PRIMARY KEY,
            rule_id INTEGER NOT NULL REFERENCES rules(id) ON DELETE CASCADE,
            type TEXT NOT NULL,
            payload TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS rule_tags (
            id INTEGER PRIMARY KEY,
            rule_id INTEGER NOT NULL REFERENCES rules(id) ON DELETE CASCADE,
            tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE
        )
    """)
    conn.commit()

    legacy = None
    try:
        if os.path.isfile(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                legacy = json.load(f)
    except Exception as e:
        logging.exception(f"Failed to read legacy settings.json: {e}")

    if legacy:
        _import_legacy_settings(conn, legacy)
        try:
            ts = time.strftime("%Y%m%d-%H%M%S")
            backup = SETTINGS_FILE + f".migrated-{ts}"
            os.replace(SETTINGS_FILE, backup)
            logging.info(f"Legacy settings.json migrated and archived as {backup}")
        except Exception as e:
            logging.exception(f"Failed to archive settings.json: {e}")

    _set_setting(conn, 'db_schema_version', 2)


def _ensure_tag_and_get_id(conn: sqlite3.Connection, tag_name: str) -> int:
    # Try find
    cur = conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
    row = cur.fetchone()
    if row:
        return row["id"]
    # Create in default group (1) and append to end of list_order for that group
    cur = conn.execute("SELECT COALESCE(MAX(list_order), 0) FROM tags WHERE group_id = 1")
    max_order = cur.fetchone()[0] if cur.fetchone() is None else 0  # safe default, but we’ll re-fetch properly
    # Re-fetch correctly (sqlite Row mishandling above)
    cur = conn.execute("SELECT COALESCE(MAX(list_order), 0) AS m FROM tags WHERE group_id = 1")
    max_order = cur.fetchone()["m"]
    conn.execute("INSERT INTO tags(id, name, list_order, color, group_id) VALUES (NULL, ?, ?, NULL, 1)",
                 (tag_name, max_order + 1))
    return conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]


def _import_legacy_settings(conn: sqlite3.Connection, s: dict):
    # primitives, file_types, recent_folders unchanged ...

    rules = s.get('rules', [])
    for rule in rules:
        cols = (
            'id', 'name', 'enabled', 'action', 'recursive', 'condition_switch',
            'keep_tags', 'keep_folder_structure', 'target_folder', 'target_subfolder',
            'name_pattern', 'overwrite_switch', 'ignore_newest', 'ignore_N'
        )
        vals = (
            int(rule.get('id')) if 'id' in rule else None,
            rule.get('name', ''),
            1 if rule.get('enabled', True) else 0,
            rule.get('action', ''),
            1 if rule.get('recursive', False) else 0,
            rule.get('condition_switch', 'all'),
            1 if rule.get('keep_tags', False) else 0,
            1 if rule.get('keep_folder_structure', False) else 0,
            rule.get('target_folder', ''),
            rule.get('target_subfolder', ''),
            rule.get('name_pattern', ''),
            rule.get('overwrite_switch', 'increment name'),
            1 if rule.get('ignore_newest', False) else 0,
            rule.get('ignore_N', ''),
        )
        placeholders = ",".join(["?"] * len(cols))
        try:
            conn.execute(f"INSERT INTO rules({','.join(cols)}) VALUES ({placeholders})", vals)
        except sqlite3.IntegrityError:
            cols_wo_id = [c for c in cols if c != 'id']
            vals_wo_id = [val for i, val in enumerate(vals) if cols[i] != 'id']
            conn.execute(
                f"INSERT INTO rules({','.join(cols_wo_id)}) VALUES ({','.join(['?']*len(cols_wo_id))})",
                vals_wo_id
            )
        cur = conn.execute("SELECT id FROM rules ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        if not row:
            logging.error(f"Failed to resolve rule id for rule {rule.get('name')}")
            continue
        rule_id = row["id"]

        for folder in rule.get('folders', []):
            try:
                conn.execute("INSERT INTO rule_folders(rule_id, folder) VALUES (?,?)", (rule_id, folder))
            except Exception as e:
                logging.exception(f"Failed to insert rule folder for rule {rule_id}: {e}")

        for cond in rule.get('conditions', []):
            cond_type = cond.get('type', '')
            try:
                conn.execute(
                    "INSERT INTO rule_conditions(rule_id, type, payload) VALUES (?,?,?)",
                    (rule_id, cond_type, json.dumps(cond))
                )
            except Exception as e:
                logging.exception(f"Failed to insert rule condition for rule {rule_id}: {e}")

        # Map tag names to tag_id in tags table
        for t in rule.get('tags', []):
            try:
                tag_id = _ensure_tag_and_get_id(conn, t)
                conn.execute("INSERT INTO rule_tags(rule_id, tag_id) VALUES (?,?)", (rule_id, tag_id))
            except Exception as e:
                logging.exception(f"Failed to insert rule tag for rule {rule_id}: {e}")

    conn.commit()
