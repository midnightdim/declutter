"""
Tests for the rules window and the rule editor that don't need a running
QApplication.

Needs the generated UI modules (pyside6-uic --from-imports design/X.ui -o src/ui/ui_X.py).

Run with:
    python -m pytest tests/test_rules_window.py -v
"""
from unittest.mock import MagicMock, patch

import pytest

from src.DeClutter import RulesWindow
from src.rule_edit_window import validate_rule


def fake_window(selected_rows, n_rules=5):
    fake = MagicMock(spec=RulesWindow)
    fake.settings = {"rules": [{"id": i + 1, "name": f"rule {i}"} for i in range(n_rules)]}
    fake.ui = MagicMock()
    fake.ui.rulesTable.selectedIndexes.return_value = [
        MagicMock(**{"row.return_value": r}) for r in selected_rows
    ]
    fake.ui.rulesTable.rowCount.return_value = n_rules
    fake.ui.rulesTable.columnCount.return_value = 4
    return fake


def delete_with_answer(fake, answer):
    with patch("src.DeClutter.QMessageBox") as box, \
         patch("src.DeClutter.save_settings") as save:
        box.question.return_value = getattr(box, answer)
        RulesWindow.delete_rule(fake)
    return save


def rule_names(fake):
    return [r["name"] for r in fake.settings["rules"]]


class TestDeleteRule:
    def test_full_row_deletes_one_rule_and_saves(self):
        """A full-row selection yields one index per column (4 here)."""
        fake = fake_window([1, 1, 1, 1])

        save = delete_with_answer(fake, "Yes")

        assert rule_names(fake) == ["rule 0", "rule 2", "rule 3", "rule 4"]
        save.assert_called_once_with(fake.settings)

    def test_several_rows(self):
        fake = fake_window([1, 1, 3, 3])

        delete_with_answer(fake, "Yes")

        assert rule_names(fake) == ["rule 0", "rule 2", "rule 4"]

    def test_cancel_changes_nothing(self):
        fake = fake_window([1, 1, 1, 1])

        save = delete_with_answer(fake, "No")

        assert len(fake.settings["rules"]) == 5
        save.assert_not_called()


class TestValidateRule:
    @staticmethod
    def rule(**kw):
        rule = {
            "name": "r", "folders": ["C:\\x"], "conditions": [{"type": "name"}],
            "action": "Tag", "name_pattern": "", "target_folder": "",
            "target_subfolder": "", "ignore_newest": True, "ignore_N": "3",
        }
        rule.update(kw)
        return rule

    @pytest.mark.parametrize("n", ["3", " 3 ", "0"])
    def test_valid_ignore_n(self, n):
        assert validate_rule(self.rule(ignore_N=n)) == ""

    @pytest.mark.parametrize("n", ["", "abc", "-1", "2.5", "\u00b2"])
    def test_invalid_ignore_n(self, n):
        assert "whole number" in validate_rule(self.rule(ignore_N=n))

    def test_ignore_n_unchecked_when_option_is_off(self):
        assert validate_rule(self.rule(ignore_newest=False, ignore_N="abc")) == ""
