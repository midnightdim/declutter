# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rules_window.ui'
##
## Created by: Qt User Interface Compiler version 6.0.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import DeClutter_rc

class Ui_rulesWindow(object):
    def setupUi(self, rulesWindow):
        if not rulesWindow.objectName():
            rulesWindow.setObjectName(u"rulesWindow")
        rulesWindow.resize(1028, 491)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(rulesWindow.sizePolicy().hasHeightForWidth())
        rulesWindow.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u":/images/DeClutter.ico", QSize(), QIcon.Normal, QIcon.Off)
        rulesWindow.setWindowIcon(icon)
        self.actionAdd = QAction(rulesWindow)
        self.actionAdd.setObjectName(u"actionAdd")
        icon1 = QIcon()
        icon1.addFile(u"icons/document-new.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionAdd.setIcon(icon1)
        self.actionOpen_log_file = QAction(rulesWindow)
        self.actionOpen_log_file.setObjectName(u"actionOpen_log_file")
        self.actionClear_log_file = QAction(rulesWindow)
        self.actionClear_log_file.setObjectName(u"actionClear_log_file")
        self.actionDelete = QAction(rulesWindow)
        self.actionDelete.setObjectName(u"actionDelete")
        icon2 = QIcon()
        icon2.addFile(u"icons/trash.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionDelete.setIcon(icon2)
        self.actionExecute = QAction(rulesWindow)
        self.actionExecute.setObjectName(u"actionExecute")
        icon3 = QIcon()
        icon3.addFile(u"icons/media-play.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionExecute.setIcon(icon3)
        self.actionMove_up = QAction(rulesWindow)
        self.actionMove_up.setObjectName(u"actionMove_up")
        icon4 = QIcon()
        icon4.addFile(u"icons/arrow-thin-up.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionMove_up.setIcon(icon4)
        self.actionMove_down = QAction(rulesWindow)
        self.actionMove_down.setObjectName(u"actionMove_down")
        icon5 = QIcon()
        icon5.addFile(u"icons/arrow-thin-down.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionMove_down.setIcon(icon5)
        self.actionSettings = QAction(rulesWindow)
        self.actionSettings.setObjectName(u"actionSettings")
        self.actionAbout = QAction(rulesWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.centralwidget = QWidget(rulesWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.addRule = QPushButton(self.centralwidget)
        self.addRule.setObjectName(u"addRule")

        self.horizontalLayout.addWidget(self.addRule)

        self.deleteRule = QPushButton(self.centralwidget)
        self.deleteRule.setObjectName(u"deleteRule")

        self.horizontalLayout.addWidget(self.deleteRule)

        self.applyRule = QPushButton(self.centralwidget)
        self.applyRule.setObjectName(u"applyRule")

        self.horizontalLayout.addWidget(self.applyRule)

        self.moveUp = QPushButton(self.centralwidget)
        self.moveUp.setObjectName(u"moveUp")

        self.horizontalLayout.addWidget(self.moveUp)

        self.moveDown = QPushButton(self.centralwidget)
        self.moveDown.setObjectName(u"moveDown")

        self.horizontalLayout.addWidget(self.moveDown)

        self.horizontalSpacer = QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.rulesTable = QTableWidget(self.centralwidget)
        if (self.rulesTable.columnCount() < 4):
            self.rulesTable.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.rulesTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.rulesTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.rulesTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.rulesTable.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.rulesTable.setObjectName(u"rulesTable")
        self.rulesTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.rulesTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.rulesTable.setAlternatingRowColors(True)
        self.rulesTable.setColumnCount(4)
        self.rulesTable.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_2.addWidget(self.rulesTable)


        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        rulesWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(rulesWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1028, 21))
        self.menuOptions = QMenu(self.menubar)
        self.menuOptions.setObjectName(u"menuOptions")
        self.menuOptions_2 = QMenu(self.menubar)
        self.menuOptions_2.setObjectName(u"menuOptions_2")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        rulesWindow.setMenuBar(self.menubar)
        self.toolBar = QToolBar(rulesWindow)
        self.toolBar.setObjectName(u"toolBar")
        rulesWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.menubar.addAction(self.menuOptions.menuAction())
        self.menubar.addAction(self.menuOptions_2.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuOptions.addAction(self.actionOpen_log_file)
        self.menuOptions.addAction(self.actionClear_log_file)
        self.menuOptions_2.addAction(self.actionSettings)
        self.menuHelp.addAction(self.actionAbout)
        self.toolBar.addAction(self.actionAdd)
        self.toolBar.addAction(self.actionDelete)
        self.toolBar.addAction(self.actionExecute)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionMove_up)
        self.toolBar.addAction(self.actionMove_down)

        self.retranslateUi(rulesWindow)

        QMetaObject.connectSlotsByName(rulesWindow)
    # setupUi

    def retranslateUi(self, rulesWindow):
        rulesWindow.setWindowTitle(QCoreApplication.translate("rulesWindow", u"DeClutter: Rules", None))
        self.actionAdd.setText(QCoreApplication.translate("rulesWindow", u"Add", None))
#if QT_CONFIG(tooltip)
        self.actionAdd.setToolTip(QCoreApplication.translate("rulesWindow", u"Add", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.actionAdd.setShortcut(QCoreApplication.translate("rulesWindow", u"Ctrl+N", None))
#endif // QT_CONFIG(shortcut)
        self.actionOpen_log_file.setText(QCoreApplication.translate("rulesWindow", u"Open log file", None))
        self.actionClear_log_file.setText(QCoreApplication.translate("rulesWindow", u"Clear log file", None))
        self.actionDelete.setText(QCoreApplication.translate("rulesWindow", u"Delete", None))
#if QT_CONFIG(shortcut)
        self.actionDelete.setShortcut(QCoreApplication.translate("rulesWindow", u"Del", None))
#endif // QT_CONFIG(shortcut)
        self.actionExecute.setText(QCoreApplication.translate("rulesWindow", u"Execute", None))
        self.actionMove_up.setText(QCoreApplication.translate("rulesWindow", u"Move up", None))
#if QT_CONFIG(shortcut)
        self.actionMove_up.setShortcut(QCoreApplication.translate("rulesWindow", u"Up", None))
#endif // QT_CONFIG(shortcut)
        self.actionMove_down.setText(QCoreApplication.translate("rulesWindow", u"Move down", None))
#if QT_CONFIG(shortcut)
        self.actionMove_down.setShortcut(QCoreApplication.translate("rulesWindow", u"Down", None))
#endif // QT_CONFIG(shortcut)
        self.actionSettings.setText(QCoreApplication.translate("rulesWindow", u"Settings", None))
        self.actionAbout.setText(QCoreApplication.translate("rulesWindow", u"About", None))
        self.addRule.setText(QCoreApplication.translate("rulesWindow", u"Add", None))
        self.deleteRule.setText(QCoreApplication.translate("rulesWindow", u"Delete", None))
        self.applyRule.setText(QCoreApplication.translate("rulesWindow", u"Apply", None))
        self.moveUp.setText(QCoreApplication.translate("rulesWindow", u"Move Up", None))
        self.moveDown.setText(QCoreApplication.translate("rulesWindow", u"Move Down", None))
        ___qtablewidgetitem = self.rulesTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("rulesWindow", u"Name", None));
        ___qtablewidgetitem1 = self.rulesTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("rulesWindow", u"Status", None));
        ___qtablewidgetitem2 = self.rulesTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("rulesWindow", u"Action", None));
        ___qtablewidgetitem3 = self.rulesTable.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("rulesWindow", u"Source(s)", None));
        self.menuOptions.setTitle(QCoreApplication.translate("rulesWindow", u"Tools", None))
        self.menuOptions_2.setTitle(QCoreApplication.translate("rulesWindow", u"Options", None))
        self.menuHelp.setTitle(QCoreApplication.translate("rulesWindow", u"Help", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("rulesWindow", u"toolBar", None))
    # retranslateUi

