from __future__ import annotations

import json
import sqlite3
from typing import Any, Dict, List, Optional

from declutter.db import get_conn, ensure_db
from declutter.config import VERSION


def init_store():
    ensure_db()


PRIMITIVE_KEYS = {
    "version": VERSION,
    "current_folder": "",
    "rule_exec_interval": 300.0,
    "dryrun": False,
    "date_type": 0,
    "style": "Fusion",
    "theme": "System",
    "rules_window_geometry": None,
    "tagger_window_geometry": None,
}


def get_setting(key: str, default=None):
    with get_conn() as conn:
        cur = conn.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = cur.fetchone()
        if not row:
            return default
        try:
            return json.loads(row["value"])
        except Exception:
            return row["value"]


def set_setting(key: str, value: Any):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO settings(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, json.dumps(value)),
        )
        conn.commit()


def get_all_settings() -> Dict[str, Any]:
    d = {}
    for k, v in PRIMITIVE_KEYS.items():
        d[k] = get_setting(k, v)
    return d


# File types


def list_file_types() -> List[Dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, name, patterns, list_order FROM file_types ORDER BY list_order, id"
        ).fetchall()
        return [dict(row) for row in rows]


def replace_file_types(items: List[Dict[str, Any]]):
    with get_conn() as conn:
        conn.execute("DELETE FROM file_types")
        order = 1
        for it in items:
            conn.execute(
                "INSERT INTO file_types(name, patterns, list_order) VALUES (?,?,?)",
                (it["name"], it["patterns"], order),
            )
            order += 1
        conn.commit()


# Recent folders (ordered MRU)


def list_recent_folders() -> List[str]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT path FROM recent_folders ORDER BY list_order, id"
        ).fetchall()
        return [row["path"] for row in rows]


def add_recent_folder(path: str, max_items: int = 15):
    with get_conn() as conn:
        conn.execute("DELETE FROM recent_folders WHERE path=?", (path,))
        conn.execute("UPDATE recent_folders SET list_order = list_order + 1")
        conn.execute(
            "INSERT INTO recent_folders(path, list_order) VALUES (?,?)", (path, 1)
        )
        rows = conn.execute(
            "SELECT id FROM recent_folders ORDER BY list_order, id"
        ).fetchall()
        if len(rows) > max_items:
            ids_to_delete = [r["id"] for r in rows[max_items:]]
            conn.executemany(
                "DELETE FROM recent_folders WHERE id=?", [(i,) for i in ids_to_delete]
            )
        conn.commit()


# Rules


def list_rules() -> List[Dict[str, Any]]:
    with get_conn() as conn:
        rules: List[Dict[str, Any]] = []
        rule_rows = conn.execute("SELECT * FROM rules ORDER BY id").fetchall()
        for rr in rule_rows:
            rid = rr["id"]
            folders = [
                r["folder"]
                for r in conn.execute(
                    "SELECT folder FROM rule_folders WHERE rule_id=? ORDER BY id",
                    (rid,),
                ).fetchall()
            ]
            cond_rows = conn.execute(
                "SELECT type, payload FROM rule_conditions WHERE rule_id=? ORDER BY id",
                (rid,),
            ).fetchall()
            conditions: List[Dict[str, Any]] = []
            for cr in cond_rows:
                try:
                    conditions.append(json.loads(cr["payload"]))
                except Exception:
                    conditions.append({"type": cr["type"]})
            tag_rows = conn.execute(
                "SELECT t.name FROM rule_tags rt JOIN tags t ON t.id = rt.tag_id WHERE rt.rule_id=? ORDER BY rt.id",
                (rid,),
            ).fetchall()
            tags = [r["name"] for r in tag_rows]
            rules.append(
                {
                    "id": rr["id"],
                    "name": rr["name"],
                    "enabled": bool(rr["enabled"]),
                    "action": rr["action"],
                    "recursive": bool(rr["recursive"]),
                    "condition_switch": rr["condition_switch"],
                    "keep_tags": bool(rr["keep_tags"]),
                    "keep_folder_structure": bool(rr["keep_folder_structure"]),
                    "target_folder": rr["target_folder"] or "",
                    "target_subfolder": rr["target_subfolder"] or "",
                    "name_pattern": rr["name_pattern"] or "",
                    "overwrite_switch": rr["overwrite_switch"],
                    "ignore_newest": bool(rr["ignore_newest"]),
                    "ignore_N": rr["ignore_N"] or "",
                    "folders": folders,
                    "conditions": conditions,
                    "tags": tags,
                }
            )
        return rules


def _ensure_tag_and_get_id(conn: sqlite3.Connection, tag_name: str) -> int:
    row = conn.execute("SELECT id FROM tags WHERE name=?", (tag_name,)).fetchone()
    if row:
        return row["id"]
    mrow = conn.execute(
        "SELECT COALESCE(MAX(list_order),0) AS m FROM tags WHERE group_id=1"
    ).fetchone()
    next_order = (mrow["m"] if mrow else 0) + 1
    conn.execute(
        "INSERT INTO tags(id, name, list_order, color, group_id) VALUES (NULL, ?, ?, NULL, 1)",
        (tag_name, next_order),
    )
    return conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]


def replace_rules(rules: List[Dict[str, Any]]):
    with get_conn() as conn:
        conn.execute("DELETE FROM rule_tags")
        conn.execute("DELETE FROM rule_conditions")
        conn.execute("DELETE FROM rule_folders")
        conn.execute("DELETE FROM rules")
        for rule in rules:
            vals = (
                int(rule["id"]) if "id" in rule else None,
                rule.get("name", ""),
                1 if rule.get("enabled", True) else 0,
                rule.get("action", ""),
                1 if rule.get("recursive", False) else 0,
                rule.get("condition_switch", "all"),
                1 if rule.get("keep_tags", False) else 0,
                1 if rule.get("keep_folder_structure", False) else 0,
                rule.get("target_folder", ""),
                rule.get("target_subfolder", ""),
                rule.get("name_pattern", ""),
                rule.get("overwrite_switch", "increment name"),
                1 if rule.get("ignore_newest", False) else 0,
                rule.get("ignore_N", ""),
            )
            try:
                conn.execute(
                    "INSERT INTO rules(id,name,enabled,action,recursive,condition_switch,keep_tags,keep_folder_structure,"
                    "target_folder,target_subfolder,name_pattern,overwrite_switch,ignore_newest,ignore_N) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    vals,
                )
            except sqlite3.IntegrityError:
                conn.execute(
                    "INSERT INTO rules(name,enabled,action,recursive,condition_switch,keep_tags,keep_folder_structure,"
                    "target_folder,target_subfolder,name_pattern,overwrite_switch,ignore_newest,ignore_N) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    vals[1:],
                )
            rid = conn.execute(
                "SELECT id FROM rules ORDER BY id DESC LIMIT 1"
            ).fetchone()["id"]

            for folder in rule.get("folders", []):
                conn.execute(
                    "INSERT INTO rule_folders(rule_id, folder) VALUES (?,?)",
                    (rid, folder),
                )

            for cond in rule.get("conditions", []):
                conn.execute(
                    "INSERT INTO rule_conditions(rule_id, type, payload) VALUES (?,?,?)",
                    (rid, cond.get("type", ""), json.dumps(cond)),
                )

            for t in rule.get("tags", []):
                tag_id = _ensure_tag_and_get_id(conn, t)
                conn.execute(
                    "INSERT INTO rule_tags(rule_id, tag_id) VALUES (?,?)", (rid, tag_id)
                )
        conn.commit()


# Compatibility shim


def load_settings(_: Optional[str] = None) -> Dict[str, Any]:
    init_store()
    s = get_all_settings()
    ftypes = list_file_types()
    s["file_types"] = {ft["name"]: ft["patterns"] for ft in ftypes}
    s["rules"] = list_rules()
    s["recent_folders"] = list_recent_folders()
    return s


def save_settings(settings: Dict[str, Any]):
    for k in PRIMITIVE_KEYS.keys():
        if k in settings:
            set_setting(k, settings[k])

    if "file_types" in settings and isinstance(settings["file_types"], dict):
        items = [
            {"name": name, "patterns": pat}
            for name, pat in settings["file_types"].items()
        ]
        replace_file_types(items)

    if "recent_folders" in settings and isinstance(settings["recent_folders"], list):
        with get_conn() as conn:
            conn.execute("DELETE FROM recent_folders")
            order = 1
            for p in settings["recent_folders"]:
                conn.execute(
                    "INSERT INTO recent_folders(path, list_order) VALUES (?,?)",
                    (p, order),
                )
                order += 1
            conn.commit()

    if "rules" in settings and isinstance(settings["rules"], list):
        replace_rules(settings["rules"])
