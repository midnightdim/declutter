"""
Tests for rule execution: dry runs, tag handling on Copy, and isolation
between rules.

Run with:
    python -m pytest tests/test_apply_rules.py -v
"""
from pathlib import Path

import pytest

from declutter.rules import apply_all_rules, apply_rule


MOCK_SETTINGS = {
    "file_types": {"Document": "*.txt"},
    "rules": [],
    "dryrun": False,
    "date_type": 0,
}


def make_rule(folder, action, **kw):
    rule = {
        "id": 1,
        "name": action + " rule",
        "enabled": True,
        "action": action,
        "folders": [str(folder)],
        "conditions": [
            {"type": "name", "filemask": "*.txt", "name_switch": "matches"}
        ],
        "condition_switch": "any",
        "recursive": False,
        "keep_tags": False,
        "overwrite_switch": "increment",
    }
    rule.update(kw)
    return rule


def key(path):
    return str(Path(path))


@pytest.fixture
def tag_db(monkeypatch):
    """In-memory stand-in for the tags database: {path: [tags]}."""
    db = {}

    def set_tags(f, tags):
        db[key(f)] = list(tags)
        return True

    def add_tags(f, tags):
        db[key(f)] = sorted(set(db.get(key(f), []) + list(tags)))

    monkeypatch.setattr("declutter.rules.check_files", lambda: None)
    monkeypatch.setattr("declutter.rules.get_tags", lambda f: db.get(key(f), []))
    monkeypatch.setattr("declutter.rules.set_tags", set_tags)
    monkeypatch.setattr("declutter.rules.add_tags", add_tags)
    monkeypatch.setattr("declutter.rules.remove_all_tags", lambda f: db.pop(key(f), None))
    monkeypatch.setattr("declutter.rules.load_settings", lambda: MOCK_SETTINGS)
    monkeypatch.setattr("declutter.file_utils.load_settings", lambda: MOCK_SETTINGS)
    return db


class TestDryRun:
    """A dry run must report what would happen and change nothing."""

    def test_move(self, tmp_path, tag_db):
        src, out = tmp_path / "src", tmp_path / "out"
        src.mkdir()
        (src / "a.txt").write_text("data")

        _report, details = apply_rule(
            make_rule(src, "Move", target_folder=str(out)), dryrun=True
        )

        assert (src / "a.txt").is_file()
        assert not out.exists()
        assert details == [f"Moved {src / 'a.txt'} to {out / 'a.txt'}"]

    def test_copy_file_with_tags(self, tmp_path, tag_db):
        src, out = tmp_path / "src", tmp_path / "out"
        src.mkdir()
        (src / "a.txt").write_text("data")
        tag_db[key(src / "a.txt")] = ["work"]

        _report, details = apply_rule(
            make_rule(src, "Copy", target_folder=str(out), keep_tags=True), dryrun=True
        )

        assert not out.exists()
        assert tag_db == {key(src / "a.txt"): ["work"]}
        assert details == [f"Copied {src / 'a.txt'} to {out / 'a.txt'}"]


class TestCopyKeepTags:
    def test_skipped_file_does_not_retag_previous_copy(self, tmp_path, tag_db):
        """b.txt already exists at the target, so it is skipped. Its tags must
        not be written onto the copy of a.txt made in the previous iteration."""
        src, out = tmp_path / "src", tmp_path / "out"
        src.mkdir()
        out.mkdir()
        (src / "a.txt").write_text("aaa")
        (src / "b.txt").write_text("bbb")
        (out / "b.txt").write_text("bbb")
        tag_db[key(src / "a.txt")] = ["a"]
        tag_db[key(src / "b.txt")] = ["b"]

        apply_rule(make_rule(src, "Copy", target_folder=str(out), keep_tags=True))

        assert tag_db[key(out / "a.txt")] == ["a"]
        assert key(out / "b.txt") not in tag_db


class TestRuleIsolation:
    def test_broken_rule_does_not_stop_later_rules(self, tmp_path, tag_db, caplog):
        src = tmp_path / "src"
        src.mkdir()
        (src / "c.txt").write_text("data")
        broken = make_rule(src, "Tag", id=1, name="broken", tags=["t1"],
                           ignore_newest=True, ignore_N="abc")
        good = make_rule(src, "Tag", id=2, name="good", tags=["t2"])

        report, _details = apply_all_rules({"rules": [broken, good]})

        assert tag_db[key(src / "c.txt")] == ["t2"]
        assert report["tagged"] == 1
        assert "Rule 'broken' failed and was skipped" in caplog.text
