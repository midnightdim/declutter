import sys
from PySide2.QtUiTools import loadUiType
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QApplication, QListWidget, QDialog, QDialogButtonBox, QFileDialog, QAbstractItemView, QMessageBox
from PySide2.QtCore import (Qt, QAbstractItemModel)
from ui_condition_dialog import Ui_Condition
from declutter_lib import load_settings, SETTINGS_FILE, get_all_tags, tag_get_color

#from PySide6.QtGui import 

class ConditionDialog(QDialog):
    def __init__(self):
        super(ConditionDialog, self).__init__()
        self.ui = Ui_Condition()
        self.ui.setupUi(self)
        self.condition = {}
        self.ui.tagsList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        #self.ui.tagsList.addItems(get_all_tags())
        for t in get_all_tags():
            self.ui.tagsList.addItem(t)
            color = tag_get_color(t)
            if color:
                self.ui.tagsList.item(self.ui.tagsList.count()-1).setBackground(QColor(color))

        #self.loadCondition()
        self.update_visibility()        
        self.ui.conditionCombo.currentIndexChanged.connect(self.update_visibility)
        self.ui.tagsCombo.currentIndexChanged.connect(self.update_tags_visibility)

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
        self.ui.tagsList.setVisible(state == "tags")

    def update_tags_visibility(self):
        state = self.ui.tagsCombo.currentText()
        self.ui.tagLabel2.setVisible(state != "no tags")
        self.ui.tagsList.setEnabled(state != "no tags")

    def loadCondition(self, cond={}):
        self.condition = cond
        if cond:
            self.ui.conditionCombo.setCurrentIndex(self.ui.conditionCombo.findText(cond['type']))
            if cond['type'] == 'name':
                self.ui.nameCombo.setCurrentIndex(self.ui.nameCombo.findText(cond['name_switch']))
                self.ui.filemask.setText(cond['filemask'])
            if cond['type'] == 'date':
                self.ui.ageCombo.setCurrentIndex(self.ui.ageCombo.findText(cond['age_switch']))
                self.ui.age.setText(cond['age'])
                self.ui.ageUnitsCombo.setCurrentIndex(self.ui.ageUnitsCombo.findText(cond['age_units']))
            if cond['type'] == 'size':
                self.ui.sizeCombo.setCurrentIndex(self.ui.sizeCombo.findText(cond['size_switch']))
                self.ui.size.setText(cond['size'])
                self.ui.sizeUnitsCombo.setCurrentIndex(self.ui.sizeUnitsCombo.findText(cond['size_units']))            
            if cond['type'] == 'tags':            
                self.ui.tagsCombo.setCurrentIndex(self.ui.tagsCombo.findText(cond['tag_switch']))
                if cond['tag_switch'] == 'no tags':
                    self.ui.tagLabel2.setVisible(False)
                    self.ui.tagsList.setEnabled(False)
                for row in range(0,self.ui.tagsList.count()):
                    if self.ui.tagsList.item(row).text() in cond['tags']:
                        self.ui.tagsList.item(row).setSelected(True)

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
            self.condition['tags'] = [self.ui.tagsList.item(row).text() for row in range(0,self.ui.tagsList.count()) if self.ui.tagsList.item(row).isSelected()]
            if not self.condition['tags']:
                error = "You haven't selected any tags"

        if error:
            QMessageBox.critical(self,"Error",error,QMessageBox.Ok)
        else:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConditionDialog()
    window.show()

    sys.exit(app.exec_())