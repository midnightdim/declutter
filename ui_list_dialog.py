# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'list_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.0.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_listDialog(object):
    def setupUi(self, listDialog):
        if not listDialog.objectName():
            listDialog.setObjectName(u"listDialog")
        listDialog.setWindowModality(Qt.ApplicationModal)
        listDialog.resize(570, 300)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(listDialog.sizePolicy().hasHeightForWidth())
        listDialog.setSizePolicy(sizePolicy)
        listDialog.setAcceptDrops(False)
        self.verticalLayout_2 = QVBoxLayout(listDialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.label = QLabel(listDialog)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.listWidget = QListWidget(listDialog)
        self.listWidget.setObjectName(u"listWidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy1)

        self.verticalLayout.addWidget(self.listWidget)

        self.buttonBox = QDialogButtonBox(listDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy2)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)
        self.buttonBox.setCenterButtons(False)

        self.verticalLayout.addWidget(self.buttonBox)


        self.verticalLayout_2.addLayout(self.verticalLayout)


        self.retranslateUi(listDialog)
        self.buttonBox.accepted.connect(listDialog.accept)
        self.buttonBox.rejected.connect(listDialog.reject)

        QMetaObject.connectSlotsByName(listDialog)
    # setupUi

    def retranslateUi(self, listDialog):
        listDialog.setWindowTitle(QCoreApplication.translate("listDialog", u"Rule test results", None))
        self.label.setText(QCoreApplication.translate("listDialog", u"Affected files and folders:", None))
    # retranslateUi

