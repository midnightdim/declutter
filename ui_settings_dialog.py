# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.0.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_settingsDialog(object):
    def setupUi(self, settingsDialog):
        if not settingsDialog.objectName():
            settingsDialog.setObjectName(u"settingsDialog")
        settingsDialog.setWindowModality(Qt.ApplicationModal)
        settingsDialog.resize(400, 300)
        self.gridLayout = QGridLayout(settingsDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tabWidget = QTabWidget(settingsDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout_4 = QGridLayout(self.tab)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_2 = QLabel(self.tab)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)

        self.ruleExecIntervalEdit = QLineEdit(self.tab)
        self.ruleExecIntervalEdit.setObjectName(u"ruleExecIntervalEdit")
        self.ruleExecIntervalEdit.setMaximumSize(QSize(50, 16777215))
        self.ruleExecIntervalEdit.setMaxLength(8)

        self.horizontalLayout.addWidget(self.ruleExecIntervalEdit)

        self.label_3 = QLabel(self.tab)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_4 = QLabel(self.tab)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_2.addWidget(self.label_4)

        self.styleComboBox = QComboBox(self.tab)
        self.styleComboBox.setObjectName(u"styleComboBox")
        self.styleComboBox.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_2.addWidget(self.styleComboBox)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)


        self.gridLayout_4.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.gridLayout_2 = QGridLayout(self.tab_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.dateDefGroupBox = QGroupBox(self.tab_2)
        self.dateDefGroupBox.setObjectName(u"dateDefGroupBox")
        self.gridLayout_3 = QGridLayout(self.dateDefGroupBox)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(self.dateDefGroupBox)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.radioButton = QRadioButton(self.dateDefGroupBox)
        self.radioButton.setObjectName(u"radioButton")

        self.verticalLayout.addWidget(self.radioButton)

        self.radioButton_2 = QRadioButton(self.dateDefGroupBox)
        self.radioButton_2.setObjectName(u"radioButton_2")

        self.verticalLayout.addWidget(self.radioButton_2)

        self.radioButton_3 = QRadioButton(self.dateDefGroupBox)
        self.radioButton_3.setObjectName(u"radioButton_3")

        self.verticalLayout.addWidget(self.radioButton_3)

        self.radioButton_4 = QRadioButton(self.dateDefGroupBox)
        self.radioButton_4.setObjectName(u"radioButton_4")

        self.verticalLayout.addWidget(self.radioButton_4)

        self.radioButton_5 = QRadioButton(self.dateDefGroupBox)
        self.radioButton_5.setObjectName(u"radioButton_5")

        self.verticalLayout.addWidget(self.radioButton_5)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.gridLayout_3.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.dateDefGroupBox, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_2, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(settingsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)


        self.retranslateUi(settingsDialog)
        self.buttonBox.accepted.connect(settingsDialog.accept)
        self.buttonBox.rejected.connect(settingsDialog.reject)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(settingsDialog)
    # setupUi

    def retranslateUi(self, settingsDialog):
        settingsDialog.setWindowTitle(QCoreApplication.translate("settingsDialog", u"Settings", None))
        self.label_2.setText(QCoreApplication.translate("settingsDialog", u"Process rules every", None))
        self.label_3.setText(QCoreApplication.translate("settingsDialog", u"minutes", None))
        self.label_4.setText(QCoreApplication.translate("settingsDialog", u"Style", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("settingsDialog", u"Main", None))
        self.dateDefGroupBox.setTitle(QCoreApplication.translate("settingsDialog", u"Date definition", None))
        self.label.setText(QCoreApplication.translate("settingsDialog", u"Which date (from file metadata) should be used in rule conditions?", None))
        self.radioButton.setText(QCoreApplication.translate("settingsDialog", u"earliest of modified & created (default)", None))
        self.radioButton_2.setText(QCoreApplication.translate("settingsDialog", u"modified", None))
        self.radioButton_3.setText(QCoreApplication.translate("settingsDialog", u"created", None))
        self.radioButton_4.setText(QCoreApplication.translate("settingsDialog", u"latest of modified & created", None))
        self.radioButton_5.setText(QCoreApplication.translate("settingsDialog", u"last access", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("settingsDialog", u"Date", None))
    # retranslateUi

