import sys
import os
from copy import deepcopy
from time import time
import logging
import webbrowser
import requests
from PySide6.QtGui import QIcon, QAction, QPalette, QColor
from PySide6.QtWidgets import (
    QApplication,
    QSystemTrayIcon,
    QMenu,
    QDialog,
    QTableWidgetItem,
    QAbstractScrollArea,
    QTableWidgetSelectionRange,
    QMainWindow,
    QMessageBox,
    QStyleFactory,
)
from PySide6.QtCore import Qt, QObject, QThread, Signal, Slot, QTimer
from src.rule_edit_window import RuleEditWindow
from src.settings_dialog import SettingsDialog
from src.ui.ui_rules_window import Ui_rulesWindow
from src.ui.ui_list_dialog import Ui_listDialog
from declutter.config import VERSION, LOG_FILE
from declutter.store import load_settings, save_settings
from declutter.rules import apply_all_rules, apply_rule, get_rule_by_id

from src.declutter_tagger import TaggerWindow


class RulesWindow(QMainWindow):
    """Main application window for managing decluttering rules."""

    def __init__(self):
        super(RulesWindow, self).__init__()
        self.ui = Ui_rulesWindow()
        self.ui.setupUi(self)

        self.minimizeAction = QAction()
        self.maximizeAction = QAction()
        self.restoreAction = QAction()
        self.quitAction = QAction()

        self.trayIcon = QSystemTrayIcon()
        self.trayIconMenu = QMenu()

        self.create_actions()
        self.create_tray_icon()
        self.trayIcon.show()
        self.settings = load_settings()
        if "style" in self.settings.keys():
            # Apply style and palette together
            style = self.settings.get("style", "Fusion")
            palette = self.settings.get("palette", "System/Default")
            apply_style_and_palette(QApplication.instance(), style, palette)

        self.ui.addRule.clicked.connect(self.add_rule)
        self.load_rules()
        self.ui.rulesTable.cellDoubleClicked.connect(self.edit_rule)
        self.ui.deleteRule.clicked.connect(self.delete_rule)
        self.ui.applyRule.clicked.connect(self.apply_rule)
        self.setWindowIcon(QIcon(":/images/icons/DeClutter.ico"))
        self.trayIcon.messageClicked.connect(self.message_clicked)
        self.trayIcon.activated.connect(self.tray_activated)
        self.trayIcon.setToolTip(
            "DeClutter runs every "
            + str(float(self.settings["rule_exec_interval"] / 60))
            + " minute(s)"
        )
        self.service_run_details = []
        # TBD: self.start_thread() - check if this is needed

        # Hide UI elements related to rule management (TBD: Re-evaluate visibility based on user roles/features)
        self.ui.addRule.setVisible(False)
        self.ui.applyRule.setVisible(False)
        self.ui.deleteRule.setVisible(False)
        self.ui.moveUp.setVisible(False)
        self.ui.moveDown.setVisible(False)

        self.ui.actionAdd.triggered.connect(self.add_rule)
        self.ui.actionDelete.triggered.connect(self.delete_rule)
        self.ui.actionExecute.triggered.connect(self.apply_rule)
        self.ui.actionOpen_log_file.triggered.connect(self.open_log_file)
        self.ui.actionClear_log_file.triggered.connect(self.clear_log_file)
        self.ui.actionSettings.triggered.connect(self.show_settings)
        self.ui.actionAbout.triggered.connect(self.show_about)
        self.ui.actionOpen_Tagger.triggered.connect(self.show_tagger)
        self.tagger = TaggerWindow()
        self.ui.actionManage_Tags.triggered.connect(self.tagger.manage_tags)

        self.ui.actionMove_up.triggered.connect(self.move_rule_up)
        self.ui.actionMove_down.triggered.connect(self.move_rule_down)

        self.service_runs = False

        self.timer = QTimer(self)
        self.timer.setInterval(int(self.settings["rule_exec_interval"] * 1000))
        self.timer.timeout.connect(self.start_thread)
        self.timer.start()

        self.instanced_thread = new_version_checker(self)
        self.instanced_thread.start()
        self.instanced_thread.version.connect(self.suggest_download)

    def suggest_download(self, version):
        """Suggests downloading a new version of the application if available."""
        if version:
            try:
                from packaging.version import Version

                current_version = Version(load_settings()["version"])
                # Normalize GitHub version (remove 'v' prefix if present)
                latest_version = Version(version.lstrip("v"))

                if latest_version > current_version:
                    reply = QMessageBox.question(
                        self,
                        f"New version: {latest_version}",
                        r"There's a new version of DeClutter available. Download now?",
                        QMessageBox.Yes | QMessageBox.No,
                    )
                    if reply == QMessageBox.Yes:
                        try:
                            webbrowser.open(
                                "https://github.com/midnightdim/declutter/releases/latest"
                            )
                        except Exception as e:
                            logging.exception(f"exception {e}")
            except ImportError:
                logging.error("packaging library not available for version comparison")
            except Exception as e:
                logging.exception(f"Version comparison failed: {e}")

    def tray_activated(self, reason):
        """Handles activation of the system tray icon."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.setVisible(True)

    def move_rule_up(self):
        """Moves the selected rule up in the list."""
        rule_idx = self.ui.rulesTable.selectedIndexes()[0].row()
        if rule_idx:
            rule_id = int(self.settings["rules"][rule_idx]["id"])
            self.settings["rules"][rule_idx]["id"] = self.settings["rules"][
                rule_idx - 1
            ]["id"]
            self.settings["rules"][rule_idx - 1]["id"] = rule_id

            rules = deepcopy(self.settings["rules"])
            rule_ids = [int(r["id"]) for r in rules if "id" in r.keys()]
            rule_ids.sort()

            self.settings["rules"] = []
            i = 0
            for rule_id in rule_ids:
                i += 1
                rule = get_rule_by_id(rule_id, rules)
                rule["id"] = i  # renumbering rules
                self.settings["rules"].append(rule)

            save_settings(self.settings)
            self.load_rules()
            self.ui.rulesTable.selectRow(rule_idx - 1)

    def move_rule_down(self):
        """Moves the selected rule down in the list."""
        rule_idx = self.ui.rulesTable.selectedIndexes()[0].row()
        if rule_idx < self.ui.rulesTable.rowCount() - 1:
            rule_id = int(self.settings["rules"][rule_idx]["id"])
            self.settings["rules"][rule_idx]["id"] = self.settings["rules"][
                rule_idx + 1
            ]["id"]
            self.settings["rules"][rule_idx + 1]["id"] = rule_id

            rules = deepcopy(self.settings["rules"])
            rule_ids = [int(r["id"]) for r in rules if "id" in r.keys()]
            rule_ids.sort()

            self.settings["rules"] = []
            i = 0
            for rule_id in rule_ids:
                i += 1
                rule = get_rule_by_id(rule_id, rules)
                rule["id"] = i  # renumbering rules
                self.settings["rules"].append(rule)

            save_settings(self.settings)
            self.load_rules()
            self.ui.rulesTable.selectRow(rule_idx + 1)

    def show_about(self):
        """Shows the application's About box."""
        QMessageBox.about(
            self,
            "About DeClutter",
            "DeClutter version "
            + str(VERSION)
            + "\nhttps://github.com/midnightdim/declutter\nAuthor: Dmitry Beloglazov\nTelegram: @beloglazov",
        )

    def show_settings(self):
        """Shows the settings dialog."""
        settings_window = SettingsDialog()
        if settings_window.exec():
            self.settings = load_settings()
            self.trayIcon.setToolTip(
                "DeClutter runs every "
                + str(float(self.settings["rule_exec_interval"] / 60))
                + " minute(s)"
            )
            self.timer.setInterval(int(self.settings["rule_exec_interval"] * 1000))

            # Apply style and palette after settings change
            style = self.settings.get("style", "Fusion")
            palette = self.settings.get("palette", "System/Default")
            apply_style_and_palette(QApplication.instance(), style, palette)

    def change_style(self, style_name):
        """Changes the application's style."""
        QApplication.setStyle(QStyleFactory.create(style_name))

    def open_log_file(self):
        """Opens the log file."""
        os.startfile(LOG_FILE)

    def clear_log_file(self):
        """Clears the log file."""
        reply = QMessageBox.question(
            self,
            "Warning",
            "Are you sure you want to clear the log?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                with open(LOG_FILE, "w"):
                    pass
            except Exception as e:
                logging.exception(f"exception {e}")

    def message_clicked(self):
        """Shows a dialog with details about the last service run."""
        msgBox = QDialog(self)
        msgBox.ui = Ui_listDialog()
        msgBox.ui.setupUi(msgBox)
        msgBox.setWindowTitle("Rule executed")
        affected = self.service_run_details
        if affected:
            msgBox.ui.label.setText(
                str(len(affected)) + " file(s) affected by this rule:"
            )
            msgBox.ui.listWidget.addItems(affected)
        else:
            msgBox.ui.listWidget.setVisible(False)
            msgBox.ui.label.setText("No files affected by this rule.")
        msgBox.exec()
        self.service_run_details = []

    def start_thread(self):
        """Starts the declutter service thread if it is not already running."""
        if not self.service_runs:
            self.service_runs = True
            instanced_thread = declutter_service(self)
            instanced_thread.start()
        else:
            logging.debug("Service still running, skipping the scheduled exec")

    def add_rule(self):
        """Opens the rule edit window to add a new rule."""
        self.rule_window = RuleEditWindow()
        if self.rule_window.exec():
            rule = self.rule_window.rule
            rule["id"] = (
                max([int(r["id"]) for r in self.settings["rules"] if "id" in r.keys()])
                + 1
                if self.settings["rules"]
                else 1
            )
            self.settings["rules"].append(rule)
        save_settings(self.settings)
        self.load_rules()

    def edit_rule(self, r, c):
        """Opens the rule edit window to edit the selected rule."""
        if c == 1:  # Enabled/Disabled is clicked
            self.settings["rules"][r]["enabled"] = not self.settings["rules"][r][
                "enabled"
            ]
            save_settings(self.settings)
        else:
            rule = deepcopy(self.settings["rules"][r])
            self.rule_window = RuleEditWindow()
            self.rule_window.load_rule(rule)
            if self.rule_window.exec():
                self.settings["rules"][r] = self.rule_window.rule
        save_settings(self.settings)
        self.load_rules()

    def delete_rule(self):
        """Deletes the selected rule(s)."""
        del_indexes = [r.row() for r in self.ui.rulesTable.selectedIndexes()]

        if del_indexes:
            del_names = [
                r["name"]
                for r in self.settings["rules"]
                if self.settings["rules"].index(r) in del_indexes
            ]

            reply = QMessageBox.question(
                self,
                "Warning",
                "Are you sure you want to delete selected rules:\n"
                + "\n".join(del_names)
                + "\n?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                for ind in sorted(del_indexes, reverse=True):
                    del self.settings["rules"][ind]
                    self.ui.rulesTable.removeRow(ind)

                self.ui.rulesTable.setRangeSelected(
                    QTableWidgetSelectionRange(
                        0,
                        0,
                        self.ui.rulesTable.rowCount() - 1,
                        self.ui.rulesTable.columnCount() - 1,
                    ),
                    False,
                )

    def apply_rule(self):
        """Applies the selected rule."""
        selected = self.ui.rulesTable.selectedIndexes()
        if not selected:
            QMessageBox.warning(self, "No rule selected", "Please select a rule first.")
            return

        rule = deepcopy(self.settings["rules"][selected[0].row()])
        rule["enabled"] = True
        report, affected = apply_rule(rule)

        msgBox = QDialog(self)
        msgBox.ui = Ui_listDialog()
        msgBox.ui.setupUi(msgBox)
        msgBox.setWindowTitle("Rule executed")

        if affected:
            msgBox.ui.label.setText(
                str(len(affected)) + " file(s) affected by this rule:"
            )
            msgBox.ui.listWidget.addItems(affected)
        else:
            msgBox.ui.listWidget.setVisible(False)
            msgBox.ui.label.setText("No files affected by this rule.")
        msgBox.exec()

    def load_rules(self):
        """Loads settings (including rules) from the store and populates the rules table."""
        self.settings = load_settings()

        rules = [(int(r["id"]), r) for r in self.settings["rules"] if "id" in r]
        rules.sort(key=lambda y: y[0])

        self.ui.rulesTable.setRowCount(len(rules))
        for i, (_, rule) in enumerate(rules):
            self.ui.rulesTable.setItem(i, 0, QTableWidgetItem(rule["name"]))
            self.ui.rulesTable.setItem(
                i, 1, QTableWidgetItem("Enabled" if rule["enabled"] else "Disabled")
            )
            self.ui.rulesTable.setItem(i, 2, QTableWidgetItem(rule["action"]))
            self.ui.rulesTable.setItem(
                i, 3, QTableWidgetItem(",".join(rule["folders"]))
            )

        self.ui.rulesTable.setColumnWidth(0, 200)
        self.ui.rulesTable.setColumnWidth(1, 80)
        self.ui.rulesTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

    def create_actions(self):
        """Creates the actions for the tray icon menu."""
        self.showRulesWindow = QAction("Rules", self)
        self.showRulesWindow.triggered.connect(self.showNormal)

        self.showTaggerWindow = QAction("Tagger", self)
        self.showTaggerWindow.triggered.connect(self.show_tagger)

        self.showSettingsWindow = QAction("Settings", self)
        self.showSettingsWindow.triggered.connect(self.show_settings)

        self.quitAction = QAction("Quit", self)
        self.quitAction.triggered.connect(QApplication.quit)

    def create_tray_icon(self):
        """Creates the system tray icon and its context menu."""
        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction(self.showRulesWindow)
        self.trayIconMenu.addAction(self.showTaggerWindow)
        self.trayIconMenu.addAction(self.showSettingsWindow)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)

        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)
        self.trayIcon.setIcon(QIcon(":/images/icons/DeClutter.ico"))
        self.trayIcon.setVisible(True)
        self.trayIcon.show()

    def setVisible(self, visible):
        """Sets the visibility of the main window and updates the tray icon actions accordingly."""
        self.minimizeAction.setEnabled(visible)
        self.maximizeAction.setEnabled(not self.isMaximized())
        self.restoreAction.setEnabled(self.isMaximized() or not visible)
        super().setVisible(visible)

    def show_tagger(self):
        """Shows the tagger window."""
        self.tagger.show()
        self.tagger.init_tag_checkboxes()  # TBD this doesn't look like the best solution  # TBD this doesn't look like the best solution

    @Slot(str, list)
    def show_tray_message(self, message, details):
        """Shows a message in the system tray."""
        if message:
            self.trayIcon.showMessage(
                "DeClutter",
                message,
                QSystemTrayIcon.Information,
                15000,
            )

        self.service_run_details = details if details else self.service_run_details
        self.service_runs = False

def make_fusion_light_palette() -> QPalette:
    p = QPalette()
    # Use Qt default-derived light palette (optionally tweak)
    # Keeping it minimal to avoid unintended overrides.
    return p  # default is light

def make_fusion_dark_palette() -> QPalette:
    p = QPalette()
    # Common dark Fusion palette roles (Qt docs and community examples)
    p.setColor(QPalette.Window, QColor(53, 53, 53))
    p.setColor(QPalette.WindowText, Qt.white)
    p.setColor(QPalette.Base, QColor(35, 35, 35))
    p.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    p.setColor(QPalette.ToolTipBase, Qt.white)
    p.setColor(QPalette.ToolTipText, Qt.white)
    p.setColor(QPalette.Text, Qt.white)
    p.setColor(QPalette.Button, QColor(53, 53, 53))
    p.setColor(QPalette.ButtonText, Qt.white)
    p.setColor(QPalette.BrightText, Qt.red)
    p.setColor(QPalette.Link, QColor(42, 130, 218))
    p.setColor(QPalette.Highlight, QColor(42, 130, 218))
    p.setColor(QPalette.HighlightedText, Qt.black)
    return p

def apply_style_and_palette(app: QApplication, style_name: str, palette_name: str):
    QApplication.setStyle(QStyleFactory.create(style_name))
    if style_name == "Fusion":
        if palette_name == "Fusion Dark":
            app.setPalette(make_fusion_dark_palette())
        elif palette_name == "Fusion Light":
            app.setPalette(make_fusion_light_palette())
        else:
            app.setPalette(QPalette())  # System/default
    else:
        # Non-Fusion: reset to default so native theming takes over
        app.setPalette(QPalette())


class service_signals(QObject):
    signal1 = Signal(str, list)


class declutter_service(QThread):
    """A QThread subclass for running DeClutter rules in the background."""

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.signals = service_signals()
        self.signals.signal1.connect(parent.show_tray_message)
        self.starting_seconds = time()

    def run(self):
        # TBD: Add more detailed logging for rule processing
        details = []
        report, details = apply_all_rules(load_settings())
        msg = ""
        for key in report.keys():
            msg += key + ": " + str(report[key]) + "\n" if report[key] > 0 else ""
        if len(msg) > 0:
            msg = "Processed files and folders:\n" + msg
        self.signals.signal1.emit(msg, details)


class new_version_checker(QThread):
    """A QThread subclass for checking for new versions of DeClutter."""

    version = Signal(str)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)

    def run(self):
        try:
            response = requests.get(
                "https://api.github.com/repos/midnightdim/declutter/releases/latest"
            )
            if response.status_code == 200:
                latest_version = response.json()["tag_name"]
                self.version.emit(latest_version.strip())
        except Exception as e:
            logging.exception(f"exception {e}")


def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    QApplication.setQuitOnLastWindowClosed(False)
    from declutter.store import init_store

    init_store()
    logging.info("DeClutter started")
    app.setWindowIcon(QIcon(":/images/icons/DeClutter.ico"))

    window = RulesWindow()
    window.show()
    window.setWindowTitle("DeClutter (beta) " + VERSION)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
