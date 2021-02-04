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


class Ui_rulesWindow(object):
    def setupUi(self, rulesWindow):
        if not rulesWindow.objectName():
            rulesWindow.setObjectName(u"rulesWindow")
        rulesWindow.setEnabled(True)
        rulesWindow.resize(957, 377)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(rulesWindow.sizePolicy().hasHeightForWidth())
        rulesWindow.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u"DeClutter.ico", QSize(), QIcon.Normal, QIcon.Off)
        rulesWindow.setWindowIcon(icon)
        rulesWindow.setSizeGripEnabled(False)
        rulesWindow.setModal(False)
        self.verticalLayout = QVBoxLayout(rulesWindow)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.addRule = QPushButton(rulesWindow)
        self.addRule.setObjectName(u"addRule")

        self.horizontalLayout.addWidget(self.addRule)

        self.deleteRule = QPushButton(rulesWindow)
        self.deleteRule.setObjectName(u"deleteRule")

        self.horizontalLayout.addWidget(self.deleteRule)

        self.applyRule = QPushButton(rulesWindow)
        self.applyRule.setObjectName(u"applyRule")

        self.horizontalLayout.addWidget(self.applyRule)

        self.moveUp = QPushButton(rulesWindow)
        self.moveUp.setObjectName(u"moveUp")

        self.horizontalLayout.addWidget(self.moveUp)

        self.moveDown = QPushButton(rulesWindow)
        self.moveDown.setObjectName(u"moveDown")

        self.horizontalLayout.addWidget(self.moveDown)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.rulesTable = QTableWidget(rulesWindow)
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


        self.verticalLayout.addLayout(self.verticalLayout_2)


        self.retranslateUi(rulesWindow)

        QMetaObject.connectSlotsByName(rulesWindow)
    # setupUi

    def retranslateUi(self, rulesWindow):
        rulesWindow.setWindowTitle(QCoreApplication.translate("rulesWindow", u"DeClutter: Rules", None))
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
    # retranslateUi

