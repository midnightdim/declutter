import sys
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (QAction, QApplication, QSystemTrayIcon, QMenu, QDialog, QTableWidgetItem, QAbstractScrollArea, \
    QTableWidgetSelectionRange, QMainWindow, QMessageBox, QStyleFactory)
from PySide2.QtCore import QObject, QThread, Signal, Slot, QTimer
from rule_edit_window import RuleEditWindow
from settings_dialog import SettingsDialog
from ui_rules_window import Ui_rulesWindow
from ui_list_dialog import Ui_listDialog    
from copy import deepcopy
from time import time
import os
import logging
from datetime import datetime
import requests
import webbrowser
from declutter_lib import LITE_MODE

if LITE_MODE:
    from declutter_lib_core import *
else:
    from declutter_lib import *
    from declutter_tagger import TaggerWindow

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
        self.settings = load_settings()
        if 'style' in self.settings.keys():
            self.change_style(self.settings['style'])
        
        self.ui.addRule.clicked.connect(self.add_rule)      
        self.load_rules()
        self.ui.rulesTable.cellDoubleClicked.connect(self.edit_rule)
        self.ui.deleteRule.clicked.connect(self.delete_rule)
        self.ui.applyRule.clicked.connect(self.apply_rule)
        #self.ui.moveUp.clicked.connect(self.start_thread)
        self.trayIcon.messageClicked.connect(self.message_clicked)
        self.trayIcon.activated.connect(self.tray_activated)
        self.trayIcon.setToolTip("DeClutter runs every " + str(float(self.settings['rule_exec_interval']/60)) + " minute(s)")
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
        self.ui.actionOpen_log_file.triggered.connect(self.open_log_file)
        self.ui.actionClear_log_file.triggered.connect(self.clear_log_file)
        self.ui.actionSettings.triggered.connect(self.show_settings)
        self.ui.actionAbout.triggered.connect(self.show_about)

        if not LITE_MODE:
            self.ui.actionOpen_Tagger.triggered.connect(self.show_tagger)
            self.tagger = TaggerWindow()
            self.ui.actionManage_Tags.triggered.connect(self.tagger.manage_tags)            
        else:
            self.ui.menuOptions_2.removeAction(self.ui.actionManage_Tags)
            self.ui.toolBar.removeAction(self.ui.actionOpen_Tagger)
        
        self.ui.actionMove_up.triggered.connect(self.move_rule_up)
        self.ui.actionMove_down.triggered.connect(self.move_rule_down)

        self.service_runs = False

        self.timer = QTimer(self)
        self.timer.setInterval(int(self.settings['rule_exec_interval']*1000))
        #self.connect(timer, SIGNAL("timeout()"), self.start_thread)
        self.timer.timeout.connect(self.start_thread)
        self.timer.start()

        instanced_thread = new_version_checker(self)
        instanced_thread.start()
        #DoubleClicked.connect(self.editRule)
    
    # def not_implemented_yet(self):   
    #     QMessageBox.information(self,"Sorry", "This feature is not implemented yet!")

    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.setVisible(True)

    def move_rule_up(self):
        rule_idx = self.ui.rulesTable.selectedIndexes()[0].row()
        if rule_idx:
            rule_id = int(self.settings['rules'][rule_idx]['id'])
            #print("swapping",self.settings['rules'][rule_idx]['name'],"and",self.settings['rules'][rule_idx-1]['name'])
            # print(self.settings['rules'][rule_idx]['id'])
            # print(self.settings['rules'][rule_idx-1]['id'])
            self.settings['rules'][rule_idx]['id'] = self.settings['rules'][rule_idx-1]['id']
            self.settings['rules'][rule_idx-1]['id'] = rule_id

            rules = deepcopy(self.settings['rules'])
            rule_ids = [int(r['id']) for r in rules if 'id' in r.keys()] 
            rule_ids.sort()

            self.settings['rules'] = []
            i = 0
            for rule_id in rule_ids:
                i+=1
                rule = get_rule_by_id(rule_id, rules)
                rule['id'] = i # renumbering rules
                self.settings['rules'].append(rule)

            save_settings(SETTINGS_FILE, self.settings)
            self.load_rules()
            self.ui.rulesTable.selectRow(rule_idx-1)

    def move_rule_down(self):
        rule_idx = self.ui.rulesTable.selectedIndexes()[0].row()
        if rule_idx < self.ui.rulesTable.rowCount()-1:
            rule_id = int(self.settings['rules'][rule_idx]['id'])
            self.settings['rules'][rule_idx]['id'] = self.settings['rules'][rule_idx+1]['id']
            self.settings['rules'][rule_idx+1]['id'] = rule_id

            rules = deepcopy(self.settings['rules'])
            rule_ids = [int(r['id']) for r in rules if 'id' in r.keys()] 
            rule_ids.sort()

            self.settings['rules'] = []
            i = 0
            for rule_id in rule_ids:
                i+=1
                rule = get_rule_by_id(rule_id, rules)
                rule['id'] = i # renumbering rules
                self.settings['rules'].append(rule)

            save_settings(SETTINGS_FILE, self.settings)
            self.load_rules()
            self.ui.rulesTable.selectRow(rule_idx+1)

    def show_about(self):
        QMessageBox.about(self,"About DeClutter", "DeClutter version "+str(VERSION)+"\nhttps://declutter.top\nAuthor: Dmitry Beloglazov\nTelegram: @beloglazov")

    def show_settings(self):
        settings_window = SettingsDialog()
        if settings_window.exec_():
            self.settings = load_settings()
            self.trayIcon.setToolTip("DeClutter runs every " + str(float(self.settings['rule_exec_interval']/60)) + " minute(s)")
            self.timer.setInterval(int(self.settings['rule_exec_interval']*1000))

    def change_style(self, style_name):
        QApplication.setStyle(QStyleFactory.create(style_name))

    def open_log_file(self):
        os.startfile(LOG_FILE)

    def clear_log_file(self):
        reply = QMessageBox.question(self, "Warning",
        "Are you sure you want to clear the log?",
        QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                with open(LOG_FILE, 'w'):
                    pass
            except Exception as e:
                logging.exception(f'exception {e}')  

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
        if not self.service_runs:
            self.service_runs = True
            instanced_thread = declutter_service(self)
            instanced_thread.start()
        else:
            print("Service still running, skipping the scheduled exec") 
    
    def add_rule(self):
        self.rule_window = RuleEditWindow()
        if self.rule_window.exec_():
            rule = self.rule_window.rule
            rule['id'] = max([int(r['id']) for r in self.settings['rules'] if 'id' in r.keys()])+1 if self.settings['rules'] else 1
            self.settings['rules'].append(rule)
        save_settings(SETTINGS_FILE, self.settings)
        self.load_rules()

    def edit_rule(self, r, c):
        if c == 1: # Enabled/Disabled is clicked
            self.settings['rules'][r]['enabled'] = not self.settings['rules'][r]['enabled']
            save_settings(SETTINGS_FILE, self.settings)
        else:
            rule = deepcopy(self.settings['rules'][r])
            self.rule_window = RuleEditWindow()
            self.rule_window.load_rule(rule)
            if self.rule_window.exec_():
                self.settings['rules'][r] = self.rule_window.rule
        save_settings(SETTINGS_FILE, self.settings)
        self.load_rules()
        
    def delete_rule(self):
        del_indexes = [r.row() for r in self.ui.rulesTable.selectedIndexes()]

        if del_indexes:
            del_names = [r['name'] for r in self.settings['rules'] if self.settings['rules'].index(r) in del_indexes]

            reply = QMessageBox.question(self, "Warning",
            "Are you sure you want to delete selected rules:\n"+"\n".join(del_names)+"\n?",
            QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                for ind in sorted(del_indexes, reverse=True):
                    del self.settings['rules'][ind]            
                    self.ui.rulesTable.removeRow(ind)

                self.ui.rulesTable.setRangeSelected(QTableWidgetSelectionRange(0,0,self.ui.rulesTable.rowCount()-1,self.ui.rulesTable.columnCount()-1), False)

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
        self.settings = load_settings()       
        self.ui.rulesTable.setRowCount(len(self.settings['rules']))
        i = 0
        rules = [(int(r['id']), r) for r in self.settings['rules'] if 'id' in r.keys()] 
        rules.sort(key=lambda y:y[0])

        for id, rule in rules:
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

        if not LITE_MODE:
            self.showTaggerWindow = QAction("Tagger", self)
            self.showTaggerWindow.triggered.connect(self.show_tagger)

        self.showSettingsWindow = QAction("Settings", self)
        self.showSettingsWindow.triggered.connect(self.show_settings)

        self.quitAction = QAction("Quit", self)
        self.quitAction.triggered.connect(QApplication.quit)

    def create_tray_icon(self):
        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction(self.showRulesWindow)
        if not LITE_MODE:
            self.trayIconMenu.addAction(self.showTaggerWindow)
        self.trayIconMenu.addAction(self.showSettingsWindow)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)

        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)
        self.trayIcon.setIcon(QIcon('DeClutter.ico'))        
        self.trayIcon.setVisible(True)
        self.trayIcon.show()

    def setVisible(self, visible):
        self.minimizeAction.setEnabled(visible)
        self.maximizeAction.setEnabled(not self.isMaximized())
        self.restoreAction.setEnabled(self.isMaximized() or not visible)
        super().setVisible(visible)        

    def show_tagger(self):        
        if not LITE_MODE:
            self.tagger.show()    
            self.tagger.init_tag_checkboxes()  # TBD this doesn't look like the best solution

    
    @Slot(str, list)
    def show_tray_message(self,message,details):
        if message:
            self.trayIcon.showMessage(
                "DeClutter",
                message,
                QSystemTrayIcon.Information,
                15000,
            )
        # logging.debug("Details"+str(details))
        self.service_run_details = details if details else self.service_run_details
        self.service_runs = False

class service_signals(QObject):
    signal1 = Signal(str,list) 

class declutter_service(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.signals = service_signals()
        self.signals.signal1.connect(parent.show_tray_message)
        self.starting_seconds = time()
        # self.settings = load_settings(SETTINGS_FILE)

    def run(self):
        print("Processing rules...",datetime.now())
        details = []
        report, details = apply_all_rules(load_settings())
        msg = ""
        for key in report.keys():
            msg+= key + ": " + str(report[key]) + "\n" if report[key] > 0 else ""
        if len(msg)>0:
            msg = "Processed files and folders:\n" + msg
        self.signals.signal1.emit(msg, details)

class new_version_checker(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)

    def run(self):
        try:
            url = 'http://declutter.top/latest_version.txt'
            r = requests.get(url)
            if r and r.text.strip()>str(load_settings()['version']):
                reply = QMessageBox.question(window, "New version: " + r.text.strip(),
                r"There's a new version of DeClutter available. Download now?",
                QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    try:
                        webbrowser.open('http://declutter.top/DeClutter.latest.exe')
                    except Exception as e:
                        logging.exception(f'exception {e}')

        except Exception as e:
            logging.exception(f'exception {e}')


def main():
    app = QApplication(sys.argv)
    QApplication.setQuitOnLastWindowClosed(False)

    logging.info("DeClutter started")
    app.setWindowIcon(QIcon('DeClutter.ico'))

    window = RulesWindow()
    window.show()
    if LITE_MODE:
        window.setWindowTitle('DeClutter Lite (beta) ' + VERSION)
    else:
        window.setWindowTitle('DeClutter (beta) ' + VERSION)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()