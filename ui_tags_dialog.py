# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tags_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.0.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import DeClutter_rc

class Ui_tagsDialog(object):
    def setupUi(self, tagsDialog):
        if not tagsDialog.objectName():
            tagsDialog.setObjectName(u"tagsDialog")
        tagsDialog.setWindowModality(Qt.ApplicationModal)
        tagsDialog.resize(264, 300)
        self.gridLayout = QGridLayout(tagsDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.addButton = QPushButton(tagsDialog)
        self.addButton.setObjectName(u"addButton")
        icon = QIcon()
        icon.addFile(u":/images/icons/document-new.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.addButton.setIcon(icon)

        self.horizontalLayout.addWidget(self.addButton)

        self.removeButton = QPushButton(tagsDialog)
        self.removeButton.setObjectName(u"removeButton")
        icon1 = QIcon()
        icon1.addFile(u":/images/icons/trash.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.removeButton.setIcon(icon1)

        self.horizontalLayout.addWidget(self.removeButton)

        self.moveUpButton = QPushButton(tagsDialog)
        self.moveUpButton.setObjectName(u"moveUpButton")
        icon2 = QIcon()
        icon2.addFile(u":/images/icons/arrow-thin-up.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.moveUpButton.setIcon(icon2)

        self.horizontalLayout.addWidget(self.moveUpButton)

        self.moveDownButton = QPushButton(tagsDialog)
        self.moveDownButton.setObjectName(u"moveDownButton")
        icon3 = QIcon()
        icon3.addFile(u":/images/icons/arrow-thin-down.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.moveDownButton.setIcon(icon3)

        self.horizontalLayout.addWidget(self.moveDownButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.tagsList = QListWidget(tagsDialog)
        self.tagsList.setObjectName(u"tagsList")

        self.verticalLayout.addWidget(self.tagsList)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(tagsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)

        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)


        self.retranslateUi(tagsDialog)
        self.buttonBox.rejected.connect(tagsDialog.reject)
        self.buttonBox.accepted.connect(tagsDialog.accept)

        QMetaObject.connectSlotsByName(tagsDialog)
    # setupUi

    def retranslateUi(self, tagsDialog):
        tagsDialog.setWindowTitle(QCoreApplication.translate("tagsDialog", u"Manage Tags", None))
        self.addButton.setText("")
        self.removeButton.setText("")
        self.moveUpButton.setText("")
        self.moveDownButton.setText("")
    # retranslateUi

