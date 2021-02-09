# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tagger_window.ui'
##
## Created by: Qt User Interface Compiler version 6.0.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import DeClutter_rc

class Ui_taggerWindow(object):
    def setupUi(self, taggerWindow):
        if not taggerWindow.objectName():
            taggerWindow.setObjectName(u"taggerWindow")
        taggerWindow.resize(1000, 600)
        icon = QIcon()
        icon.addFile(u":/images/DeClutter.ico", QSize(), QIcon.Normal, QIcon.Off)
        taggerWindow.setWindowIcon(icon)
        self.actionManage_Tags = QAction(taggerWindow)
        self.actionManage_Tags.setObjectName(u"actionManage_Tags")
        self.centralwidget = QWidget(taggerWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.treeView = QTreeView(self.centralwidget)
        self.treeView.setObjectName(u"treeView")
        self.treeView.setRootIsDecorated(False)
        self.treeView.setItemsExpandable(False)
        self.treeView.setSortingEnabled(True)
        self.treeView.setExpandsOnDoubleClick(False)

        self.gridLayout.addWidget(self.treeView, 0, 0, 1, 1)

        taggerWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(taggerWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1000, 21))
        self.menuOptions = QMenu(self.menubar)
        self.menuOptions.setObjectName(u"menuOptions")
        taggerWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(taggerWindow)
        self.statusbar.setObjectName(u"statusbar")
        taggerWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuOptions.menuAction())
        self.menuOptions.addAction(self.actionManage_Tags)

        self.retranslateUi(taggerWindow)

        QMetaObject.connectSlotsByName(taggerWindow)
    # setupUi

    def retranslateUi(self, taggerWindow):
        taggerWindow.setWindowTitle(QCoreApplication.translate("taggerWindow", u"DeClutter: Tagger", None))
        self.actionManage_Tags.setText(QCoreApplication.translate("taggerWindow", u"Manage Tags", None))
        self.menuOptions.setTitle(QCoreApplication.translate("taggerWindow", u"Options", None))
    # retranslateUi

