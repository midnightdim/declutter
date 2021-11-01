import sys
#from PySide2.QtUiTools import loadUiType
from PySide2.QtGui import QStandardItemModel
from PySide2.QtWidgets import QApplication,  QDialog,  QFileDialog, QAbstractItemView, QMessageBox,  QMessageBox
from PySide2.QtCore import QItemSelectionModel
from ui_rule_edit_window import Ui_RuleEditWindow
# from declutter_lib import get_files_affected_by_rule, get_tags_and_groups, ALL_TAGGED_TEXT
from declutter_lib import LITE_MODE
if not LITE_MODE:
    from declutter_lib import get_files_affected_by_rule, get_tags_and_groups, ALL_TAGGED_TEXT
else:
    from declutter_lib_core import get_files_affected_by_rule
from condition_dialog import ConditionDialog
from ui_list_dialog import Ui_listDialog
from os.path import normpath
from tags_dialog import generate_tag_model
#from PySide6.QtGui import 

class RuleEditWindow(QDialog):
    # def __init__(self, lite_mode = False):
    def __init__(self):    
        super(RuleEditWindow, self).__init__()
        self.ui = Ui_RuleEditWindow()
        self.ui.setupUi(self)
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

        self.rule = {}
        # self.lite_mode = lite_mode
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

        if not LITE_MODE:
            self.ui.tagsView.setSelectionMode(QAbstractItemView.ExtendedSelection)
            self.ui.allTaggedAddButton.clicked.connect(self.add_all_tagged)
            
            self.tag_model = QStandardItemModel()
            generate_tag_model(self.tag_model,get_tags_and_groups(),False)       
            self.ui.tagsView.setModel(self.tag_model)
            self.ui.tagsView.expandAll()
            self.ui.tagsView.clicked.connect(self.tags_selection_changed)
        # for t in get_all_tags():
        #     self.ui.tagsList.addItem(t)
        #     color = tag_get_color(t)
        #     if color:
        #         self.ui.tagsList.item(self.ui.tagsList.count()-1).setBackground(QColor(color))

        self.ui.advancedButton.clicked.connect(self.show_advanced)
        # self.ui.buttonBox.clicked.connect(self.process)
    
        self.ui.ignoreNewestCheckBox.setVisible(False)
        self.ui.numberNewestEdit.setVisible(False)
        self.ui.newestLabel.setVisible(False)
        self.ui.line.setVisible(False)

        # self.ui.tagAddButton.setVisible(False)
        self.ui.conditionLoadButton.setVisible(False)
        self.ui.conditionSaveButton.setVisible(False)

        if LITE_MODE:
            self.ui.allTaggedAddButton.setVisible(False)
            self.ui.keepTagsCheckBox.setVisible(False)
            self.ui.actionComboBox.removeItem(5)
            self.ui.actionComboBox.removeItem(5)
            self.ui.actionComboBox.removeItem(5)
            self.ui.targetFolderEdit.setToolTip('<type> will be replaced with file type')

        self.ui.ruleNameEdit.setFocus()

        self.action_change()

    def tags_selection_changed(self):
        selected_tags = [self.ui.tagsView.model().itemFromIndex(index).text() for index in self.ui.tagsView.selectedIndexes()]
        self.ui.selectedTagsLabel.setText('Selected tags: '+', '.join(selected_tags))

    def show_advanced(self):
        self.ui.line.setVisible(True)
        self.ui.advancedButton.setVisible(False)
        self.ui.ignoreNewestCheckBox.setVisible(True)
        self.ui.numberNewestEdit.setVisible(True)
        self.ui.newestLabel.setVisible(True)

    def add_condition(self):
        self.condition_window = ConditionDialog()
        self.condition_window.exec_()
        if not 'conditions' in self.rule.keys():
            self.rule['conditions'] = []
        if self.condition_window.condition:
            self.rule['conditions'].append(self.condition_window.condition)
            self.refresh_conditions()
        #print(self.rule['conditions'])
        #print(self.condition_window.condition)

    def delete_condition(self,cond):
        del self.rule['conditions'][self.ui.conditionListWidget.selectedIndexes()[0].row()]
        self.refresh_conditions()

    def edit_condition(self, cond):
        c = self.rule['conditions'][self.ui.conditionListWidget.indexFromItem(cond).row()]
        if c['type'] == 'tags' and LITE_MODE:
            return
        #print(self.ui.conditionListWidget.indexFromItem(cond).row())
        self.condition_window = ConditionDialog()
        self.condition_window.load_condition(c)
        self.condition_window.exec_()
        #self.condition_window.show()
        # print(self.condition_window.condition)
        #print(self.rule)
        self.refresh_conditions()

    # def refresh_sources(self):
    #     self.ui.sourceListWidget.clear()
    #     self.ui.sourceListWidget.addItems(self.rule['folders'])

    def refresh_conditions(self):
        conds = []

        for c in self.rule['conditions']:
            if c['type'] == 'tags' and c['tag_switch'] != 'tags in group':
                conds.append('Has ' + c['tag_switch'] + (' of these tags: ' + ', '.join(c['tags']) if c['tag_switch'] not in ('no tags','any tags') else ''))
            elif c['type'] == 'tags' and c['tag_switch'] == 'tags in group':
                conds.append('Has tags in group: '+c['tag_group'] )
            elif c['type'] == 'date':
                conds.append('Age is ' + c['age_switch'] + ' ' + str(c['age']) + ' ' + c['age_units'])      
            elif c['type'] == 'name':
                if not 'name_switch' in c.keys():
                    c['name_switch'] = 'matches'
                conds.append('Name ' + c['name_switch'] + ' ' + str(c['filemask']))
            elif c['type'] == 'size':
                conds.append('File size is ' + c['size_switch'] + ' ' + str(c['size']) + c['size_units'] )
            elif c['type'] == 'type':
                conds.append('File type ' + c['file_type_switch'] + ' ' + c['file_type'])

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
        # print([index.data() for index in self.ui.tagsView.selectedIndexes()])
        self.rule['tags'] = [index.data() for index in self.ui.tagsView.selectedIndexes()]
        # self.rule['tags'] = [self.ui.tagsView.item(row).text() for row in range(0,self.ui.tagsView.count()) if self.ui.tagsView.item(row).isSelected()]
        self.rule['ignore_newest'] = self.ui.ignoreNewestCheckBox.isChecked()
        self.rule['ignore_N'] = self.ui.numberNewestEdit.text()

    def accept(self):
        self.update_rule_from_ui()
        error = ""
        error = "Please specify the number of files to ignore" if (self.rule['ignore_newest'] and self.rule['ignore_N']=="") else error #TBD check if ignore_N is int
        error = "Please specify the name pattern" if (self.rule['action'] == "Rename" and self.rule['name_pattern'] == "") else error
        error = "Please specify the target subfolder" if (self.rule['action'] == "Move to subfolder" and self.rule['target_subfolder'] == "") else error
        error = "Please specify the target folder" if (self.rule['action'] in ("Move","Copy") and self.rule['target_folder'] == "") else error
        error = "Please add at least one condition" if 'conditions' not in self.rule.keys() or not self.rule['conditions'] else error
        error = "Please select at least one source" if ('folders' not in self.rule.keys()) or (not self.rule['folders']) else error
        error = "Please enter the name" if self.rule['name'] == "" else error
        if error:
            QMessageBox.critical(self,"Error",error,QMessageBox.Ok)
        else:
            if 'id' not in self.rule.keys() and not self.rule['enabled']:
                reply = QMessageBox.question(self, "Enable rule?",
                "The rule is not enabled, would you like to enable it before saving?",
                QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.rule['enabled'] = True
            super(RuleEditWindow, self).accept()

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
        self.ui.keepFolderStructureCheckBox.setChecked(rule['keep_folder_structure'] if 'keep_folder_structure' in rule.keys() else False)
        self.ui.subfolderEdit.setText(rule['target_subfolder'] if 'target_subfolder' in rule.keys() else '')
        self.ui.renameEdit.setText(rule['name_pattern'] if 'name_pattern' in rule.keys() else '') 
        if 'overwrite_switch' in rule.keys():
            self.ui.overwriteComboBox.setCurrentIndex(self.ui.overwriteComboBox.findText(rule['overwrite_switch']))

        if not LITE_MODE:
            for i in range(self.ui.tagsView.model().rowCount()):
                for k in range(self.ui.tagsView.model().item(i).rowCount()):
                    if self.ui.tagsView.model().item(i).child(k).text() in rule['tags']:
                        # print(self.ui.tagsView.model().item(i).child(k).text())
                        self.ui.tagsView.selectionModel().select(self.ui.tagsView.model().indexFromItem(self.ui.tagsView.model().item(i).child(k)),QItemSelectionModel.Select)
            
            self.ui.selectedTagsLabel.setText('Selected tags: '+','.join(rule['tags']))

        # for index in self.ui.tagsView.setSelection()
        #     if self.ui.tagsView.item(row).text() in rule['tags']:
        #         self.ui.tagsView.item(row).setSelected(True)
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
        self.ui.folderBrowseButton.setVisible(state in ("Move", "Copy","Move to subfolder"))
        self.ui.keepTagsCheckBox.setVisible(state in ("Move", "Copy","Move to subfolder") and not LITE_MODE)
        self.ui.keepFolderStructureCheckBox.setVisible(state in ("Move", "Copy"))
        self.ui.fileWithSameNameLabel.setVisible(state in ("Move", "Copy", "Rename", "Move to subfolder"))
        self.ui.overwriteComboBox.setVisible(state in ("Move", "Copy", "Rename", "Move to subfolder"))
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
            # self.refresh_sources()

    def add_all_tagged(self):
        if not 'folders' in self.rule.keys():
            self.rule['folders'] = []
        if ALL_TAGGED_TEXT not in self.rule['folders']:
            self.rule['folders'].append(ALL_TAGGED_TEXT)
            self.ui.sourceListWidget.addItem(ALL_TAGGED_TEXT)
        # self.refresh_sources()

    def delete_source(self):
        del self.rule['folders'][self.ui.sourceListWidget.selectedIndexes()[0].row()]
        self.ui.sourceListWidget.takeItem(self.ui.sourceListWidget.currentRow())
        # self.refresh_sources()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RuleEditWindow()
    window.show()

    sys.exit(app.exec_())