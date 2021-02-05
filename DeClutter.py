import sys
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QWidget, QApplication, QSystemTrayIcon, QMenu, QDialog, QTableWidgetItem, QAbstractScrollArea, QTableWidgetSelectionRange, QMainWindow
from PySide6.QtCore import QObject, QThread, Signal, Slot, QTimer
from rule_edit_window import RuleEditWindow
from ui_rules_window import Ui_rulesWindow
from ui_list_dialog import Ui_listDialog
from declutter_lib import *
from copy import deepcopy
from time import time

#SETTINGS_FILE = os.path.join(APP_FOLDER, "settings.json")

class RulesWindow(QMainWindow):
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
        self.settings = load_settings(SETTINGS_FILE)
        
        self.ui.addRule.clicked.connect(self.add_rule)      
        self.load_rules()
        self.ui.rulesTable.cellDoubleClicked.connect(self.edit_rule)
        self.ui.deleteRule.clicked.connect(self.delete_rule)
        self.ui.applyRule.clicked.connect(self.apply_rule)
        #self.ui.moveUp.clicked.connect(self.start_thread)
        self.trayIcon.messageClicked.connect(self.message_clicked)
        self.service_run_details = []
        #self.start_thread()        

        self.ui.addRule.setVisible(False)
        self.ui.applyRule.setVisible(False)
        self.ui.deleteRule.setVisible(False)
        self.ui.moveUp.setVisible(False)
        self.ui.moveDown.setVisible(False)
    
        self.ui.actionAdd.triggered.connect(self.add_rule)
        self.ui.actionDelete.triggered.connect(self.delete_rule)
        self.ui.actionExecute.triggered.connect(self.apply_rule)
        # self.ui.actionMove_up.triggered.connect(self.move_rule_up)
        # self.ui.actionMove_down.triggered.connect(self.move_rule_down)
        
        self.timer = QTimer(self)
        self.timer.setInterval(20000)
        #self.connect(timer, SIGNAL("timeout()"), self.start_thread)
        self.timer.timeout.connect(self.start_thread)
        self.timer.start()

        #DoubleClicked.connect(self.editRule)
  
    def message_clicked(self):
        msgBox = QDialog(self)
        msgBox.ui = Ui_listDialog()
        msgBox.ui.setupUi(msgBox)
        msgBox.setWindowTitle("Rule executed")
        affected = self.service_run_details
        if affected:
            msgBox.ui.label.setText(str(len(affected)) + " file(s) affected by this rule:")
            msgBox.ui.listWidget.addItems(affected)
        else:
            msgBox.ui.listWidget.setVisible(False)
            msgBox.ui.label.setText("No files affected by this rule.")
        msgBox.exec_()
        self.service_run_details = []

    def start_thread(self):
        instanced_thread = declutter_service(self)
        instanced_thread.start()    
    
    def add_rule(self):
        #print("Opening rule window")
        self.rule_window = RuleEditWindow()
        self.rule_window.exec_()
        if self.rule_window.updated:
            #print("updating")
            self.settings['rules'].append(self.rule_window.rule)
            #print(self.settings['rules'])
        self.load_rules()
        save_settings(SETTINGS_FILE, self.settings)

    def edit_rule(self, r, c):
        rule = deepcopy(self.settings['rules'][r])
        self.rule_window = RuleEditWindow()
        self.rule_window.load_rule(rule)
        self.rule_window.exec_() # TBD this should return 1 or 0 for Save and Cancel, but it doesn't, so I had to use .updated flag, should be revised
        if self.rule_window.updated:
            self.settings['rules'][r] = self.rule_window.rule
        self.load_rules()
        save_settings(SETTINGS_FILE, self.settings)

    def delete_rule(self):
        #r = self.ui.rulesTable.currentRow()
        #print(r)
        del_indexes = [r.row() for r in self.ui.rulesTable.selectedIndexes()]

        for ind in sorted(del_indexes, reverse=True):
            #print("removing",r.row())
            #print(self.settings['rules'][r.row()]['name'])
            del self.settings['rules'][ind]
            #self.ui.rulesTable.removeRow(r.row())
            self.ui.rulesTable.removeRow(ind)
        #print(self.ui.rulesTable.selectedIndexes())
        self.ui.rulesTable.setRangeSelected(QTableWidgetSelectionRange(0,0,self.ui.rulesTable.rowCount()-1,self.ui.rulesTable.columnCount()-1), False)
        #print('deleting',self.settings['rules'][r])
        #del self.settings['rules'][r]
        #self.ui.rulesTable.removeRow(r)
        #self.loadRules()

    def apply_rule(self):
        rule = deepcopy(self.settings['rules'][self.ui.rulesTable.selectedIndexes()[0].row()])
        rule['enabled'] = True
        report, affected = apply_rule(rule)

        msgBox = QDialog(self)
        msgBox.ui = Ui_listDialog()
        msgBox.ui.setupUi(msgBox)
        msgBox.setWindowTitle("Rule executed")
        
        if affected:
            msgBox.ui.label.setText(str(len(affected)) + " file(s) affected by this rule:")
            msgBox.ui.listWidget.addItems(affected)
        else:
            msgBox.ui.listWidget.setVisible(False)
            msgBox.ui.label.setText("No files affected by this rule.")
        msgBox.exec_()

    def load_rules(self):
        #print(self.settings['rules'])
        #self.ui.rulesTable.insertRow(1)
       
        self.ui.rulesTable.setRowCount(len(self.settings['rules']))
        i = 0
        # self.ui.rulesTable.setItem(0,0,newItem)
        
        for rule in self.settings['rules']:
            newItem = QTableWidgetItem(rule['name'])
            self.ui.rulesTable.setItem(i,0,newItem)
            newItem = QTableWidgetItem("Enabled" if rule['enabled'] else "Disabled")
            self.ui.rulesTable.setItem(i,1,newItem)            
            newItem = QTableWidgetItem(rule['action'])
            self.ui.rulesTable.setItem(i,2,newItem)
            newItem = QTableWidgetItem(','.join(rule['folders']))
            self.ui.rulesTable.setItem(i,3,newItem)            
            i+=1
        self.ui.rulesTable.setColumnWidth(0,200)
        self.ui.rulesTable.setColumnWidth(1,80)
        self.ui.rulesTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

    def create_actions(self):
        self.showRulesWindow = QAction("Rules", self)
        self.showRulesWindow.triggered.connect(self.showNormal)

        self.showTaggerWindow = QAction("Tagger", self)
        self.showTaggerWindow.triggered.connect(self.showTagger)

        self.showSettingsWindow = QAction("Settings", self)
        self.showSettingsWindow.triggered.connect(self.showSettings)

        self.quitAction = QAction("Quit", self)
        self.quitAction.triggered.connect(QApplication.quit)

    def create_tray_icon(self):
        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction(self.showRulesWindow)
        self.trayIconMenu.addAction(self.showTaggerWindow)
        self.trayIconMenu.addAction(self.showSettingsWindow)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)

        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)
        self.trayIcon.setIcon(QIcon('DeClutter.ico'))        

    def setVisible(self, visible):
        self.minimizeAction.setEnabled(visible)
        self.maximizeAction.setEnabled(not self.isMaximized())
        self.restoreAction.setEnabled(self.isMaximized() or not visible)
        super().setVisible(visible)        

    def showTagger(self):
        print("Showing tagger")

    def showSettings(self):
        print("Showing settings")

    @Slot(str, list)
    def show_tray_message(self,message,details):
        self.trayIcon.showMessage(
            "DeClutter",
            message,
            QSystemTrayIcon.Information,
            15000,
        )
        self.service_run_details = details

    # @Slot(list)
    # def update_details(self,details):
    #     self.service_run_details = details
    #     print(details)


class service_signals(QObject):
    signal1 = Signal(str,list)
    #signal_str2 = Signal(list)
    #signal_int = Signal(int)    

class declutter_service(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        # Instantiate signals and connect signals to the slots
        self.signals = service_signals()
        self.signals.signal1.connect(parent.show_tray_message)
        #self.signals.signal_str.connect(parent.show_tray_message)
        #self.signals.signal_str2.connect(parent.update_details)
        # self.signals.signal_int.connect(parent.update_int_field)
        self.starting_seconds = time()
        self.settings = load_settings(SETTINGS_FILE)

    def run(self):
        print("Service launched")
        #print("Runs every",self.settings['rule_exec_interval'],"seconds")
        # Do something on the worker thread
        #a = 1 + 1
        # Emit signals whenever you want
        #self.signals.signal_int.emit(a)

        # self.signals.signal_str.emit("DeClutter service run") 
        #print("Run")
        #while True:            
            #delta_from_last = time() - self.starting_seconds
            #print(delta_from_last)
        #if delta_from_last >= self.settings['rule_exec_interval']: #TBD have to get settings from parent!      
            #print("Delta passed")
            #self.starting_seconds = time()
            #delta_from_last = 0
        report, details = apply_all_rules(self.settings)
        msg = ""
        for key in report.keys():
            msg+= key + ": " + str(report[key]) + "\n" if report[key] > 0 else ""
        if len(msg)>0:
            #print(details)
            self.signals.signal1.emit("Processed files and folders:\n" + msg, details)
            #self.sleep(self.settings['rule_exec_interval'])                    

def main():
    app = QApplication(sys.argv)
    #QApplication.setQuitOnLastWindowClosed(False)

    window = RulesWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()