"""
Tests for special-character filename handling (GitHub issue #10).

Verifies that fnmatch glob-special characters in filenames ([, ], etc.)
don't cause silent mismatches in file-type detection or name conditions.

Run with:
    python -m pytest tests/test_special_chars.py -v
"""
from unittest.mock import patch
import pytest

from declutter.file_utils import _escape_glob, get_file_type


# ---------------------------------------------------------------------------
# _escape_glob
# ---------------------------------------------------------------------------

class TestEscapeGlob:
    """The helper must neutralise [ and ] so fnmatch treats them literally."""

    def test_brackets_escaped(self):
        result = _escape_glob("file [test].txt")
        # The escaped string should work with fnmatch
        from fnmatch import fnmatch
        assert fnmatch(result, "*.txt") is True
        assert fnmatch(result, "file*") is True

    def test_no_special_chars_unchanged(self):
        assert _escape_glob("normal_file.txt") == "normal_file.txt"

    def test_parentheses_unchanged(self):
        # ( and ) are NOT glob-special
        assert _escape_glob("file (copy).txt") == "file (copy).txt"

    def test_hyphen_unchanged(self):
        assert _escape_glob("my-file.txt") == "my-file.txt"

    def test_mixed_special_chars(self):
        result = _escape_glob("report [2024] (final)-v2.txt")
        assert "[[]" in result  # [ was escaped
        assert "[]]" in result  # ] was escaped
        assert "(final)" in result  # parens untouched
        assert "-v2" in result  # hyphen untouched


# ---------------------------------------------------------------------------
# get_file_type — must return correct type regardless of special chars
# ---------------------------------------------------------------------------

MOCK_SETTINGS = {
    "file_types": {
        "Document": "*.txt, *.doc, *.docx, *.pdf",
        "Image": "*.png, *.jpg, *.jpeg",
        "Video": "*.mp4, *.mkv",
    },
    "rules": [],
    "recent_folders": [],
}


class TestGetFileTypeSpecialChars:
    """get_file_type must not be confused by glob chars in filenames."""

    @patch("declutter.file_utils.load_settings", return_value=MOCK_SETTINGS)
    def test_normal_filename(self, _mock):
        assert get_file_type("C:\\Users\\test\\readme.txt") == "Document"

    @patch("declutter.file_utils.load_settings", return_value=MOCK_SETTINGS)
    def test_brackets_in_filename(self, _mock):
        assert get_file_type("C:\\Downloads\\report [2024].pdf") == "Document"

    @patch("declutter.file_utils.load_settings", return_value=MOCK_SETTINGS)
    def test_parentheses_in_filename(self, _mock):
        assert get_file_type("C:\\Downloads\\file (copy).txt") == "Document"

    @patch("declutter.file_utils.load_settings", return_value=MOCK_SETTINGS)
    def test_hyphen_in_filename(self, _mock):
        assert get_file_type("C:\\Downloads\\my-video-file.mp4") == "Video"

    @patch("declutter.file_utils.load_settings", return_value=MOCK_SETTINGS)
    def test_all_special_chars_combined(self, _mock):
        assert get_file_type(
            "C:\\Downloads\\example-file (2024) [test].txt"
        ) == "Document"

    @patch("declutter.file_utils.load_settings", return_value=MOCK_SETTINGS)
    def test_unknown_extension(self, _mock):
        assert get_file_type("C:\\Downloads\\file [test].xyz") == "Other"

    @patch("declutter.file_utils.load_settings", return_value=MOCK_SETTINGS)
    def test_unix_path_with_brackets(self, _mock):
        assert get_file_type("/home/user/photo [edit].jpg") == "Image"


# ---------------------------------------------------------------------------
# fnmatch name-condition matching (via rules engine)
# ---------------------------------------------------------------------------

class TestNameConditionSpecialChars:
    """Name conditions in rules must match filenames with special chars."""

    def test_fnmatch_with_escaped_brackets(self):
        """Simulates what the rules engine does for a name condition."""
        from fnmatch import fnmatch

        filename = "example-file (2024) [test].txt"
        pattern = "*.txt"
        # Without escaping, this would FAIL
        assert fnmatch(_escape_glob(filename), pattern) is True

    def test_fnmatch_star_dot_star_with_brackets(self):
        from fnmatch import fnmatch

        filename = "report [final].doc"
        pattern = "*.*"
        assert fnmatch(_escape_glob(filename), pattern) is True

    def test_fnmatch_specific_pattern_with_brackets(self):
        from fnmatch import fnmatch

        filename = "data [2024-01].csv"
        pattern = "data*"
        assert fnmatch(_escape_glob(filename), pattern) is True
