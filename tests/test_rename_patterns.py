"""
Tests for Rename action name patterns (<filename>, <folder>, <replace:A:B>).

Reproduces the bug where a pattern consisting only of a <replace:...> token
resolves to an empty name, so the file is "renamed" onto its own parent
folder and ends up as "<parent> (1)", "<parent> (2)", ... one level up.

Run with:
    python -m pytest tests/test_rename_patterns.py -v
"""
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from declutter.file_utils import advanced_move
from declutter.rules import apply_rule, is_valid_filename, resolve_name_pattern


MOCK_SETTINGS = {
    "file_types": {"Video": "*.mp4, *.mkv"},
    "rules": [],
    "dryrun": False,
    "date_type": 0,
}


def make_rename_rule(folder, name_pattern, recursive=False):
    return {
        "id": 1,
        "name": "test rename rule",
        "enabled": True,
        "action": "Rename",
        "folders": [str(folder)],
        "name_pattern": name_pattern,
        "conditions": [
            {"type": "name", "filemask": "*.mp4", "name_switch": "matches"}
        ],
        "condition_switch": "any",
        "recursive": recursive,
        "keep_tags": False,
        "overwrite_switch": "increment",
    }


@pytest.fixture
def no_db(monkeypatch):
    """Stub out everything that would touch the tags database."""
    for name, ret in (
        ("check_files", None),
        ("get_tags", []),
        ("remove_all_tags", None),
        ("set_tags", True),
    ):
        monkeypatch.setattr(
            "declutter.rules." + name, lambda *a, _r=ret, **kw: _r
        )
    monkeypatch.setattr("declutter.rules.load_settings", lambda: MOCK_SETTINGS)
    monkeypatch.setattr(
        "declutter.file_utils.load_settings", lambda: MOCK_SETTINGS
    )


class TestReplaceToken:
    """<replace:A:B> must edit the file name, never the file's location."""

    def test_replace_with_filename_token(self, tmp_path, no_db):
        """The documented form: <filename><replace:A:B>."""
        folder = tmp_path / "Ant Videos"
        folder.mkdir()
        (folder / "clip - WEBSITE.COM.mp4").write_text("data")

        apply_rule(make_rename_rule(folder, "<filename><replace: - WEBSITE.COM:>"))

        assert (folder / "clip.mp4").is_file()
        assert not (folder / "clip - WEBSITE.COM.mp4").exists()

    def test_replace_only_pattern(self, tmp_path, no_db):
        """GitHub bug report: pattern is just <replace: - WEBSITE.COM:>.

        Expected: substring removed from the file name, file stays put.
        Buggy behaviour: newname == "" -> target is the parent folder itself
        -> file lands next to it as "Ant Videos (1)".
        """
        folder = tmp_path / "Ant Videos"
        folder.mkdir()
        (folder / "clip - WEBSITE.COM.mp4").write_text("data")

        report, _details = apply_rule(
            make_rename_rule(folder, "<replace: - WEBSITE.COM:>")
        )

        # Nothing may appear next to the watched folder
        assert sorted(p.name for p in tmp_path.iterdir()) == ["Ant Videos"]
        assert (folder / "clip.mp4").is_file()
        assert (folder / "clip.mp4").read_text() == "data"
        assert report["renamed"] == 1

    def test_multiple_replace_tokens(self, tmp_path, no_db):
        """Two <replace:> tokens in one pattern must both apply."""
        folder = tmp_path / "Ant Videos"
        folder.mkdir()
        (folder / "my-clip [ad].mp4").write_text("data")

        apply_rule(
            make_rename_rule(folder, "<filename><replace: [ad]:><replace:-:_>")
        )

        assert (folder / "my_clip.mp4").is_file()

    def test_empty_result_leaves_file_alone(self, tmp_path, no_db):
        """A pattern that resolves to nothing must be a no-op, not a move."""
        folder = tmp_path / "Ant Videos"
        folder.mkdir()
        (folder / "clip.mp4").write_text("data")

        report, _details = apply_rule(make_rename_rule(folder, "<replace:clip.mp4:>"))

        assert sorted(p.name for p in tmp_path.iterdir()) == ["Ant Videos"]
        assert (folder / "clip.mp4").is_file()
        assert report["renamed"] == 0

    def test_no_data_loss_on_empty_name(self, tmp_path, no_db):
        """The reported case verbatim: two files, folder named 'Ant Videos'.

        Buggy behaviour: the first file becomes 'Ant Videos (1)' one level up
        and the second one is silently deleted (advanced_move compares the
        file's size against the parent folder's size, sees a match, and drops
        the source).
        """
        folder = tmp_path / "Ant Videos"
        folder.mkdir()
        (folder / "a - WEBSITE.COM.mp4").write_text("aaaa")
        (folder / "b - WEBSITE.COM.mp4").write_text("bbbbbbbb")

        apply_rule(make_rename_rule(folder, "<replace: - WEBSITE.COM:>"))

        assert sorted(p.name for p in tmp_path.iterdir()) == ["Ant Videos"]
        assert (folder / "a.mp4").read_text() == "aaaa"
        assert (folder / "b.mp4").read_text() == "bbbbbbbb"

    def test_dot_result_leaves_file_alone(self, tmp_path, no_db):
        """'.' resolves to the parent folder just like an empty name."""
        folder = tmp_path / "Ant Videos"
        folder.mkdir()
        (folder / "clip.mp4").write_text("data")

        report, _details = apply_rule(make_rename_rule(folder, "<replace:clip.mp4:.>"))

        assert sorted(p.name for p in tmp_path.iterdir()) == ["Ant Videos"]
        assert (folder / "clip.mp4").is_file()
        assert report["renamed"] == 0

    def test_dryrun_reports_skip_for_invalid_name(self, tmp_path, no_db):
        folder = tmp_path / "Ant Videos"
        folder.mkdir()
        (folder / "clip.mp4").write_text("data")

        _report, details = apply_rule(
            make_rename_rule(folder, "<replace:clip.mp4:>"), dryrun=True
        )

        assert len(details) == 1 and details[0].startswith("Skipped renaming")

    def test_tags_follow_incremented_name(self, tmp_path, no_db, monkeypatch):
        """On a name collision tags must go to 'name (1)', not to 'name'."""
        folder = tmp_path / "Ant Videos"
        folder.mkdir()
        (folder / "clip.mp4").write_text("existing")
        (folder / "clip - WEBSITE.COM.mp4").write_text("new, longer content")
        tagged = {}
        monkeypatch.setattr("declutter.rules.get_tags", lambda f: ["keep"])
        monkeypatch.setattr(
            "declutter.rules.set_tags", lambda f, tags: tagged.update({str(f): tags})
        )

        apply_rule(make_rename_rule(folder, "<replace: - WEBSITE.COM:>"))

        assert (folder / "clip (1).mp4").is_file()
        assert tagged == {str(folder / "clip (1).mp4"): ["keep"]}


class TestResolveNamePattern:
    """Pure name resolution, no file system involved."""

    PATH = Path("Work") / "my-clip [ad].mp4"

    @pytest.mark.parametrize("pattern, expected", [
        ("<filename>", "my-clip [ad].mp4"),
        ("<folder> - <filename>", "Work - my-clip [ad].mp4"),
        ("<replace: [ad]:>", "my-clip.mp4"),
        ("  <replace: [ad]:>  ", "my-clip.mp4"),
        ("<filename><replace: [ad]:><replace:-:_>", "my_clip.mp4"),
        # literal text must survive, it is not a "replace only" pattern
        ("backup_<replace: [ad]:>", "backup_"),
        ("backup_<filename><replace: [ad]:>", "backup_my-clip.mp4"),
        # fixed names still work
        ("archive.zip", "archive.zip"),
        # an empty search string is ignored instead of exploding the name
        ("<filename><replace::x>", "my-clip [ad].mp4"),
    ])
    def test_patterns(self, pattern, expected):
        assert resolve_name_pattern(pattern, self.PATH) == expected

    def test_tokens_in_file_name_are_not_interpreted(self):
        path = Path("Work") / "a<replace:a:b>"
        assert resolve_name_pattern("<filename>", path) == "a<replace:a:b>"

    @pytest.mark.parametrize("name", ["", ".", "..", "a/b"])
    def test_invalid_names(self, name):
        assert not is_valid_filename(name)

    def test_valid_name(self):
        assert is_valid_filename("clip (1).mp4")


class TestAdvancedMoveFileVsFolder:
    """A file and a folder with the same name are never duplicates."""

    def test_empty_file_onto_empty_folder_is_not_deleted(self, tmp_path, no_db):
        (tmp_path / "src").mkdir()
        (tmp_path / "dst" / "Backup").mkdir(parents=True)
        (tmp_path / "src" / "Backup").write_text("")

        result = advanced_move(tmp_path / "src" / "Backup", tmp_path / "dst" / "Backup")

        assert Path(result) == tmp_path / "dst" / "Backup (1)"
        assert (tmp_path / "dst" / "Backup (1)").is_file()
        assert (tmp_path / "dst" / "Backup").is_dir()

    def test_overwrite_never_replaces_folder_with_file(self, tmp_path, no_db):
        (tmp_path / "src").mkdir()
        (tmp_path / "dst" / "Backup").mkdir(parents=True)
        (tmp_path / "dst" / "Backup" / "important.txt").write_text("keep me")
        (tmp_path / "src" / "Backup").write_text("file")

        advanced_move(tmp_path / "src" / "Backup", tmp_path / "dst" / "Backup", overwrite=True)

        assert (tmp_path / "dst" / "Backup" / "important.txt").read_text() == "keep me"
        assert (tmp_path / "dst" / "Backup (1)").is_file()
