import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple

from declutter.config import DB_FILE
from declutter.file_utils import quick_file_fingerprint
from declutter.store import load_settings, save_settings

TAGS_CACHE = {}

# ---------- DB helpers ----------

def _ensure_file_row(conn: sqlite3.Connection, filepath: str) -> Tuple[int, str]:
    """
    Ensure a row exists in files for filepath.
    Returns (file_id, normalized_filepath). Always stores normalized lowercase path and hash.
    """
    norm = os.path.normpath(filepath).lower()
    cur = conn.execute("SELECT id, hash FROM files WHERE filepath = ?", (norm,))
    row = cur.fetchone()
    if row:
        # if hash missing, compute and update once
        if not row["hash"]:
            fhash = quick_file_fingerprint(norm)
            if fhash:
                conn.execute("UPDATE files SET hash=? WHERE id=?", (fhash, row["id"]))
        return row["id"], norm

    # insert new row with hash
    fhash = quick_file_fingerprint(norm)
    conn.execute("INSERT INTO files(id, filepath, hash) VALUES (NULL, ?, ?)", (norm, fhash))
    file_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
    return file_id, norm

def _get_tag_id(conn: sqlite3.Connection, tag: str) -> int:
    cur = conn.execute("SELECT id FROM tags WHERE name = ?", (tag,))
    row = cur.fetchone()
    if row:
        return row[0]
    # create tag at end of default group
    cur = conn.execute("SELECT COALESCE(MAX(list_order),0) FROM tags WHERE group_id=1")
    max_order = cur.fetchone()[0]
    conn.execute("INSERT INTO tags VALUES (null, ?, ?, null, ?)", (tag, max_order + 1, 1))
    return conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]

# ---------- Public API (with hashing integrated) ----------

def tag_set_color(tag, color):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE tags set color = ? WHERE name = ?", (color, tag))
    conn.commit()
    conn.close()

def tag_get_color(tag):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT color FROM tags WHERE name = ?", (tag,))
    row = c.fetchone()[0]
    conn.close()
    return row

def create_tag(tag, group_id=1):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT max(list_order) from tags WHERE tags.group_id=?", (group_id,))
    row = c.fetchone()[0]
    count = 1 if row is None else row + 1
    c.execute("INSERT INTO tags VALUES (null, ?, ?, null, ?)", (tag, count, group_id))
    tag_id = c.lastrowid
    conn.commit()
    conn.close()
    return tag_id

def move_tag(tag, direction):  # Moves tag up or down in lists
    tags = get_all_tags()
    if tag == tags[0] and direction == "up":
        return
    if tag == tags[-1] and direction == "down":
        return
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    ind = tags.index(tag)
    if direction == "down":
        swap = tags[ind + 1]
        tags[ind], tags[ind + 1] = swap, tag
    elif direction == "up":
        swap = tags[ind - 1]
        tags[ind], tags[ind - 1] = swap, tag
    for t in tags:
        c.execute("UPDATE tags set list_order = ? WHERE name = ?", (tags.index(t) + 1, t))
    conn.commit()
    conn.close()

def rename_group(old_group, new_group):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE tag_groups set name = ? WHERE name = ?", (new_group, old_group))
    conn.commit()
    conn.close()

def rename_tag(old_tag, new_tag):
    tagged_files = get_files_by_tag(old_tag)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if new_tag in get_all_tags():
        delete_tag(old_tag)
    else:
        c.execute("UPDATE tags set name = ? WHERE name = ?", (new_tag, old_tag))
    conn.commit()
    conn.close()

    # updating tagged files
    for f in tagged_files:
        add_tag(f, new_tag)

    # updating rules and conditions
    settings = load_settings()
    for r in settings['rules']:
        if old_tag in r['tags']:
            r['tags'].remove(old_tag)
            r['tags'].append(new_tag)
        for cond in r['conditions']:
            if cond.get('type') == 'tags' and old_tag in cond.get('tags', []):
                cond['tags'].remove(old_tag)
                cond['tags'].append(new_tag)
    save_settings(settings)

def set_tags(filename, tags):  # stores complete tag set for file
    filename = os.path.normpath(filename).lower()
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        file_id, norm = _ensure_file_row(conn, filename)

        c.execute("DELETE FROM file_tags WHERE file_tags.file_id = ?", (file_id,))
        for t in tags:
            tag_id = _get_tag_id(conn, t)
            c.execute("INSERT INTO file_tags VALUES (?,?,?)", (file_id, tag_id, datetime.now()))
        conn.commit()
        conn.close()

        TAGS_CACHE[norm] = tags
        return True
    except Exception as e:
        logging.exception(e)
        return False

def get_tags(filename):
    filename = os.path.normpath(filename).lower()
    if filename in TAGS_CACHE:
        return TAGS_CACHE[filename]
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    tags = [f[0] for f in c.execute(
        "SELECT tags.name FROM file_tags JOIN tags on tag_id = tags.id "
        "WHERE file_tags.file_id = (SELECT id from files WHERE filepath = ?) "
        "order by tags.group_id, tags.list_order", (filename,))]
    if not tags:
        c.execute("DELETE FROM files WHERE filepath = ?", (filename,))
        conn.commit()
    conn.close()
    TAGS_CACHE[filename] = tags
    return tags

# returns list of tuples [(tag, group_id)]
def get_tags_by_group_ids(filename):
    filename = os.path.normpath(filename).lower()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    tags = [f for f in c.execute(
        "SELECT name, group_id FROM file_tags JOIN tags on tag_id = tags.id "
        "WHERE file_tags.file_id = (SELECT id from files WHERE filepath = ?)", (filename,))]
    conn.close()
    return tags

def add_tags(filename, tags):
    cur_tags = get_tags(filename)
    set_tags(filename, list(set(tags + cur_tags)))

def add_tag(filename, tag):
    add_tags(filename, [tag])

def remove_tags(filename, tags):
    filename = os.path.normpath(filename).lower()
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    file_id, _ = _ensure_file_row(conn, filename)
    for t in tags:
        tag_id = _get_tag_id(conn, t)
        c.execute("DELETE FROM file_tags WHERE file_tags.file_id = ? AND file_tags.tag_id = ?", (file_id, tag_id))
    conn.commit()
    conn.close()
    if filename in TAGS_CACHE:
        del TAGS_CACHE[filename]

def remove_all_tags(filename):
    filename = os.path.normpath(filename).lower()
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Keep files row; just remove associations
    c.execute("SELECT id from files WHERE filepath = ?", (filename,))
    row = c.fetchone()
    if not row:
        conn.close()
        TAGS_CACHE[filename] = []
        return
    file_id = row[0]
    c.execute("DELETE FROM file_tags WHERE file_tags.file_id = ?", (file_id,))
    conn.commit()
    conn.close()
    TAGS_CACHE[filename] = []

def clear_tags_cache():
    global TAGS_CACHE
    TAGS_CACHE = {}

def get_all_files_from_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    files = [f[0] for f in c.execute("SELECT filepath FROM files")]
    conn.close()
    return files

def get_all_tags():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    tags = [f[0] for f in c.execute("SELECT name FROM tags ORDER by list_order")]
    conn.close()
    return tags

def get_all_tags_by_group_id(id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    tags = [f[0] for f in c.execute("SELECT name FROM tags WHERE group_id=?", (id,))]
    conn.close()
    return tags

def get_all_tag_groups():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    groups = [f[0] for f in c.execute("SELECT name FROM tag_groups ORDER by list_order")]
    conn.close()
    return groups

def get_tag_groups(filename):
    filename = os.path.normpath(filename).lower()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    tags = [f[0] for f in c.execute(
        "SELECT name from tag_groups WHERE id in (SELECT tags.group_id FROM file_tags JOIN tags on tag_id = tags.id "
        "WHERE file_tags.file_id = (SELECT id from files WHERE filepath = ?) order by tags.group_id)", (filename,))]
    conn.close()
    return tags

def get_files_by_tags(tags: List[str]):
    if not tags:
        return []
    all_files = get_files_by_tag(tags[0])
    if all_files:
        for t in tags[1:]:
            all_files = list(set(all_files).intersection(set(get_files_by_tag(t))))
        if not all_files:
            return []
        else:
            return all_files
    return []

def get_files_by_tag(tag):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    files = [f[0] for f in c.execute(
        "SELECT files.filepath FROM file_tags JOIN files on file_id = files.id "
        "WHERE file_tags.tag_id = (SELECT id from tags WHERE name = ?)", (tag,))]
    conn.close()
    return files

def remove_tag(filename, tag):
    remove_tags(filename, [tag])

def delete_tag(tag):  # Removes tag from the database
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM file_tags WHERE file_tags.tag_id IN (SELECT id from tags WHERE name = ?)", (tag,))
    c.execute("DELETE FROM tags WHERE name = ?", (tag,))
    conn.commit()
    conn.close()

def delete_group(group_id, keep_tags):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM tag_groups WHERE id = ?", (group_id,))
    if keep_tags:
        c.execute("UPDATE tags set group_id = 1 WHERE group_id = ?", (group_id,))
    else:
        c.execute("DELETE FROM file_tags WHERE file_tags.tag_id IN (SELECT id from tags WHERE group_id = ?)", (group_id,))
        c.execute("DELETE FROM tags WHERE group_id = ?", (group_id,))
    conn.commit()
    conn.close()

def get_tags_and_groups():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    groups = c.execute("SELECT id, name, list_order, widget_type, name_shown FROM tag_groups ORDER BY list_order")
    tree = {}
    for g in groups.fetchall():
        tree[g[1]] = {'id': g[0], 'list_order': g[2], 'widget_type': g[3], 'name_shown': g[4], 'type': 'group', 'name': g[1]}
        tags = c.execute("SELECT id, name, list_order, color FROM tags WHERE group_id=? ORDER BY list_order", (g[0],))
        tree[g[1]]['tags'] = []
        for t in tags.fetchall():
            tree[g[1]]['tags'].append({'type': 'tag', 'id': t[0], 'name': t[1], 'list_order': t[2], 'color': t[3], 'group_id': g[0]})
    conn.close()
    return tree

def create_group(name, widget_type=0, name_shown=1):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT max(list_order) from tag_groups")
    row = c.fetchone()[0]
    count = 1 if row is None else row + 1
    c.execute("INSERT INTO tag_groups VALUES (null, ?, ?, ?, ?)", (name, count, widget_type, name_shown))
    group_id = c.lastrowid
    conn.commit()
    conn.close()
    return group_id

def set_group_type(group, widget_type):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE tag_groups SET widget_type = ? WHERE name = ?", (widget_type, group))
    conn.commit()
    conn.close()

def move_tag_to_group(tag_id, group_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT max(list_order) from tags where group_id=?", (group_id,))
    row = c.fetchone()[0]
    count = 1 if row is None else row + 1
    c.execute("UPDATE tags set (group_id, list_order) = (?,?) WHERE id = ?", (group_id, count, tag_id))
    conn.commit()
    conn.close()

# tags are in format {'name':name,'id':id,'list_order':list_order,'group_id':group_id}
def move_tag_to_tag(tag1, tag2, position):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT list_order,group_id from tags WHERE id = ?", (tag2['id'],))
    row = c.fetchone()
    new_list_order = row[0] if int(position) == 1 else row[0] + 1
    group = row[1]
    c.execute("SELECT id from tags WHERE (group_id,list_order) = (?,?)", (group, new_list_order))
    row = c.fetchone()
    if row is not None:
        c.execute("UPDATE tags set list_order = list_order+1 WHERE group_id = ? and list_order >= ?", (group, new_list_order))
    c.execute("UPDATE tags set (list_order,group_id) = (?,?) WHERE id = ?", (new_list_order, group, tag1['id']))
    conn.commit()
    conn.close()

def move_group_to_group(group1, group2, position):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT list_order from tag_groups WHERE id = ?", (group2['id'],))
    row = c.fetchone()
    new_list_order = row[0] if int(position) == 1 else row[0] + 1
    c.execute("SELECT id from tag_groups WHERE list_order = ?", (new_list_order,))
    row = c.fetchone()
    if row is not None:
        c.execute("UPDATE tag_groups set list_order = list_order+1 WHERE list_order >= ?", (new_list_order,))
    c.execute("UPDATE tag_groups set list_order = ? WHERE id = ?", (new_list_order, group1['id']))
    conn.commit()
    conn.close()

def get_file_tags_by_group(group, filename):
    filename = os.path.normpath(filename).lower()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM tag_groups WHERE name = ?", (group,))
    row = c.fetchone()
    tags = []
    if row is not None:
        group_id = row[0]
        tags = [f[0] for f in c.execute(
            "SELECT tags.name FROM file_tags JOIN tags on tag_id = tags.id "
            "WHERE file_tags.file_id = (SELECT id from files WHERE filepath = ?) AND tags.group_id = ?",
            (filename, group_id))]
    conn.close()
    return tags

def check_files():
    """
    Reconcile DB with filesystem.
    - If a file path exists but normalized differs, normalize path in DB.
    - If a file at stored path is missing, try to locate by hash nearby (same drive or under current_folder).
    - If not found, keep the DB row and log a warning (do not delete).
    """
    files = get_all_files_from_db()
    if not files:
        return

    # Choose a search root from settings for fallback scanning
    settings = load_settings()
    root = settings.get('current_folder') or str(Path.home())

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    for f in files:
        try:
            # Normalize known path
            norm = os.path.normpath(f).lower()
            if os.path.exists(f):
                actual = os.path.normpath(f).lower()
                if actual != norm:
                    c.execute("UPDATE files SET filepath=? WHERE filepath=?", (actual, norm))
                # ensure hash present
                cur = c.execute("SELECT id, hash FROM files WHERE filepath=?", (actual,))
                row = cur.fetchone()
                if row and not row["hash"]:
                    fhash = quick_file_fingerprint(actual)
                    if fhash:
                        c.execute("UPDATE files SET hash=? WHERE id=?", (fhash, row["id"]))
                continue

            # Missing at stored path: try to rediscover by hash
            cur = c.execute("SELECT id, hash FROM files WHERE filepath=?", (norm,))
            row = cur.fetchone()
            if not row:
                continue
            file_id = row["id"]
            fhash = row["hash"]

            if not fhash:
                # Try compute hash from original path if partially accessible (unlikely), else skip discovery
                # We keep the DB row; user can run a full reconcile later
                logging.warning(f"Missing file without hash; cannot reconcile: {f}")
                continue

            # Try to find a file with the same hash under root
            found = _find_by_hash(fhash, root)
            if found:
                new_path = os.path.normpath(found).lower()
                c.execute("UPDATE files SET filepath=? WHERE id=?", (new_path, file_id))
                logging.info(f"Reconciled moved file: {f} -> {new_path}")
            else:
                logging.warning(f"Tagged file missing; not deleted from DB (awaiting reconcile): {f}")

        except Exception as e:
            logging.exception(f"check_files error for {f}: {e}")

    conn.commit()
    conn.close()

def _find_by_hash(target_hash: str, root: str) -> Optional[str]:
    """
    Shallow scan under root to find a file with matching quick fingerprint.
    Limits work by skipping very deep recursion or hidden/system dirs.
    """
    try:
        root_path = Path(root)
        if not root_path.exists():
            return None
        # Simple bounded scan: depth 3 by default
        max_depth = 3
        root_parts = len(root_path.parts)
        for p in root_path.rglob("*"):
            try:
                if not p.is_file():
                    continue
                # depth limit
                if len(p.parts) - root_parts > max_depth:
                    continue
                # Skip very large number of files – optional throttle could be added
                h = quick_file_fingerprint(str(p))
                if h == target_hash:
                    return str(p)
            except Exception:
                continue
    except Exception:
        return None
    return None

def has_any_tag(path: str) -> bool:
    norm = os.path.normpath(path).lower()
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT id FROM files WHERE filepath = ?", (norm,)).fetchone()
        if not row:
            return False
        file_id = row["id"] if isinstance(row, sqlite3.Row) else row
        cur = conn.execute("SELECT 1 FROM file_tags WHERE file_id = ? LIMIT 1", (file_id,))
        return cur.fetchone() is not None 