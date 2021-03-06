import sys
# from PySide2.QtUiTools import loadUiType
from PySide2.QtGui import QStandardItemModel
from PySide2.QtWidgets import QApplication, QDialog, QAbstractItemView, QMessageBox
from PySide2.QtCore import QItemSelectionModel
from ui_condition_dialog import Ui_Condition
# from declutter_lib import load_settings, get_tags_and_groups, get_all_tag_groups
from declutter_lib import LITE_MODE, load_settings
if not LITE_MODE:
    from declutter_lib import get_tags_and_groups, get_all_tag_groups
from tags_dialog import generate_tag_model
#from PySide6.QtGui import 

class ConditionDialog(QDialog):
    def __init__(self):
        super(ConditionDialog, self).__init__()
        self.ui = Ui_Condition()
        self.ui.setupUi(self)
        self.condition = {}

        if not LITE_MODE:
            self.ui.tagsView.setSelectionMode(QAbstractItemView.ExtendedSelection)
            self.tag_model = QStandardItemModel()
            generate_tag_model(self.tag_model,get_tags_and_groups(),False)
            self.ui.tagsView.setModel(self.tag_model)
            self.ui.tagsView.expandAll()
            self.ui.tagsView.clicked.connect(self.tags_selection_changed)
        else:
            self.ui.conditionCombo.removeItem(3)
        #self.ui.tagsList.addItems(get_all_tags())

        # for t in get_all_tags():
        #     self.ui.tagsList.addItem(t)
        #     color = tag_get_color(t)
        #     if color:
        #         self.ui.tagsList.item(self.ui.tagsList.count()-1).setBackground(QColor(color))

        #self.loadCondition()
        self.ui.typeCombo.insertItems(0,list(load_settings()['file_types'].keys()))
        self.update_visibility()

        if not LITE_MODE:
            self.ui.tagGroupsCombo.insertItems(0,get_all_tag_groups())

        self.ui.conditionCombo.currentIndexChanged.connect(self.update_visibility)
        self.ui.tagsCombo.currentIndexChanged.connect(self.update_tags_visibility)

    def tags_selection_changed(self):
        selected_tags = [self.ui.tagsView.model().itemFromIndex(index).text() for index in self.ui.tagsView.selectedIndexes()]
        self.ui.selectedTagsLabel.setText('Selected tags: '+', '.join(selected_tags))

    def update_visibility(self):
        state = self.ui.conditionCombo.currentText()
        self.ui.nameLabel.setVisible(state == "name")
        self.ui.nameCombo.setVisible(state == "name")
        self.ui.expressionLabel.setVisible(state == "name")
        self.ui.filemask.setVisible(state == "name")
        self.ui.filenameHint.setVisible(state == "name")
        self.ui.ageLabel.setVisible(state == "date")
        self.ui.ageCombo.setVisible(state == "date")
        self.ui.age.setVisible(state == "date")
        self.ui.ageUnitsCombo.setVisible(state == "date")
        #self.ui.ageSpacer.setVisible(state == "date")
        self.ui.sizeLabel.setVisible(state == "size")
        self.ui.sizeCombo.setVisible(state == "size")
        self.ui.size.setVisible(state == "size")
        self.ui.sizeUnitsCombo.setVisible(state == "size")
        self.ui.tagLabel.setVisible(state == "tags")
        self.ui.tagsCombo.setVisible(state == "tags")
        self.ui.tagLabel2.setVisible(state == "tags")
        self.ui.tagsView.setVisible(state == "tags")
        self.ui.selectedTagsLabel.setVisible(state == "tags")
        self.ui.tagGroupsCombo.setVisible(state == "tags" and self.ui.tagsCombo.currentText() == "tags in group")
        self.ui.typeCombo.setVisible(state == "type")
        self.ui.typeLabel.setVisible(state == "type")
        self.ui.typeSwitchCombo.setVisible(state == "type")

    def update_tags_visibility(self):
        state = self.ui.tagsCombo.currentText()
        self.ui.tagLabel2.setVisible(state not in ('no tags', 'any tags', 'tags in group'))
        self.ui.tagsView.setEnabled(state not in ('no tags', 'any tags', 'tags in group'))
        self.ui.selectedTagsLabel.setVisible(state not in ('no tags', 'any tags', 'tags in group'))
        self.ui.tagGroupsCombo.setVisible(state == 'tags in group')

    def load_condition(self, cond={}):
        self.condition = cond
        if cond:
            self.ui.conditionCombo.setCurrentIndex(self.ui.conditionCombo.findText(cond['type']))
            if cond['type'] == 'name':
                self.ui.nameCombo.setCurrentIndex(self.ui.nameCombo.findText(cond['name_switch']))
                self.ui.filemask.setText(cond['filemask'])
            elif cond['type'] == 'date':
                self.ui.ageCombo.setCurrentIndex(self.ui.ageCombo.findText(cond['age_switch']))
                self.ui.age.setText(str(cond['age']))
                self.ui.ageUnitsCombo.setCurrentIndex(self.ui.ageUnitsCombo.findText(cond['age_units']))
            elif cond['type'] == 'size':
                self.ui.sizeCombo.setCurrentIndex(self.ui.sizeCombo.findText(cond['size_switch']))
                self.ui.size.setText(cond['size'])
                self.ui.sizeUnitsCombo.setCurrentIndex(self.ui.sizeUnitsCombo.findText(cond['size_units']))            
            elif cond['type'] == 'tags':
                self.ui.tagsCombo.setCurrentIndex(self.ui.tagsCombo.findText(cond['tag_switch']))
                self.ui.tagGroupsCombo.setVisible(cond['tag_switch'] == 'tags in group')
                if 'tag_group' in cond.keys():
                    self.ui.tagGroupsCombo.setCurrentText(cond['tag_group'])
                if cond['tag_switch'] in ('no tags', 'any tags', 'tags in group'):
                    self.ui.tagLabel2.setVisible(False)
                    self.ui.tagsView.setEnabled(False)

                if not LITE_MODE:
                    for i in range(self.ui.tagsView.model().rowCount()):
                        for k in range(self.ui.tagsView.model().item(i).rowCount()):
                            if self.ui.tagsView.model().item(i).child(k).text() in cond['tags']:
                                # print(self.ui.tagsView.model().item(i).child(k).text())
                                self.ui.tagsView.selectionModel().select(self.ui.tagsView.model().indexFromItem(self.ui.tagsView.model().item(i).child(k)),QItemSelectionModel.Select)
                    
                    self.ui.selectedTagsLabel.setText('Selected tags: '+','.join(cond['tags']))     
                    
            elif cond['type'] == 'type':
                self.ui.typeSwitchCombo.setCurrentIndex(self.ui.typeSwitchCombo.findText(cond['file_type_switch']))
                self.ui.typeCombo.setCurrentIndex(self.ui.typeCombo.findText(cond['file_type']))
                # for row in range(0,self.ui.tagsList.count()):
                #     if self.ui.tagsView.item(row).text() in cond['tags']:
                #         self.ui.tagsView.item(row).setSelected(True)

                # for tagItem in self.ui.tagsList.items():
                #     print(tagItem.text())
                #for tag in cond['tags']:
    def accept(self):
        error = ""
        self.condition['type']=self.ui.conditionCombo.currentText()
        if self.condition['type'] == 'name':
            self.condition['name_switch']=self.ui.nameCombo.currentText()            
            error = "Filemask can't be empty" if self.ui.filemask.text() == "" else ""
            self.condition['filemask']=self.ui.filemask.text()            
        elif self.condition['type'] == 'date':
            self.condition['age_switch']=self.ui.ageCombo.currentText()
            try:            
                self.condition['age']=float(self.ui.age.text())
            except:                
                error = "Incorrect Age value"
            self.condition['age_units']=self.ui.ageUnitsCombo.currentText()
        elif self.condition['type'] == 'size':
            self.condition['size_switch']=self.ui.sizeCombo.currentText()
            try:
                self.condition['size']=float(self.ui.size.text())
            except:
                error = "Incorrect Size value"
            self.condition['size_units']=self.ui.sizeUnitsCombo.currentText()            
        elif self.condition['type'] == 'tags':
            self.condition['tag_switch']=self.ui.tagsCombo.currentText()
            self.condition['tags'] = [index.data() for index in self.ui.tagsView.selectedIndexes()]
            if self.condition['tag_switch'] == 'tags in group':
                self.condition['tag_group'] = self.ui.tagGroupsCombo.currentText()
            if not self.condition['tags'] and not self.condition['tag_switch'] in ('no tags', 'any tags', 'tags in group'):
                error = "You haven't selected any tags"
        elif self.condition['type'] == 'type':      
            self.condition['file_type_switch']=self.ui.typeSwitchCombo.currentText()
            self.condition['file_type']=self.ui.typeCombo.currentText()

        if error:
            QMessageBox.critical(self,"Error",error,QMessageBox.Ok)
        else:
            super(ConditionDialog, self).accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConditionDialog()
    window.show()

    sys.exit(app.exec_())