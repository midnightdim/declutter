# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'condition_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from tag_tree import TagTree

import DeClutter_rc

class Ui_Condition(object):
    def setupUi(self, Condition):
        if not Condition.objectName():
            Condition.setObjectName(u"Condition")
        Condition.setWindowModality(Qt.ApplicationModal)
        Condition.resize(417, 334)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Condition.sizePolicy().hasHeightForWidth())
        Condition.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u":/images/DeClutter.ico", QSize(), QIcon.Normal, QIcon.Off)
        Condition.setWindowIcon(icon)
        self.horizontalLayout = QHBoxLayout(Condition)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.label = QLabel(Condition)
        self.label.setObjectName(u"label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)

        self.horizontalLayout_4.addWidget(self.label)

        self.conditionCombo = QComboBox(Condition)
        self.conditionCombo.addItem("")
        self.conditionCombo.addItem("")
        self.conditionCombo.addItem("")
        self.conditionCombo.addItem("")
        self.conditionCombo.addItem("")
        self.conditionCombo.setObjectName(u"conditionCombo")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.conditionCombo.sizePolicy().hasHeightForWidth())
        self.conditionCombo.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.conditionCombo)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.nameLabel = QLabel(Condition)
        self.nameLabel.setObjectName(u"nameLabel")

        self.horizontalLayout_3.addWidget(self.nameLabel)

        self.nameCombo = QComboBox(Condition)
        self.nameCombo.addItem("")
        self.nameCombo.addItem("")
        self.nameCombo.setObjectName(u"nameCombo")

        self.horizontalLayout_3.addWidget(self.nameCombo)

        self.expressionLabel = QLabel(Condition)
        self.expressionLabel.setObjectName(u"expressionLabel")

        self.horizontalLayout_3.addWidget(self.expressionLabel)

        self.filemask = QLineEdit(Condition)
        self.filemask.setObjectName(u"filemask")

        self.horizontalLayout_3.addWidget(self.filemask)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.filenameHint = QLabel(Condition)
        self.filenameHint.setObjectName(u"filenameHint")

        self.verticalLayout.addWidget(self.filenameHint)

        self.ageLayout = QHBoxLayout()
        self.ageLayout.setObjectName(u"ageLayout")
        self.ageLabel = QLabel(Condition)
        self.ageLabel.setObjectName(u"ageLabel")

        self.ageLayout.addWidget(self.ageLabel)

        self.ageCombo = QComboBox(Condition)
        self.ageCombo.addItem("")
        self.ageCombo.addItem("")
        self.ageCombo.setObjectName(u"ageCombo")

        self.ageLayout.addWidget(self.ageCombo)

        self.age = QLineEdit(Condition)
        self.age.setObjectName(u"age")

        self.ageLayout.addWidget(self.age)

        self.ageUnitsCombo = QComboBox(Condition)
        self.ageUnitsCombo.addItem("")
        self.ageUnitsCombo.addItem("")
        self.ageUnitsCombo.addItem("")
        self.ageUnitsCombo.addItem("")
        self.ageUnitsCombo.setObjectName(u"ageUnitsCombo")

        self.ageLayout.addWidget(self.ageUnitsCombo)

        self.ageSpacer = QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.ageLayout.addItem(self.ageSpacer)


        self.verticalLayout.addLayout(self.ageLayout)

        self.sizeLayout = QHBoxLayout()
        self.sizeLayout.setObjectName(u"sizeLayout")
        self.sizeLabel = QLabel(Condition)
        self.sizeLabel.setObjectName(u"sizeLabel")

        self.sizeLayout.addWidget(self.sizeLabel)

        self.sizeCombo = QComboBox(Condition)
        self.sizeCombo.addItem("")
        self.sizeCombo.addItem("")
        self.sizeCombo.setObjectName(u"sizeCombo")

        self.sizeLayout.addWidget(self.sizeCombo)

        self.size = QLineEdit(Condition)
        self.size.setObjectName(u"size")

        self.sizeLayout.addWidget(self.size)

        self.sizeUnitsCombo = QComboBox(Condition)
        self.sizeUnitsCombo.addItem("")
        self.sizeUnitsCombo.addItem("")
        self.sizeUnitsCombo.addItem("")
        self.sizeUnitsCombo.addItem("")
        self.sizeUnitsCombo.addItem("")
        self.sizeUnitsCombo.setObjectName(u"sizeUnitsCombo")

        self.sizeLayout.addWidget(self.sizeUnitsCombo)

        self.horizontalSpacer_2 = QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.sizeLayout.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addLayout(self.sizeLayout)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.tagLabel = QLabel(Condition)
        self.tagLabel.setObjectName(u"tagLabel")

        self.horizontalLayout_7.addWidget(self.tagLabel)

        self.tagsCombo = QComboBox(Condition)
        self.tagsCombo.addItem("")
        self.tagsCombo.addItem("")
        self.tagsCombo.addItem("")
        self.tagsCombo.addItem("")
        self.tagsCombo.addItem("")
        self.tagsCombo.addItem("")
        self.tagsCombo.setObjectName(u"tagsCombo")

        self.horizontalLayout_7.addWidget(self.tagsCombo)

        self.tagLabel2 = QLabel(Condition)
        self.tagLabel2.setObjectName(u"tagLabel2")

        self.horizontalLayout_7.addWidget(self.tagLabel2)

        self.tagGroupsCombo = QComboBox(Condition)
        self.tagGroupsCombo.setObjectName(u"tagGroupsCombo")

        self.horizontalLayout_7.addWidget(self.tagGroupsCombo)

        self.horizontalSpacer_3 = QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_3)


        self.verticalLayout.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.tagsView = TagTree(Condition)
        self.tagsView.setObjectName(u"tagsView")
        self.tagsView.setStyleSheet(u"")

        self.horizontalLayout_8.addWidget(self.tagsView)

        self.horizontalSpacer_4 = QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_4)


        self.verticalLayout.addLayout(self.horizontalLayout_8)

        self.selectedTagsLabel = QLabel(Condition)
        self.selectedTagsLabel.setObjectName(u"selectedTagsLabel")

        self.verticalLayout.addWidget(self.selectedTagsLabel)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.typeLabel = QLabel(Condition)
        self.typeLabel.setObjectName(u"typeLabel")

        self.horizontalLayout_2.addWidget(self.typeLabel)

        self.typeSwitchCombo = QComboBox(Condition)
        self.typeSwitchCombo.addItem("")
        self.typeSwitchCombo.addItem("")
        self.typeSwitchCombo.setObjectName(u"typeSwitchCombo")
        self.typeSwitchCombo.setMaximumSize(QSize(50, 16777215))
        self.typeSwitchCombo.setBaseSize(QSize(0, 0))

        self.horizontalLayout_2.addWidget(self.typeSwitchCombo)

        self.typeCombo = QComboBox(Condition)
        self.typeCombo.setObjectName(u"typeCombo")

        self.horizontalLayout_2.addWidget(self.typeCombo)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_5)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.buttonBox = QDialogButtonBox(Condition)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)

        self.verticalLayout.setStretch(10, 2)

        self.horizontalLayout.addLayout(self.verticalLayout)


        self.retranslateUi(Condition)
        self.buttonBox.accepted.connect(Condition.accept)
        self.buttonBox.rejected.connect(Condition.reject)

        QMetaObject.connectSlotsByName(Condition)
    # setupUi

    def retranslateUi(self, Condition):
        Condition.setWindowTitle(QCoreApplication.translate("Condition", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Condition", u"Select files by", None))
        self.conditionCombo.setItemText(0, QCoreApplication.translate("Condition", u"name", None))
        self.conditionCombo.setItemText(1, QCoreApplication.translate("Condition", u"date", None))
        self.conditionCombo.setItemText(2, QCoreApplication.translate("Condition", u"size", None))
        self.conditionCombo.setItemText(3, QCoreApplication.translate("Condition", u"tags", None))
        self.conditionCombo.setItemText(4, QCoreApplication.translate("Condition", u"type", None))

        self.nameLabel.setText(QCoreApplication.translate("Condition", u"File name", None))
        self.nameCombo.setItemText(0, QCoreApplication.translate("Condition", u"matches", None))
        self.nameCombo.setItemText(1, QCoreApplication.translate("Condition", u"doesn't match", None))

        self.expressionLabel.setText(QCoreApplication.translate("Condition", u"expression", None))
        self.filemask.setText(QCoreApplication.translate("Condition", u"*", None))
        self.filenameHint.setText(QCoreApplication.translate("Condition", u"You can use multiple comma-separated expressions", None))
        self.ageLabel.setText(QCoreApplication.translate("Condition", u"File age", None))
        self.ageCombo.setItemText(0, QCoreApplication.translate("Condition", u">=", None))
        self.ageCombo.setItemText(1, QCoreApplication.translate("Condition", u"<", None))

        self.ageUnitsCombo.setItemText(0, QCoreApplication.translate("Condition", u"days", None))
        self.ageUnitsCombo.setItemText(1, QCoreApplication.translate("Condition", u"weeks", None))
        self.ageUnitsCombo.setItemText(2, QCoreApplication.translate("Condition", u"months", None))
        self.ageUnitsCombo.setItemText(3, QCoreApplication.translate("Condition", u"years", None))

        self.sizeLabel.setText(QCoreApplication.translate("Condition", u"File size is", None))
        self.sizeCombo.setItemText(0, QCoreApplication.translate("Condition", u">=", None))
        self.sizeCombo.setItemText(1, QCoreApplication.translate("Condition", u"<", None))

        self.sizeUnitsCombo.setItemText(0, QCoreApplication.translate("Condition", u"B", None))
        self.sizeUnitsCombo.setItemText(1, QCoreApplication.translate("Condition", u"KB", None))
        self.sizeUnitsCombo.setItemText(2, QCoreApplication.translate("Condition", u"MB", None))
        self.sizeUnitsCombo.setItemText(3, QCoreApplication.translate("Condition", u"GB", None))
        self.sizeUnitsCombo.setItemText(4, QCoreApplication.translate("Condition", u"TB", None))

        self.tagLabel.setText(QCoreApplication.translate("Condition", u"File has", None))
        self.tagsCombo.setItemText(0, QCoreApplication.translate("Condition", u"any", None))
        self.tagsCombo.setItemText(1, QCoreApplication.translate("Condition", u"all", None))
        self.tagsCombo.setItemText(2, QCoreApplication.translate("Condition", u"none", None))
        self.tagsCombo.setItemText(3, QCoreApplication.translate("Condition", u"no tags", None))
        self.tagsCombo.setItemText(4, QCoreApplication.translate("Condition", u"any tags", None))
        self.tagsCombo.setItemText(5, QCoreApplication.translate("Condition", u"tags in group", None))

        self.tagLabel2.setText(QCoreApplication.translate("Condition", u"of selected tags:", None))
        self.selectedTagsLabel.setText(QCoreApplication.translate("Condition", u"Selected tags:", None))
        self.typeLabel.setText(QCoreApplication.translate("Condition", u"File type ", None))
        self.typeSwitchCombo.setItemText(0, QCoreApplication.translate("Condition", u"is", None))
        self.typeSwitchCombo.setItemText(1, QCoreApplication.translate("Condition", u"is not", None))

    # retranslateUi

