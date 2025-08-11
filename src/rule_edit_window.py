import sys
from os.path import normpath

from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QAbstractItemView,
    QMessageBox,
    QListWidgetItem,
)
from PySide6.QtCore import QItemSelectionModel

from src.ui.ui_list_dialog import Ui_listDialog
from src.ui.ui_rule_edit_window import Ui_RuleEditWindow
from src.condition_dialog import ConditionDialog
from src.tags_dialog import generate_tag_model

from declutter.rules import get_files_affected_by_rule
from declutter.tags import get_tags_and_groups
from declutter.config import ALL_TAGGED_TEXT


class RuleEditWindow(QDialog):
    def __init__(self):
        super(RuleEditWindow, self).__init__()

        self.ui = Ui_RuleEditWindow()
        self.ui.setupUi(self)

        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

        self.rule = {}
        self.updated = False  # kept for compatibility if used elsewhere

        # Sources
        self.ui.folderAddButton.clicked.connect(self.add_folder)
        self.ui.sourceRemoveButton.clicked.connect(self.delete_source)

        # Actions and testing
        self.ui.actionComboBox.currentIndexChanged.connect(self.action_change)
        self.ui.testButton.clicked.connect(self.test_rule)
        self.ui.folderBrowseButton.clicked.connect(self.select_folder)

        # Conditions
        self.ui.conditionAddButton.clicked.connect(self.add_condition)
        self.ui.conditionRemoveButton.clicked.connect(self.delete_condition)
        self.ui.conditionListWidget.itemDoubleClicked.connect(self.edit_condition)

        # Tags view (for Tag/Remove tags actions and for displaying selected tags in UI)
        self.ui.tagsView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.ui.allTaggedAddButton.clicked.connect(self.add_all_tagged)

        self.tag_model = QStandardItemModel()
        generate_tag_model(self.tag_model, get_tags_and_groups(), False)
        self.ui.tagsView.setModel(self.tag_model)
        self.ui.tagsView.expandAll()
        self.ui.tagsView.clicked.connect(self.tags_selection_changed)

        # Advanced
        self.ui.advancedButton.clicked.connect(self.show_advanced)

        # Initial visibility tweaks
        self.ui.ignoreNewestCheckBox.setVisible(False)
        self.ui.numberNewestEdit.setVisible(False)
        self.ui.newestLabel.setVisible(False)
        self.ui.line.setVisible(False)
        self.ui.conditionLoadButton.setVisible(False)
        self.ui.conditionSaveButton.setVisible(False)

        self.ui.ruleNameEdit.setFocus()
        self.action_change()

    def tags_selection_changed(self):
        selected_tags = [
            self.ui.tagsView.model().itemFromIndex(index).text()
            for index in self.ui.tagsView.selectedIndexes()
        ]
        self.ui.selectedTagsLabel.setText('Selected tags: ' + ', '.join(selected_tags))

    def show_advanced(self):
        self.ui.line.setVisible(True)
        self.ui.advancedButton.setVisible(False)
        self.ui.ignoreNewestCheckBox.setVisible(True)
        self.ui.numberNewestEdit.setVisible(True)
        self.ui.newestLabel.setVisible(True)

    def add_condition(self):
        dlg = ConditionDialog(self)
        # New condition starts blank; user fills dialog
        if dlg.exec() == QDialog.Accepted and dlg.condition:
            if 'conditions' not in self.rule:
                self.rule['conditions'] = []
            self.rule['conditions'].append(dlg.condition)
            self.refresh_conditions()

    def delete_condition(self):
        # Delete selected condition from list and rule
        if 'conditions' not in self.rule or not self.rule['conditions']:
            return
        indexes = self.ui.conditionListWidget.selectedIndexes()
        if not indexes:
            return
        row = indexes[0].row()
        if row < 0 or row >= len(self.rule['conditions']):
            return
        del self.rule['conditions'][row]
        self.refresh_conditions()

    def edit_condition(self, item: QListWidgetItem):
        # Double-click handler to edit a condition
        if 'conditions' not in self.rule or not self.rule['conditions']:
            return
        row = self.ui.conditionListWidget.row(item)
        if row < 0 or row >= len(self.rule['conditions']):
            return

        existing = self.rule['conditions'][row]
        dlg = ConditionDialog(self)
        # Preload existing condition into dialog
        if hasattr(dlg, 'load_condition'):
            dlg.load_condition(existing)
        else:
            dlg.condition = dict(existing)

        if dlg.exec() == QDialog.Accepted and dlg.condition:
            self.rule['conditions'][row] = dlg.condition
            self.refresh_conditions()

    def refresh_conditions(self):
        # Rebuilds the textual list of conditions in the widget
        conds = []
        for c in self.rule.get('conditions', []):
            ctype = c.get('type')

            if ctype == 'tags' and c.get('tag_switch') != 'tags in group':
                tag_switch = c.get('tag_switch', '')
                if tag_switch in ('no tags', 'any tags'):
                    desc = 'Has ' + tag_switch
                else:
                    desc = 'Has ' + tag_switch + ' of these tags: ' + ', '.join(c.get('tags', []))
                conds.append(desc)

            elif ctype == 'tags' and c.get('tag_switch') == 'tags in group':
                conds.append('Has tags in group: ' + c.get('tag_group', ''))

            elif ctype == 'date':
                conds.append('Age is ' + c.get('age_switch', '') + ' ' + str(c.get('age', '')) + ' ' + c.get('age_units', ''))

            elif ctype == 'name':
                name_switch = c.get('name_switch', 'matches')
                conds.append('Name ' + name_switch + ' ' + str(c.get('filemask', '')))

            elif ctype == 'size':
                conds.append('File size is ' + c.get('size_switch', '') + ' ' + str(c.get('size', '')) + c.get('size_units', ''))

            elif ctype == 'type':
                conds.append('File type ' + c.get('file_type_switch', '') + ' ' + c.get('file_type', ''))

            else:
                # Fallback textualization
                conds.append(str(c))

        self.ui.conditionListWidget.clear()
        self.ui.conditionListWidget.addItems(conds)

    def select_folder(self):
        """Opens a folder selection dialog and sets the selected path to the appropriate text field."""
        # Decide which field to populate
        if self.ui.actionComboBox.currentText() == "Move to subfolder":
            folderField = self.ui.subfolderEdit
        else:
            folderField = self.ui.targetFolderEdit

        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self, "Select folder", folderField.text(), options)
        if directory:
            folderField.setText(directory)

    def update_rule_from_ui(self):
        # Ensure keys exist
        if 'conditions' not in self.rule:
            self.rule['conditions'] = []
        if 'folders' not in self.rule:
            self.rule['folders'] = []
        if 'tags' not in self.rule:
            self.rule['tags'] = []

        self.rule['name'] = self.ui.ruleNameEdit.text()
        self.rule['enabled'] = self.ui.enabledCheckBox.isChecked()
        self.rule['recursive'] = self.ui.recursiveCheckBox.isChecked()
        self.rule['condition_switch'] = self.ui.conditionSwitchComboBox.currentText()
        self.rule['action'] = self.ui.actionComboBox.currentText()
        self.rule['keep_tags'] = self.ui.keepTagsCheckBox.isChecked()
        self.rule['keep_folder_structure'] = self.ui.keepFolderStructureCheckBox.isChecked()
        self.rule['target_folder'] = self.ui.targetFolderEdit.text()
        self.rule['target_subfolder'] = self.ui.subfolderEdit.text()
        self.rule['name_pattern'] = self.ui.renameEdit.text()
        self.rule['overwrite_switch'] = self.ui.overwriteComboBox.currentText()
        self.rule['tags'] = [index.data() for index in self.ui.tagsView.selectedIndexes()]
        self.rule['ignore_newest'] = self.ui.ignoreNewestCheckBox.isChecked()
        self.rule['ignore_N'] = self.ui.numberNewestEdit.text()

    def accept(self):
        self.update_rule_from_ui()

        error = ""
        # Validation chain
        if self.rule['ignore_newest'] and self.rule['ignore_N'] == "":
            error = "Please specify the number of files to ignore"
        if self.rule['action'] == "Rename" and self.rule['name_pattern'] == "":
            error = "Please specify the name pattern"
        if self.rule['action'] == "Move to subfolder" and self.rule['target_subfolder'] == "":
            error = "Please specify the target subfolder"
        if self.rule['action'] in ("Move", "Copy") and self.rule['target_folder'] == "":
            error = "Please specify the target folder"
        if not self.rule.get('conditions'):
            error = "Please add at least one condition"
        if not self.rule.get('folders'):
            error = "Please select at least one source"
        if self.rule['name'] == "":
            error = "Please enter the name"

        if error:
            QMessageBox.critical(self, "Error", error, QMessageBox.Ok)
            return

        if 'id' not in self.rule and not self.rule['enabled']:
            reply = QMessageBox.question(
                self,
                "Enable rule?",
                "The rule is not enabled, would you like to enable it before saving?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.rule['enabled'] = True

        super(RuleEditWindow, self).accept()

    def test_rule(self):
        self.update_rule_from_ui()

        msgBox = QDialog(self)
        msgBox.ui = Ui_listDialog()
        msgBox.ui.setupUi(msgBox)

        affected = get_files_affected_by_rule(self.rule)
        if affected:
            msgBox.ui.label.setText(str(len(affected)) + " file(s) affected by this rule:")
            msgBox.ui.listWidget.addItems(affected)
        else:
            msgBox.ui.listWidget.setVisible(False)
            msgBox.ui.label.setText("No files affected by this rule.")

        msgBox.exec()

    def load_rule(self, rule: dict):
        # Set rule reference (rule may be modified in place by caller)
        self.rule = rule or {}

        # Defaults to avoid KeyErrors
        self.rule.setdefault('folders', [])
        self.rule.setdefault('conditions', [])
        self.rule.setdefault('tags', [])
        self.rule.setdefault('keep_folder_structure', False)
        self.rule.setdefault('target_subfolder', '')
        self.rule.setdefault('name_pattern', '')
        self.rule.setdefault('overwrite_switch', self.ui.overwriteComboBox.currentText())
        self.rule.setdefault('ignore_newest', False)
        self.rule.setdefault('ignore_N', '')

        # Populate UI from rule
        self.ui.ruleNameEdit.setText(self.rule.get('name', ''))
        self.ui.sourceListWidget.clear()
        self.ui.sourceListWidget.addItems(self.rule.get('folders', []))
        self.ui.enabledCheckBox.setChecked(bool(self.rule.get('enabled', False)))
        self.ui.recursiveCheckBox.setChecked(bool(self.rule.get('recursive', False)))
        self.ui.conditionSwitchComboBox.setCurrentText(self.rule.get('condition_switch', 'all'))

        self.refresh_conditions()

        # Action-dependent fields
        self.ui.actionComboBox.setCurrentIndex(self.ui.actionComboBox.findText(self.rule.get('action', 'Move')))
        self.ui.targetFolderEdit.setText(self.rule.get('target_folder', ''))
        self.ui.keepTagsCheckBox.setChecked(bool(self.rule.get('keep_tags', False)))
        self.ui.keepFolderStructureCheckBox.setChecked(bool(self.rule.get('keep_folder_structure', False)))
        self.ui.subfolderEdit.setText(self.rule.get('target_subfolder', ''))
        self.ui.renameEdit.setText(self.rule.get('name_pattern', ''))

        if 'overwrite_switch' in self.rule:
            self.ui.overwriteComboBox.setCurrentIndex(
                self.ui.overwriteComboBox.findText(self.rule['overwrite_switch'])
            )

        # Restore tag selections in the tree
        sel_model = self.ui.tagsView.selectionModel()
        sel_model.clearSelection()
        model = self.ui.tagsView.model()
        target_tags = set(self.rule.get('tags', []))
        for i in range(model.rowCount()):
            parent_item = model.item(i)
            for k in range(parent_item.rowCount()):
                child = parent_item.child(k)
                if child.text() in target_tags:
                    sel_model.select(model.indexFromItem(child), QItemSelectionModel.Select)
        self.ui.selectedTagsLabel.setText('Selected tags: ' + ','.join(self.rule.get('tags', [])))

        # Apply action visibility
        self.action_change()

        # Advanced (ignore newest)
        self.ui.ignoreNewestCheckBox.setChecked(bool(self.rule.get('ignore_newest', False)))
        self.ui.numberNewestEdit.setText(self.rule.get('ignore_N', ''))

        if self.rule.get('ignore_newest'):
            self.ui.line.setVisible(True)
            self.ui.ignoreNewestCheckBox.setVisible(True)
            self.ui.numberNewestEdit.setVisible(True)
            self.ui.newestLabel.setVisible(True)

    def action_change(self):
        state = self.ui.actionComboBox.currentText()

        self.ui.toFolderLabel.setVisible(state in ("Move", "Copy"))
        self.ui.targetFolderEdit.setVisible(state in ("Move", "Copy"))
        self.ui.folderBrowseButton.setVisible(state in ("Move", "Copy", "Move to subfolder"))

        self.ui.keepTagsCheckBox.setVisible(state in ("Move", "Copy", "Move to subfolder"))
        self.ui.keepFolderStructureCheckBox.setVisible(state in ("Move", "Copy"))

        self.ui.fileWithSameNameLabel.setVisible(state in ("Move", "Copy", "Rename", "Move to subfolder"))
        self.ui.overwriteComboBox.setVisible(state in ("Move", "Copy", "Rename", "Move to subfolder"))

        self.ui.renameEdit.setVisible(state == "Rename")
        self.ui.subfolderEdit.setVisible(state == "Move to subfolder")

        self.ui.tagsView.setVisible(state in ("Tag", "Remove tags"))
        self.ui.selectedTagsLabel.setVisible(state in ("Tag", "Remove tags"))

    def add_folder(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self, "Select folder", '', options)
        if directory:
            folders = self.rule.setdefault('folders', [])
            normalized = normpath(directory)
            if normalized not in folders:
                folders.append(normalized)
                self.ui.sourceListWidget.addItem(normalized)

    def add_all_tagged(self):
        folders = self.rule.setdefault('folders', [])
        if ALL_TAGGED_TEXT not in folders:
            folders.append(ALL_TAGGED_TEXT)
            self.ui.sourceListWidget.addItem(ALL_TAGGED_TEXT)

    def delete_source(self):
        indexes = self.ui.sourceListWidget.selectedIndexes()
        if not indexes:
            return
        row = indexes[0].row()
        if row < 0 or row >= len(self.rule.get('folders', [])):
            return
        del self.rule['folders'][row]
        self.ui.sourceListWidget.takeItem(row)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RuleEditWindow()
    window.show()
    sys.exit(app.exec())
