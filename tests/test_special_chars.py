"""
Tests for special-character filename handling.

Verifies that fnmatch glob-special characters in filenames ([, ], etc.)
don't cause silent mismatches in file-type detection or name conditions.

Run with:
    python -m pytest tests/test_special_chars.py -v
"""
from unittest.mock import patch
import pytest
from fnmatch import fnmatch
from declutter.file_utils import get_file_type, get_actual_filename

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
        filename = "example-file (2024) [test].txt"
        pattern = "*.txt"
        # fnmatch natively handles brackets in FILENAME as literal characters on most platforms
        # (or at least consistently enough for our purposes)
        assert fnmatch(filename, pattern) is True

    def test_fnmatch_star_dot_star_with_brackets(self):
        filename = "report [final].doc"
        pattern = "*.*"
        assert fnmatch(filename, pattern) is True

    def test_fnmatch_specific_pattern_with_brackets(self):
        filename = "data [2024-01].csv"
        pattern = "data*"
        assert fnmatch(filename, pattern) is True

class TestGetActualFilename:
    """get_actual_filename must handle brackets when converting case on Windows."""

    def test_brackets_in_real_filename(self, tmp_path):
        # Create a file with brackets on logical disk
        # (tmp_path is guaranteed to exist)
        d = tmp_path / "subdir"
        d.mkdir()
        # Create file with Mixed Case and brackets
        f = d / "TeSt[1].txt"
        f.write_text("content")
        
        # Query with lowercase
        query = str(d / "test[1].txt")
        
        # The function should find the real file
        result = get_actual_filename(query)
        
        # Result should match the actual file name on disk
        # Note: on Windows valid filesystems are case-preserving.
        from pathlib import Path
        assert Path(result).name == "TeSt[1].txt"
