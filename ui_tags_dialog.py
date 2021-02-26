# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tags_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.0.1
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
        icon = QIcon()
        icon.addFile(u":/images/DeClutter.ico", QSize(), QIcon.Normal, QIcon.Off)
        tagsDialog.setWindowIcon(icon)
        self.gridLayout = QGridLayout(tagsDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.addButton = QPushButton(tagsDialog)
        self.addButton.setObjectName(u"addButton")
        icon1 = QIcon()
        icon1.addFile(u":/images/icons/document-new.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.addButton.setIcon(icon1)

        self.horizontalLayout.addWidget(self.addButton)

        self.removeButton = QPushButton(tagsDialog)
        self.removeButton.setObjectName(u"removeButton")
        icon2 = QIcon()
        icon2.addFile(u":/images/icons/trash.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.removeButton.setIcon(icon2)

        self.horizontalLayout.addWidget(self.removeButton)

        self.moveUpButton = QPushButton(tagsDialog)
        self.moveUpButton.setObjectName(u"moveUpButton")
        icon3 = QIcon()
        icon3.addFile(u":/images/icons/arrow-thin-up.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.moveUpButton.setIcon(icon3)

        self.horizontalLayout.addWidget(self.moveUpButton)

        self.moveDownButton = QPushButton(tagsDialog)
        self.moveDownButton.setObjectName(u"moveDownButton")
        icon4 = QIcon()
        icon4.addFile(u":/images/icons/arrow-thin-down.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.moveDownButton.setIcon(icon4)

        self.horizontalLayout.addWidget(self.moveDownButton)

        self.colorButton = QPushButton(tagsDialog)
        self.colorButton.setObjectName(u"colorButton")
        icon5 = QIcon()
        icon5.addFile(u":/images/icons/brush.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.colorButton.setIcon(icon5)

        self.horizontalLayout.addWidget(self.colorButton)

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
        self.colorButton.setText("")
    # retranslateUi

