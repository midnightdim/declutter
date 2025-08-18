import sys
from PySide6.QtWidgets import QDialog, QTableWidgetItem, QApplication, QStyleFactory, QMessageBox
from PySide6.QtCore import Qt
from declutter.store import load_settings, save_settings
from src.startup import is_enabled as startup_is_enabled, enable as startup_enable, disable as startup_disable

from src.ui.ui_settings_dialog import Ui_settingsDialog


class SettingsDialog(QDialog):
    def __init__(self):
        super(SettingsDialog, self).__init__()
        self.ui = Ui_settingsDialog()
        self.ui.setupUi(self)
        self.initialize()

    def initialize(self):
        self.settings = load_settings()
        
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
        if self.ui.styleComboBox.currentText().lower() == "windowsvista":
            # UI lock: force Light for windowsvista
            t_idx = self.ui.themeComboBox.findText("Light")
            if t_idx >= 0:
                self.ui.themeComboBox.setCurrentIndex(t_idx)
            self.ui.themeComboBox.setEnabled(False)
        else:
            t_idx = self.ui.themeComboBox.findText(saved_theme)
            if t_idx >= 0:
                self.ui.themeComboBox.setCurrentIndex(t_idx)
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
            idx = self.ui.themeComboBox.findText("Light")
            if idx >= 0:
                self.ui.themeComboBox.setCurrentIndex(idx)

    def cell_changed(self, row, col):
        if col == 0:
            settings = load_settings()
            new_value = self.ui.fileTypesTable.item(row, 0).text()
            other_values = [self.ui.fileTypesTable.item(i, 0).text() for i in range(
                self.ui.fileTypesTable.rowCount()) if self.ui.fileTypesTable.item(i, 0) and i != row]
            if new_value in other_values:  # settings['file_types'].keys():
                QMessageBox.critical(
                    self, "Error", "Duplicate format name, please change it")
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
                    used_in_rules = "\nIt's used in " + \
                        str(count)+" condition(s) (which won't be removed)." if count > 0 else ""
                    # TBD remove orphaned conditions
                    reply = QMessageBox.question(self, "Warning",
                                                 "This will delete the format. Are you sure?"+used_in_rules,
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
                self, "Error", "Duplicate format name(s) detected, please remove duplicates")
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
            self.settings['theme'] = self.ui.themeComboBox.currentText()

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
