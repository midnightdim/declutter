import sys
from os.path import normpath
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QApplication,  QDialog,  QFileDialog, QAbstractItemView, QMessageBox
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
        self.updated = False # TBD: Check if this flag is still necessary or used consistently
        

        self.ui.folderAddButton.clicked.connect(self.add_folder)
        self.ui.sourceRemoveButton.clicked.connect(self.delete_source)
        self.ui.actionComboBox.currentIndexChanged.connect(self.action_change)
        self.ui.testButton.clicked.connect(self.test_rule)
        self.ui.folderBrowseButton.clicked.connect(self.select_folder)
        self.ui.conditionAddButton.clicked.connect(self.add_condition)
        self.ui.conditionRemoveButton.clicked.connect(self.delete_condition)
        self.ui.conditionListWidget.itemDoubleClicked.connect(
            self.edit_condition)

        self.ui.tagsView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.ui.allTaggedAddButton.clicked.connect(self.add_all_tagged)

        self.tag_model = QStandardItemModel()
        generate_tag_model(self.tag_model, get_tags_and_groups(), False)
        self.ui.tagsView.setModel(self.tag_model)
        self.ui.tagsView.expandAll()
        self.ui.tagsView.clicked.connect(self.tags_selection_changed)

        self.ui.advancedButton.clicked.connect(self.show_advanced)

        # TBD: These visibility settings might be redundant or could be handled more dynamically
        self.ui.ignoreNewestCheckBox.setVisible(False)
        self.ui.numberNewestEdit.setVisible(False)
        self.ui.newestLabel.setVisible(False)
        self.ui.line.setVisible(False)

        self.ui.conditionLoadButton.setVisible(False)
        self.ui.conditionSaveButton.setVisible(False)

        self.ui.ruleNameEdit.setFocus()

        self.action_change()

    def tags_selection_changed(self):
        selected_tags = [self.ui.tagsView.model().itemFromIndex(
            index).text() for index in self.ui.tagsView.selectedIndexes()]
        self.ui.selectedTagsLabel.setText(
            'Selected tags: '+', '.join(selected_tags))

    def show_advanced(self):
        self.ui.line.setVisible(True)
        self.ui.advancedButton.setVisible(False)
        self.ui.ignoreNewestCheckBox.setVisible(True)
        self.ui.numberNewestEdit.setVisible(True)
        self.ui.newestLabel.setVisible(True)

    def add_condition(self):
        self.condition_window = ConditionDialog()
        self.condition_window.exec()
        if not 'conditions' in self.rule.keys():
            self.rule['conditions'] = []
        if self.condition_window.condition:
            self.rule['conditions'].append(self.condition_window.condition)
            self.refresh_conditions()
        

    def delete_condition(self, cond):
        del self.rule['conditions'][self.ui.conditionListWidget.selectedIndexes()[
            0].row()]
        self.refresh_conditions()

    def edit_condition(self, cond):
        c = self.rule['conditions'][self.ui.conditionListWidget.indexFromItem(
            cond).row()]
        # TBD: Implement actual editing of the condition in the dialog
        self.refresh_conditions()

    

    def refresh_conditions(self):
        conds = []

        for c in self.rule['conditions']:
            if c['type'] == 'tags' and c['tag_switch'] != 'tags in group':
                conds.append('Has ' + c['tag_switch'] + (' of these tags: ' + ', '.join(
                    c['tags']) if c['tag_switch'] not in ('no tags', 'any tags') else ''))
            elif c['type'] == 'tags' and c['tag_switch'] == 'tags in group':
                conds.append('Has tags in group: '+c['tag_group'])
            elif c['type'] == 'date':
                conds.append(
                    'Age is ' + c['age_switch'] + ' ' + str(c['age']) + ' ' + c['age_units'])
            elif c['type'] == 'name':
                if not 'name_switch' in c.keys():
                    c['name_switch'] = 'matches'
                conds.append(
                    'Name ' + c['name_switch'] + ' ' + str(c['filemask']))
            elif c['type'] == 'size':
                conds.append(
                    'File size is ' + c['size_switch'] + ' ' + str(c['size']) + c['size_units'])
            elif c['type'] == 'type':
                conds.append('File type ' +
                             c['file_type_switch'] + ' ' + c['file_type'])

        self.ui.conditionListWidget.clear()
        self.ui.conditionListWidget.addItems(conds)

    def select_folder(self):
        """Opens a folder selection dialog and sets the selected path to the appropriate text field."""
        folderField = self.ui.subfolderEdit if self.ui.actionComboBox.currentText(
        ) == "Move to subfolder" else self.ui.targetFolderEdit  # TBD this is a bit dangerous in case of errors
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                                                     "QFileDialog.getExistingDirectory()",
                                                     folderField.text(), options)
        if directory:
            folderField.setText(directory)

    def update_rule_from_ui(self):
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
        
        self.rule['tags'] = [index.data()
                             for index in self.ui.tagsView.selectedIndexes()]
        
        self.rule['ignore_newest'] = self.ui.ignoreNewestCheckBox.isChecked()
        self.rule['ignore_N'] = self.ui.numberNewestEdit.text()

    def accept(self):
        self.update_rule_from_ui()
        error = ""
        error = "Please specify the number of files to ignore" if (
            self.rule['ignore_newest'] and self.rule['ignore_N'] == "") else error  # TBD check if ignore_N is int
        error = "Please specify the name pattern" if (
            self.rule['action'] == "Rename" and self.rule['name_pattern'] == "") else error
        error = "Please specify the target subfolder" if (
            self.rule['action'] == "Move to subfolder" and self.rule['target_subfolder'] == "") else error
        error = "Please specify the target folder" if (self.rule['action'] in (
            "Move", "Copy") and self.rule['target_folder'] == "") else error
        error = "Please add at least one condition" if 'conditions' not in self.rule.keys(
        ) or not self.rule['conditions'] else error
        error = "Please select at least one source" if (
            'folders' not in self.rule.keys()) or (not self.rule['folders']) else error
        error = "Please enter the name" if self.rule['name'] == "" else error
        if error:
            QMessageBox.critical(self, "Error", error, QMessageBox.Ok)
        else:
            if 'id' not in self.rule.keys() and not self.rule['enabled']:
                reply = QMessageBox.question(self, "Enable rule?",
                                             "The rule is not enabled, would you like to enable it before saving?",
                                             QMessageBox.Yes | QMessageBox.No)
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
            msgBox.ui.label.setText(
                str(len(affected)) + " file(s) affected by this rule:")
            msgBox.ui.listWidget.addItems(affected)
        else:
            msgBox.ui.listWidget.setVisible(False)
            msgBox.ui.label.setText("No files affected by this rule.")
        msgBox.exec()

    def load_rule(self, rule):
        self.rule = rule
        # TBD: Check if this assignment is always necessary or if rule is modified in place
        
        self.ui.ruleNameEdit.setText(rule['name'])
        self.ui.sourceListWidget.addItems(rule['folders'])
        self.ui.enabledCheckBox.setChecked(rule['enabled'])
        self.ui.recursiveCheckBox.setChecked(rule['recursive'])
        
        self.ui.conditionSwitchComboBox.setCurrentText(
            rule['condition_switch'])

        self.refresh_conditions()

        # TBD: Check if this index finding is efficient for large lists
        self.ui.actionComboBox.setCurrentIndex(
            self.ui.actionComboBox.findText(rule['action']))
        self.ui.targetFolderEdit.setText(rule['target_folder'])
        self.ui.keepTagsCheckBox.setChecked(rule['keep_tags'])
        self.ui.keepFolderStructureCheckBox.setChecked(
            rule['keep_folder_structure'] if 'keep_folder_structure' in rule.keys() else False)
        self.ui.subfolderEdit.setText(
            rule['target_subfolder'] if 'target_subfolder' in rule.keys() else '')
        self.ui.renameEdit.setText(
            rule['name_pattern'] if 'name_pattern' in rule.keys() else '')
        if 'overwrite_switch' in rule.keys():
            self.ui.overwriteComboBox.setCurrentIndex(
                self.ui.overwriteComboBox.findText(rule['overwrite_switch']))

        for i in range(self.ui.tagsView.model().rowCount()):
            for k in range(self.ui.tagsView.model().item(i).rowCount()):
                if self.ui.tagsView.model().item(i).child(k).text() in rule['tags']:
                    # TBD: This print statement is for debugging and should be removed or replaced with proper logging
                    # print(self.ui.tagsView.model().item(i).child(k).text())
                    self.ui.tagsView.selectionModel().select(self.ui.tagsView.model().indexFromItem(
                        self.ui.tagsView.model().item(i).child(k)), QItemSelectionModel.Select)

        self.ui.selectedTagsLabel.setText(
            'Selected tags: '+','.join(rule['tags']))

        # TBD: Check if this action_change call is always necessary here
        self.action_change()

        self.ui.ignoreNewestCheckBox.setChecked(rule['ignore_newest'])
        self.ui.numberNewestEdit.setText(rule['ignore_N'])

        if self.rule['ignore_newest']:
            self.ui.line.setVisible(True)
            self.ui.ignoreNewestCheckBox.setVisible(True)
            self.ui.numberNewestEdit.setVisible(True)
            self.ui.newestLabel.setVisible(True)

    def action_change(self):
        state = self.ui.actionComboBox.currentText()
        self.ui.toFolderLabel.setVisible(state in ("Move", "Copy"))
        self.ui.targetFolderEdit.setVisible(state in ("Move", "Copy"))
        self.ui.folderBrowseButton.setVisible(
            state in ("Move", "Copy", "Move to subfolder"))
        self.ui.keepTagsCheckBox.setVisible(
            state in ("Move", "Copy", "Move to subfolder"))
        self.ui.keepFolderStructureCheckBox.setVisible(
            state in ("Move", "Copy"))
        self.ui.fileWithSameNameLabel.setVisible(
            state in ("Move", "Copy", "Rename", "Move to subfolder"))
        self.ui.overwriteComboBox.setVisible(
            state in ("Move", "Copy", "Rename", "Move to subfolder"))
        self.ui.renameEdit.setVisible(state == "Rename")
        self.ui.subfolderEdit.setVisible(state == "Move to subfolder")
        self.ui.tagsView.setVisible(state in ("Tag", "Remove tags"))
        self.ui.selectedTagsLabel.setVisible(state in ("Tag", "Remove tags"))

    def add_folder(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                                                     "QFileDialog.getExistingDirectory()",
                                                     '', options)
        if directory:
            if not 'folders' in self.rule.keys():
                self.rule['folders'] = []
            if normpath(directory) not in self.rule['folders']:
                self.rule['folders'].append(normpath(directory))
                self.ui.sourceListWidget.addItem(normpath(directory))


    def add_all_tagged(self):
        if not 'folders' in self.rule.keys():
            self.rule['folders'] = []
        if ALL_TAGGED_TEXT not in self.rule['folders']:
            self.rule['folders'].append(ALL_TAGGED_TEXT)
            self.ui.sourceListWidget.addItem(ALL_TAGGED_TEXT)


    def delete_source(self):
        del self.rule['folders'][self.ui.sourceListWidget.selectedIndexes()[
            0].row()]
        self.ui.sourceListWidget.takeItem(
            self.ui.sourceListWidget.currentRow())



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RuleEditWindow()
    window.show()

    sys.exit(app.exec())
