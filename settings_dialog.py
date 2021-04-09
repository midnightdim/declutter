import sys
from PySide2.QtUiTools import loadUiType
# from PySide2.QtGui import QColor
from PySide2.QtWidgets import QApplication, QDialog, QMessageBox, QSpacerItem, QLineEdit, QPushButton, QStyleFactory, QSizePolicy, QLabel, QTableWidgetItem, QHeaderView
from PySide2.QtCore import Qt
from declutter_lib import load_settings, save_settings, SETTINGS_FILE

from ui_settings_dialog import Ui_settingsDialog

class SettingsDialog(QDialog):
    def __init__(self):
        super(SettingsDialog, self).__init__()
        self.ui = Ui_settingsDialog()
        self.ui.setupUi(self)
        self.initialize()

    def initialize(self):
        self.settings = load_settings()
        # settings_window = QDialog(self)
        # settings_window.ui = Ui_settingsDialog()
        # settings_window.ui.setupUi(settings_window)
        i=0
        self.format_fields={}
        for f in self.settings['file_types']:
            self.ui.fileTypesTable.insertRow(i)
            item = QTableWidgetItem(f)
            if f in ('Audio','Video','Image'):
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.ui.fileTypesTable.setItem(i,0,item)
            self.ui.fileTypesTable.setItem(i,1,QTableWidgetItem(self.settings['file_types'][f]))

            # self.ui.fileTypesGridLayout.addWidget(QLabel(f),i,0)
            # self.format_fields[f] = QLineEdit(self.settings['file_types'][f])
            # self.ui.fileTypesGridLayout.addWidget(self.format_fields[f],i,1)
            i+=1
        
        # self.ui.fileFormatsTable.horizontalHeader().setSectionResizeMode()

        # verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # addnew_button = QPushButton("Add new")
        # addnew_button.clicked.connect(self.add_new_file_type)
        # self.ui.fileTypesGridLayout.addWidget(addnew_button,i,0)
        # self.ui.fileTypesGridLayout.addItem(verticalSpacer,i+1,0)

        # self.ui.fileTypesTable.cellDoubleClicked.connect(self.table_dblclicked)
        self.ui.addFileTypeButton.clicked.connect(self.add_new_file_type)
        self.ui.fileTypesTable.cellActivated.connect(self.cell_entered)
        self.ui.fileTypesTable.cellChanged.connect(self.cell_changed, Qt.QueuedConnection)

        default_style_name = QApplication.style().objectName().lower()
        result = []
        for style in QStyleFactory.keys():
            if style.lower() == default_style_name:
                result.insert(0, style)
            else:
                result.append(style)

        self.ui.styleComboBox.addItems(result)
        self.ui.styleComboBox.textActivated.connect(self.change_style)

        rbs = [c for c in self.ui.dateDefGroupBox.children() if 'QRadioButton' in str(type(c))] # TBD vN this is not very safe
        rbs[self.settings['date_type']].setChecked(True)
        self.ui.ruleExecIntervalEdit.setText(str(self.settings['rule_exec_interval']/60))

    def cell_entered(self,x,y):
        print('entered',x,y)

    def cell_changed(self,row,col):
        if col == 0:
            settings = load_settings()
            new_value = self.ui.fileTypesTable.item(row,0).text()
            if new_value in settings['file_types'].keys(): 
                QMessageBox.critical(self, "Error", "Duplicate format name, please change it")
                self.ui.fileTypesTable.editItem(self.ui.fileTypesTable.item(row,0))
                return False
            if row < len(settings['file_types']): #it's not a new format
                prev_value = list(settings['file_types'].keys())[row]  # TBD this is unsafe and will cause bugs on non-Win systems        
                if new_value != prev_value and new_value:
                    # print('updating settings and rules')
                    settings['file_types'][new_value]=settings['file_types'][prev_value]
                    del settings['file_types'][prev_value]
                    for i in range(0,len(settings['rules'])):
                        for k in range (0,len(settings['rules'][i]['conditions'])):
                            c = settings['rules'][i]['conditions'][k]
                            if c['type'] == 'type' and c['file_type'] == prev_value:
                                settings['rules'][i]['conditions'][k]['file_type'] = new_value
                    save_settings(SETTINGS_FILE,settings)

                if new_value == "":
                    count = 0
                    for i in range(0,len(settings['rules'])):
                        for k in range (0,len(settings['rules'][i]['conditions'])):
                            c = settings['rules'][i]['conditions'][k]
                            if c['type'] == 'type' and c['file_type'] == prev_value:
                                count+=1
                    used_in_rules = "\nIt's used in "+str(count)+" condition(s) (which won't be removed)." if count>0 else ""
                    # TBD remove orphaned conditions
                    reply = QMessageBox.question(self, "Warning",
                        "This will delete the format. Are you sure?"+used_in_rules,
                        QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        del settings['file_types'][prev_value]
                        save_settings(SETTINGS_FILE,settings)
                        self.ui.fileTypesTable.removeRow(row)
                    else:
                        self.ui.fileTypesTable.item(row,0).setText(prev_value)


    # def table_dblclicked(self,row,col):
    #     print(row,col)

    def add_new_file_type(self):
        self.ui.fileTypesTable.insertRow(self.ui.fileTypesTable.rowCount())
        # i = self.ui.fileTypesGridLayout.rowCount() - 2
        # button = self.ui.fileTypesGridLayout.itemAtPosition(i,0).widget()
        # self.ui.fileTypesGridLayout.removeWidget(button)
        # button.hide()
        # # self.ui.fileTypesGridLayout.takeAt(0)

        # # self.ui.fileTypesGridLayout.removeWidget(self.addnew_button)
        # # self.ui.fileTypesGridLayout.removeWidget(QPushButton())
        # self.ui.fileTypesGridLayout.addWidget(QLineEdit(),i,0)
        # self.ui.fileTypesGridLayout.addWidget(QLineEdit(),3,1)

    def accept(self):
        rbs = [c for c in self.ui.dateDefGroupBox.children() if 'QRadioButton' in str(type(c))]
        for c in rbs:
            if c.isChecked():
                self.settings['date_type'] = rbs.index(c)
        self.settings['rule_exec_interval']=float(self.ui.ruleExecIntervalEdit.text())*60
        self.settings['style'] = self.ui.styleComboBox.currentText()

        # for f in self.format_fields:
        #     self.settings['file_types'][f] = self.format_fields[f].text() #TBD add validation
        
        self.settings['file_types'] = {}
        # TBD add validation
        for i in range(0,self.ui.fileTypesTable.rowCount()):
            if self.ui.fileTypesTable.item(i,0) and self.ui.fileTypesTable.item(i,0).text():
                self.settings['file_types'][self.ui.fileTypesTable.item(i,0).text()] = self.ui.fileTypesTable.item(i,1).text()

        save_settings(SETTINGS_FILE, self.settings)
        super(SettingsDialog, self).accept()

    def change_style(self, style_name):
        QApplication.setStyle(QStyleFactory.create(style_name))        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsDialog()
    window.show()

    sys.exit(app.exec_())