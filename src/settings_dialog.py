import sys
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QTableWidgetItem,
    QApplication,
    QStyleFactory,
    QMessageBox,
)
from PySide6.QtCore import Qt
from declutter.store import load_settings, save_settings
from src.startup import is_enabled as startup_is_enabled, enable as startup_enable, disable as startup_disable
from declutter.i18n import THEMES, combo_value, set_combo_value, setup_combo, setup_language_combo, tr

from src.ui.ui_settings_dialog import Ui_settingsDialog


class SettingsDialog(QDialog):
    def __init__(self):
        super(SettingsDialog, self).__init__()
        self.ui = Ui_settingsDialog()
        self.ui.setupUi(self)
        self._setup_language_controls()
        self.initialize()

    def _setup_language_controls(self):
        self.languageLabel = QLabel(self)
        self.languageComboBox = QComboBox(self)
        layout = QHBoxLayout()
        layout.addWidget(self.languageLabel)
        layout.addWidget(self.languageComboBox)
        layout.addStretch()
        self.ui.verticalLayout_2.insertLayout(3, layout)

    def apply_localization(self):
        self.setWindowTitle(tr("settings.title"))
        self.ui.tabWidget.setTabText(0, tr("settings.main_tab"))
        self.ui.tabWidget.setTabText(1, tr("settings.date_tab"))
        self.ui.tabWidget.setTabText(2, tr("settings.file_types_tab"))
        self.ui.label_2.setText(tr("settings.process_interval"))
        self.ui.label_3.setText(tr("settings.minutes"))
        self.ui.label_4.setText(tr("settings.style"))
        self.ui.themeLabel.setText(tr("settings.theme"))
        self.languageLabel.setText(tr("settings.language"))
        self.ui.startAtLoginCheckBox.setText(tr("settings.launch_startup"))
        self.ui.dateDefGroupBox.setTitle(tr("settings.date_title"))
        self.ui.label.setText(tr("settings.date_question"))
        self.ui.radioButton.setText(tr("date_option.0"))
        self.ui.radioButton_2.setText(tr("date_option.1"))
        self.ui.radioButton_3.setText(tr("date_option.2"))
        self.ui.radioButton_4.setText(tr("date_option.3"))
        self.ui.radioButton_5.setText(tr("date_option.4"))
        self.ui.fileTypesTable.horizontalHeaderItem(0).setText(tr("column.name"))
        self.ui.fileTypesTable.horizontalHeaderItem(1).setText(tr("column.filemask"))
        self.ui.addFileTypeButton.setText(tr("button.add_file_type"))
        self.ui.label_5.setText(tr("file_types.note"))

        ok_button = self.ui.buttonBox.button(QDialogButtonBox.Ok)
        cancel_button = self.ui.buttonBox.button(QDialogButtonBox.Cancel)
        if ok_button:
            ok_button.setText(tr("button.ok"))
        if cancel_button:
            cancel_button.setText(tr("button.cancel"))

    def initialize(self):
        self.settings = load_settings()
        self.apply_localization()
        
        i = 0
        self.format_fields = {}
        for f in self.settings['file_types']:
            self.ui.fileTypesTable.insertRow(i)
            item = QTableWidgetItem(f)
            if f in ('Audio', 'Video', 'Image'):
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.ui.fileTypesTable.setItem(i, 0, item)
            self.ui.fileTypesTable.setItem(
                i, 1, QTableWidgetItem(self.settings['file_types'][f]))

            # TBD: This increment is inside the loop, which is correct, but the comment was misleading.
            i += 1

        self.ui.addFileTypeButton.clicked.connect(self.add_new_file_type)
        
        self.ui.fileTypesTable.cellChanged.connect(
            self.cell_changed, Qt.QueuedConnection)

        # Collect styles with exact keys returned by Qt
        style_keys = list(QStyleFactory.keys())  # exact casing from Qt
        # Keep current style (from settings) at top if present, else keep default order
        self.ui.styleComboBox.clear()
        if self.settings.get('style') in style_keys:
            # Put saved style at index 0 for convenience
            styles_ordered = [self.settings['style']] + [s for s in style_keys if s != self.settings['style']]
        else:
            styles_ordered = style_keys
        self.ui.styleComboBox.addItems(styles_ordered)

        # Preselect saved style exactly, if present
        if self.settings.get('style') in style_keys:
            idx = self.ui.styleComboBox.findText(self.settings['style'])
            if idx >= 0:
                self.ui.styleComboBox.setCurrentIndex(idx)

        # Apply the theme lock logic once after style selection
        self._update_theme_lock(self.ui.styleComboBox.currentText())

        # Initialize theme combo from saved settings
        saved_theme = self.settings.get("theme", "System")
        setup_combo(self.ui.themeComboBox, THEMES, "theme", saved_theme)
        setup_language_combo(self.languageComboBox, self.settings.get("language", "en"))
        if self.ui.styleComboBox.currentText().lower() == "windowsvista":
            # UI lock: force Light for windowsvista
            set_combo_value(self.ui.themeComboBox, "Light")
            self.ui.themeComboBox.setEnabled(False)
        else:
            set_combo_value(self.ui.themeComboBox, saved_theme)
            self.ui.themeComboBox.setEnabled(True)

        # Keep reacting when user changes style
        self.ui.styleComboBox.textActivated.connect(self._update_theme_lock)

        rbs = [c for c in self.ui.dateDefGroupBox.children() if 'QRadioButton' in str(
            type(c))]  # TBD vN this is not very safe
        rbs[self.settings['date_type']].setChecked(True)
        self.ui.ruleExecIntervalEdit.setText(
            str(self.settings['rule_exec_interval']/60))
        
        # Startup checkbox handling:
        # - Windows: hide it (managed by installer/OS).
        # - macOS: show and bind actual state.
        if sys.platform.startswith("win"):
            self.ui.startAtLoginCheckBox.setVisible(False)
        else:
            try:
                self.ui.startAtLoginCheckBox.setChecked(startup_is_enabled())
            except Exception:
                self.ui.startAtLoginCheckBox.setChecked(False)
        

    def _update_theme_lock(self, style_name: str):
        is_vista = style_name.lower() == "windowsvista"
        self.ui.themeComboBox.setEnabled(not is_vista)
        if is_vista:
            # Force Light in UI for windowsvista
            set_combo_value(self.ui.themeComboBox, "Light")

    def cell_changed(self, row, col):
        if col == 0:
            settings = load_settings()
            new_value = self.ui.fileTypesTable.item(row, 0).text()
            other_values = [self.ui.fileTypesTable.item(i, 0).text() for i in range(
                self.ui.fileTypesTable.rowCount()) if self.ui.fileTypesTable.item(i, 0) and i != row]
            if new_value in other_values:  # settings['file_types'].keys():
                QMessageBox.critical(
                    self, tr("dialog.error"), tr("dialog.duplicate_file_type"))
                self.ui.fileTypesTable.editItem(
                    self.ui.fileTypesTable.item(row, 0))
                return False
            if row < len(settings['file_types']):  # it's not a new format
                # TBD this is unsafe and will cause bugs on non-Win systems
                prev_value = list(settings['file_types'].keys())[row]
                if new_value != prev_value and new_value:
                    
                    settings['file_types'][new_value] = settings['file_types'][prev_value]
                    del settings['file_types'][prev_value]
                    for i in range(len(settings['rules'])):
                        for k in range(len(settings['rules'][i]['conditions'])):
                            c = settings['rules'][i]['conditions'][k]
                            if c['type'] == 'type' and c['file_type'] == prev_value:
                                settings['rules'][i]['conditions'][k]['file_type'] = new_value
                    save_settings(settings)
                    self.settings = settings

                if new_value == "":
                    count = 0
                    for i in range(len(settings['rules'])):
                        for k in range(0, len(settings['rules'][i]['conditions'])):
                            c = settings['rules'][i]['conditions'][k]
                            if c['type'] == 'type' and c['file_type'] == prev_value:
                                count += 1
                    used_in_rules = tr("dialog.remove_file_type_used", count=count) if count > 0 else ""
                    # TBD remove orphaned conditions
                    reply = QMessageBox.question(self, tr("dialog.warning"),
                                                 tr("dialog.remove_file_type", used=used_in_rules),
                                                 QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        del settings['file_types'][prev_value]
                        save_settings(settings)
                        self.settings = settings
                        self.ui.fileTypesTable.removeRow(row)
                    else:
                        self.ui.fileTypesTable.item(row, 0).setText(prev_value)

    

    def add_new_file_type(self):
        """Adds a new empty row to the file types table for a new file type entry."""
        self.ui.fileTypesTable.insertRow(self.ui.fileTypesTable.rowCount())
        

    def accept(self):
        format_names = [self.ui.fileTypesTable.item(i, 0).text() for i in range(
            self.ui.fileTypesTable.rowCount()) if self.ui.fileTypesTable.item(i, 0)]
        if len(format_names) != len(set(format_names)):
            QMessageBox.critical(
                self, tr("dialog.error"), tr("dialog.duplicate_file_types"))
            return False

        rbs = [c for c in self.ui.dateDefGroupBox.children()
               if 'QRadioButton' in str(type(c))]
        for c in rbs:
            if c.isChecked():
                self.settings['date_type'] = rbs.index(c)
        self.settings['rule_exec_interval'] = float(
            self.ui.ruleExecIntervalEdit.text())*60
        self.settings['style'] = self.ui.styleComboBox.currentText()
        if self.settings['style'].lower() == "windowsvista":
            self.settings['theme'] = "Light"
        else:
            self.settings['theme'] = combo_value(self.ui.themeComboBox)
        self.settings['language'] = combo_value(self.languageComboBox)

        self.settings['file_types'] = {}
        # TBD add validation
        for i in range(self.ui.fileTypesTable.rowCount()):
            if self.ui.fileTypesTable.item(i, 0) and self.ui.fileTypesTable.item(i, 0).text():
                self.settings['file_types'][self.ui.fileTypesTable.item(
                    i, 0).text()] = self.ui.fileTypesTable.item(i, 1).text()

        if not sys.platform.startswith("win"):
            try:
                want = self.ui.startAtLoginCheckBox.isChecked()
                if want:
                    startup_enable()
                else:
                    startup_disable()
            except Exception:
                pass

        save_settings(self.settings)
        super(SettingsDialog, self).accept()

    def change_style(self, style_name):
        QApplication.setStyle(QStyleFactory.create(style_name))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsDialog()
    

    sys.exit(app.exec())
