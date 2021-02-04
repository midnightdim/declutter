import sys
from PySide6.QtUiTools import loadUiType
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QListWidget, QDialog, QDialogButtonBox, QFileDialog, QAbstractItemView, QMessageBox, QSizePolicy, QHBoxLayout
from PySide6.QtCore import (Qt, QAbstractItemModel)
from ui_rule_edit_window import Ui_RuleEditWindow
from declutter_lib import get_all_tags, get_files_affected_by_rule
from condition_dialog import ConditionDialog
from ui_list_dialog import Ui_listDialog
from os.path import normpath
#from PySide6.QtGui import 

class RuleEditWindow(QDialog):
    def __init__(self):
        super(RuleEditWindow, self).__init__()
        self.ui = Ui_RuleEditWindow()
        self.ui.setupUi(self)

        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

        self.rule = {}
        self.updated = False
        # self.rule = get_rule_by_name("Move envato")
        # self.loadRule(self.rule)

        self.ui.folderAddButton.clicked.connect(self.add_folder)
        self.ui.sourceRemoveButton.clicked.connect(self.delete_source)
        self.ui.actionComboBox.currentIndexChanged.connect(self.action_change)
        self.ui.testButton.clicked.connect(self.test_rule)
        self.ui.folderBrowseButton.clicked.connect(self.select_folder)
        self.ui.conditionAddButton.clicked.connect(self.add_condition)
        self.ui.conditionRemoveButton.clicked.connect(self.delete_condition)
        self.ui.conditionListWidget.itemDoubleClicked.connect(self.edit_condition)
        self.ui.tagsList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.ui.tagsList.addItems(get_all_tags())
        # self.ui.buttonBox.clicked.connect(self.process)
 
        self.action_change()

    def add_condition(self):
        self.condition_window = ConditionDialog()
        self.condition_window.exec_()
        if not 'conditions' in self.rule.keys():
            self.rule['conditions'] = []
        self.rule['conditions'].append(self.condition_window.condition)
        self.refresh_conditions()
        #print(self.rule['conditions'])
        #print(self.condition_window.condition)

    def delete_condition(self,cond):
        del self.rule['conditions'][self.ui.conditionListWidget.selectedIndexes()[0].row()]
        self.refresh_conditions()

    def edit_condition(self, cond):
        #print(self.ui.conditionListWidget.indexFromItem(cond).row())
        self.condition_window = ConditionDialog()
        self.condition_window.loadCondition(self.rule['conditions'][self.ui.conditionListWidget.indexFromItem(cond).row()])
        self.condition_window.exec_()
        #self.condition_window.show()
        # print(self.condition_window.condition)
        #print(self.rule)
        self.refresh_conditions()

    def refresh_sources(self):
        self.ui.sourceListWidget.clear()
        self.ui.sourceListWidget.addItems(self.rule['folders'])

    def refresh_conditions(self):
        conds = []
        for c in self.rule['conditions']:
            if c['type'] == 'tags':
                conds.append('Has ' + c['tag_switch'] + (' of these tags: ' + str(c['tags']) if c['tag_switch']!='no tags' else ''))
            elif c['type'] == 'date':
                conds.append('Age is ' + c['age_switch'] + ' ' + str(c['age']) + ' ' + c['age_units'])      
            elif c['type'] == 'name':
                if not 'name_switch' in c.keys():
                    c['name_switch'] = 'matches'
                conds.append('Name ' + c['name_switch'] + ' ' + str(c['filemask']))
            elif c['type'] == 'size':
                conds.append('File size is ' + c['size_switch'] + ' ' + str(c['size']) + c['size_units'] )

        self.ui.conditionListWidget.clear()
        self.ui.conditionListWidget.addItems(conds)        
    
    def select_folder(self):
        folderField = self.ui.subfolderEdit if self.ui.actionComboBox.currentText() == "Move to subfolder" else self.ui.targetFolderEdit # TBD this is a bit dangerous in case of errors
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
        self.rule['tags'] = [self.ui.tagsList.item(row).text() for row in range(0,self.ui.tagsList.count()) if self.ui.tagsList.item(row).isSelected()]

    def accept(self):
        #print("Saving")
        self.update_rule_from_ui()
        self.updated = True
        #self.rule_init = self.rule
        #self.setResult(QDialog.DialogCode.Accepted)  # doesn't work for some reason
        #self.setResult(1)
        #print(self.result())
        self.close()

    def test_rule(self):
        #msgBox = QMessageBox.information(self,"Some title","Files and folders affected by this rule:")
        #msgBox.setDetailedText("details go here")
        #reply = msgBox.exec_()

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
        msgBox.exec_()


    def load_rule(self, rule):
        self.rule = rule
        #self.rule = rule.copy()
        #self.rule_init = rule
        self.ui.ruleNameEdit.setText(rule['name'])
        self.ui.sourceListWidget.addItems(rule['folders'])
        self.ui.enabledCheckBox.setChecked(rule['enabled'])
        self.ui.recursiveCheckBox.setChecked(rule['recursive'])
        #print(self.rule['condition_switch'])
        self.ui.conditionSwitchComboBox.setCurrentText(rule['condition_switch'])

        self.refresh_conditions()

        # self.ui.conditionListWidget.addItems(conds)
        self.ui.actionComboBox.setCurrentIndex(self.ui.actionComboBox.findText(rule['action']))
        self.ui.targetFolderEdit.setText(rule['target_folder'])
        self.ui.keepTagsCheckBox.setChecked(rule['keep_tags'])
        self.ui.keepFolderStructureCheckBox.setChecked(rule['keep_folder_structure'])
        self.ui.subfolderEdit.setText(rule['target_subfolder'] if 'target_subfolder' in rule.keys() else '')
        self.ui.renameEdit.setText(rule['name_pattern'] if 'name_pattern' in rule.keys() else '') 
        if 'overwrite_switch' in rule.keys():
            self.ui.overwriteComboBox.setCurrentIndex(self.ui.overwriteComboBox.findText(rule['overwrite_switch']))

        for row in range(0,self.ui.tagsList.count()):
            if self.ui.tagsList.item(row).text() in rule['tags']:
                self.ui.tagsList.item(row).setSelected(True)
        self.action_change()

    def action_change(self):
        state = self.ui.actionComboBox.currentText()
        self.ui.toFolderLabel.setVisible(state in ("Move", "Copy"))
        self.ui.targetFolderEdit.setVisible(state in ("Move", "Copy"))
        self.ui.folderBrowseButton.setVisible(state in ("Move", "Copy","Move to subfolder"))
        self.ui.keepTagsCheckBox.setVisible(state in ("Move", "Copy"))
        self.ui.keepFolderStructureCheckBox.setVisible(state in ("Move", "Copy"))
        self.ui.fileWithSameNameLabel.setVisible(state in ("Move", "Copy", "Rename", "Move to subfolder"))
        self.ui.overwriteComboBox.setVisible(state in ("Move", "Copy", "Rename", "Move to subfolder"))
        self.ui.renameEdit.setVisible(state == "Rename")
        self.ui.subfolderEdit.setVisible(state == "Move to subfolder")
        self.ui.tagsList.setVisible(state == "Tag")

    def add_folder(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                "QFileDialog.getExistingDirectory()",
                '', options)
        if directory:
            if not 'folders' in self.rule.keys():
                self.rule['folders'] = []
            self.rule['folders'].append(normpath(directory))
            self.refresh_sources()

    def delete_source(self):
        del self.rule['folders'][self.ui.sourceListWidget.selectedIndexes()[0].row()]
        self.refresh_sources()    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RuleEditWindow()
    window.show()

    sys.exit(app.exec_())