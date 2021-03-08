# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tags_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from tag_groups import TreeView

import DeClutter_rc

class Ui_tagsDialog(object):
    def setupUi(self, tagsDialog):
        if not tagsDialog.objectName():
            tagsDialog.setObjectName(u"tagsDialog")
        tagsDialog.setWindowModality(Qt.ApplicationModal)
        tagsDialog.resize(291, 486)
        icon = QIcon()
        icon.addFile(u":/images/DeClutter.ico", QSize(), QIcon.Normal, QIcon.Off)
        tagsDialog.setWindowIcon(icon)
        self.gridLayout = QGridLayout(tagsDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.buttonBox = QDialogButtonBox(tagsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)

        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.addButton = QPushButton(tagsDialog)
        self.addButton.setObjectName(u"addButton")
        icon1 = QIcon()
        icon1.addFile(u":/images/icons/tag.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.addButton.setIcon(icon1)

        self.horizontalLayout.addWidget(self.addButton)

        self.addGroupButton = QPushButton(tagsDialog)
        self.addGroupButton.setObjectName(u"addGroupButton")
        icon2 = QIcon()
        icon2.addFile(u":/images/icons/folder.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.addGroupButton.setIcon(icon2)

        self.horizontalLayout.addWidget(self.addGroupButton)

        self.removeButton = QPushButton(tagsDialog)
        self.removeButton.setObjectName(u"removeButton")
        icon3 = QIcon()
        icon3.addFile(u":/images/icons/trash.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.removeButton.setIcon(icon3)

        self.horizontalLayout.addWidget(self.removeButton)

        self.colorButton = QPushButton(tagsDialog)
        self.colorButton.setObjectName(u"colorButton")
        icon4 = QIcon()
        icon4.addFile(u":/images/icons/brush.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.colorButton.setIcon(icon4)

        self.horizontalLayout.addWidget(self.colorButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.treeView = TreeView(tagsDialog)
        self.treeView.setObjectName(u"treeView")

        self.verticalLayout.addWidget(self.treeView)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.retranslateUi(tagsDialog)
        self.buttonBox.rejected.connect(tagsDialog.reject)
        self.buttonBox.accepted.connect(tagsDialog.accept)

        QMetaObject.connectSlotsByName(tagsDialog)
    # setupUi

    def retranslateUi(self, tagsDialog):
        tagsDialog.setWindowTitle(QCoreApplication.translate("tagsDialog", u"Manage Tags", None))
#if QT_CONFIG(tooltip)
        self.addButton.setToolTip(QCoreApplication.translate("tagsDialog", u"Add Tag", None))
#endif // QT_CONFIG(tooltip)
        self.addButton.setText("")
#if QT_CONFIG(tooltip)
        self.addGroupButton.setToolTip(QCoreApplication.translate("tagsDialog", u"Add Group", None))
#endif // QT_CONFIG(tooltip)
        self.addGroupButton.setText("")
#if QT_CONFIG(tooltip)
        self.removeButton.setToolTip(QCoreApplication.translate("tagsDialog", u"Delete", None))
#endif // QT_CONFIG(tooltip)
        self.removeButton.setText("")
#if QT_CONFIG(tooltip)
        self.colorButton.setToolTip(QCoreApplication.translate("tagsDialog", u"Select Color", None))
#endif // QT_CONFIG(tooltip)
        self.colorButton.setText("")
    # retranslateUi

