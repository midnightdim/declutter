"""
Minimal tests for the scheduler-flag lifecycle (GitHub issue #9).

These tests verify that:
1. show_tray_message is a real method of RulesWindow (not nested inside closeEvent)
2. The service_runs flag resets correctly after the service thread finishes
3. declutter_service.run() emits the signal even when apply_all_rules raises

Run with:
    python -m pytest tests/test_scheduler_flag.py -v
"""
import importlib
import inspect
import sys
import types
from unittest.mock import patch, MagicMock

import pytest


# ---------------------------------------------------------------------------
# Helpers to import the module under test without needing a running QApplication
# ---------------------------------------------------------------------------

def _get_declutter_service_class():
    """Import and return the declutter_service class from src.DeClutter."""
    mod = importlib.import_module("src.DeClutter")
    return mod.declutter_service


def _get_rules_window_class():
    """Import and return the RulesWindow class from src.DeClutter."""
    mod = importlib.import_module("src.DeClutter")
    return mod.RulesWindow


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestShowTrayMessageIsMethod:
    """show_tray_message must be a proper method of RulesWindow, not a nested function."""

    def test_show_tray_message_exists_on_class(self):
        RulesWindow = _get_rules_window_class()
        assert hasattr(RulesWindow, "show_tray_message"), (
            "show_tray_message is missing from RulesWindow — "
            "it may still be nested inside closeEvent."
        )

    def test_show_tray_message_is_function(self):
        RulesWindow = _get_rules_window_class()
        attr = getattr(RulesWindow, "show_tray_message", None)
        assert callable(attr), "show_tray_message should be callable"

    def test_show_tray_message_not_inside_close_event(self):
        """Verify via source inspection that show_tray_message is not indented under closeEvent."""
        RulesWindow = _get_rules_window_class()
        close_src = inspect.getsource(RulesWindow.closeEvent)
        assert "show_tray_message" not in close_src, (
            "show_tray_message appears inside closeEvent source — "
            "it should be an independent method."
        )


class TestServiceRunsFlag:
    """The service_runs flag must be reset after the service thread completes."""

    def test_show_tray_message_resets_service_runs(self):
        """Calling show_tray_message should set service_runs to False."""
        RulesWindow = _get_rules_window_class()

        # Build a minimal fake instance with mock attrs used by show_tray_message
        fake = MagicMock(spec=RulesWindow)
        fake.service_runs = True
        fake.service_run_details = []
        fake.trayIcon = MagicMock()

        # Call unbound method on the fake
        RulesWindow.show_tray_message(fake, "test message", ["detail"])
        assert fake.service_runs is False


class TestDeclutterServiceExceptionSafety:
    """declutter_service.run() must emit the signal even when apply_all_rules raises."""

    @patch("src.DeClutter.load_settings", return_value={
        "rules": [], "dryrun": False, "file_types": {}, "recent_folders": [],
    })
    @patch("src.DeClutter.apply_all_rules", side_effect=RuntimeError("boom"))
    def test_signal_emitted_on_exception(self, mock_apply, mock_load):
        DeclutterService = _get_declutter_service_class()

        # Create a mock that has the same interface as declutter_service
        svc = MagicMock(spec=DeclutterService)
        svc.signals = MagicMock()

        # Call the real run method on the mock instance
        DeclutterService.run(svc)

        # Signal must have been emitted even though apply_all_rules raised
        svc.signals.signal1.emit.assert_called_once_with("", [])

    @patch("src.DeClutter.load_settings", return_value={
        "rules": [], "dryrun": False, "file_types": {}, "recent_folders": [],
    })
    @patch("src.DeClutter.apply_all_rules", return_value=({}, []))
    def test_signal_emitted_on_success(self, mock_apply, mock_load):
        DeclutterService = _get_declutter_service_class()

        svc = MagicMock(spec=DeclutterService)
        svc.signals = MagicMock()

        DeclutterService.run(svc)

        # Signal must have been emitted on success too
        svc.signals.signal1.emit.assert_called_once()
