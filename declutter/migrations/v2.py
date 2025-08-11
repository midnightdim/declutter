from __future__ import annotations

import json
import logging
import os
import sqlite3
import time

from declutter.config import SETTINGS_FILE
from . import set_schema_version


def migration_2(conn: sqlite3.Connection):
    c = conn.cursor()
    logging.info("Running migration to schema v2")

    # Create new tables
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

    # Import legacy settings.json if present
    legacy = None
    try:
        if os.path.isfile(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                legacy = json.load(f)
    except Exception as e:
        logging.exception(f"Failed to read legacy settings.json: {e}")

    if legacy:
        _import_legacy(conn, legacy)
        # Archive legacy file after successful migration
        try:
            ts = time.strftime("%Y%m%d-%H%M%S")
            backup = SETTINGS_FILE + f".migrated-{ts}"
            os.replace(SETTINGS_FILE, backup)
            logging.info(f"Migrated settings.json -> {backup}")
        except Exception as e:
            logging.exception(f"Failed to archive settings.json: {e}")

    set_schema_version(conn, 2)


def _import_legacy(conn: sqlite3.Connection, s: dict):
    # Settings primitives
    primitives = {
        'version': s.get('version'),
        'current_folder': s.get('current_folder', ''),
        'current_drive': s.get('current_drive', ''),
        'rule_exec_interval': s.get('rule_exec_interval', 300.0),
        'dryrun': s.get('dryrun', False),
        'date_type': s.get('date_type', 0),
        'style': s.get('style', 'Fusion'),
    }
    for k, v in primitives.items():
        conn.execute(
            "INSERT INTO settings(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (k, json.dumps(v)),
        )

    # file_types dict -> rows
    file_types = s.get('file_types', {})
    order = 1
    for name, patterns in file_types.items():
        try:
            conn.execute(
                "INSERT OR IGNORE INTO file_types(name, patterns, list_order) VALUES (?,?,?)",
                (name, patterns, order)
            )
        except Exception as e:
            logging.exception(f"file_type insert failed for {name}: {e}")
        order += 1

    # recent_folders ordered list
    recent = s.get('recent_folders', [])
    conn.execute("DELETE FROM recent_folders")
    order = 1
    for path in recent:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO recent_folders(path, list_order) VALUES (?,?)",
                (path, order)
            )
        except Exception as e:
            logging.exception(f"recent_folders insert failed for {path}: {e}")
        order += 1

    # rules and nested entities
    rules = s.get('rules', [])
    for rule in rules:
        rule_id = _insert_rule_row(conn, rule)
        # folders
        for folder in rule.get('folders', []):
            conn.execute(
                "INSERT INTO rule_folders(rule_id, folder) VALUES (?,?)",
                (rule_id, folder)
            )
        # conditions
        for cond in rule.get('conditions', []):
            conn.execute(
                "INSERT INTO rule_conditions(rule_id, type, payload) VALUES (?,?,?)",
                (rule_id, cond.get('type', ''), json.dumps(cond))
            )
        # tags: names -> ids
        for tname in rule.get('tags', []):
            tag_id = _ensure_tag_and_get_id(conn, tname)
            conn.execute(
                "INSERT INTO rule_tags(rule_id, tag_id) VALUES (?,?)",
                (rule_id, tag_id)
            )

    conn.commit()


def _insert_rule_row(conn: sqlite3.Connection, rule: dict) -> int:
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
        conn.execute(
            f"INSERT INTO rules({','.join(cols)}) VALUES ({placeholders})", vals
        )
        # If we inserted with explicit id, use it
        if vals[0] is not None:
            return int(vals[0])
    except sqlite3.IntegrityError:
        # Id conflict; fall back to auto-id
        pass
    # Insert without id
    conn.execute(
        "INSERT INTO rules(name,enabled,action,recursive,condition_switch,keep_tags,keep_folder_structure,"
        "target_folder,target_subfolder,name_pattern,overwrite_switch,ignore_newest,ignore_N) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        vals[1:]
    )
    return conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]


def _ensure_tag_and_get_id(conn: sqlite3.Connection, tag_name: str) -> int:
    row = conn.execute("SELECT id FROM tags WHERE name=?", (tag_name,)).fetchone()
    if row:
        return row["id"]
    # Append to default group (group_id=1)
    mrow = conn.execute("SELECT COALESCE(MAX(list_order), 0) AS m FROM tags WHERE group_id=1").fetchone()
    next_order = (mrow["m"] if mrow else 0) + 1
    conn.execute(
        "INSERT INTO tags(id, name, list_order, color, group_id) VALUES (NULL, ?, ?, NULL, 1)",
        (tag_name, next_order)
    )
    return conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
