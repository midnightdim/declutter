# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rule_edit_window.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from tag_tree import TagTree


class Ui_RuleEditWindow(object):
    def setupUi(self, RuleEditWindow):
        if not RuleEditWindow.objectName():
            RuleEditWindow.setObjectName(u"RuleEditWindow")
        RuleEditWindow.setWindowModality(Qt.ApplicationModal)
        RuleEditWindow.resize(694, 571)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(RuleEditWindow.sizePolicy().hasHeightForWidth())
        RuleEditWindow.setSizePolicy(sizePolicy)
        self.gridLayout_2 = QGridLayout(RuleEditWindow)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.keepTagsCheckBox = QCheckBox(RuleEditWindow)
        self.keepTagsCheckBox.setObjectName(u"keepTagsCheckBox")

        self.horizontalLayout_6.addWidget(self.keepTagsCheckBox)

        self.keepFolderStructureCheckBox = QCheckBox(RuleEditWindow)
        self.keepFolderStructureCheckBox.setObjectName(u"keepFolderStructureCheckBox")

        self.horizontalLayout_6.addWidget(self.keepFolderStructureCheckBox)

        self.horizontalLayout_6.setStretch(0, 1)
        self.horizontalLayout_6.setStretch(1, 5)

        self.gridLayout.addLayout(self.horizontalLayout_6, 7, 0, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.folderBrowseButton = QPushButton(RuleEditWindow)
        self.folderBrowseButton.setObjectName(u"folderBrowseButton")

        self.horizontalLayout_5.addWidget(self.folderBrowseButton)


        self.gridLayout.addLayout(self.horizontalLayout_5, 6, 1, 1, 1)

        self.formLayout_5 = QFormLayout()
        self.formLayout_5.setObjectName(u"formLayout_5")
        self.label_3 = QLabel(RuleEditWindow)
        self.label_3.setObjectName(u"label_3")

        self.formLayout_5.setWidget(0, QFormLayout.LabelRole, self.label_3)

        self.formLayout_6 = QFormLayout()
        self.formLayout_6.setObjectName(u"formLayout_6")
        self.conditionSwitchComboBox = QComboBox(RuleEditWindow)
        self.conditionSwitchComboBox.addItem("")
        self.conditionSwitchComboBox.addItem("")
        self.conditionSwitchComboBox.addItem("")
        self.conditionSwitchComboBox.setObjectName(u"conditionSwitchComboBox")

        self.formLayout_6.setWidget(0, QFormLayout.LabelRole, self.conditionSwitchComboBox)

        self.label_4 = QLabel(RuleEditWindow)
        self.label_4.setObjectName(u"label_4")

        self.formLayout_6.setWidget(0, QFormLayout.FieldRole, self.label_4)


        self.formLayout_5.setLayout(0, QFormLayout.FieldRole, self.formLayout_6)


        self.gridLayout.addLayout(self.formLayout_5, 3, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.actionComboBox = QComboBox(RuleEditWindow)
        self.actionComboBox.addItem("")
        self.actionComboBox.addItem("")
        self.actionComboBox.addItem("")
        self.actionComboBox.addItem("")
        self.actionComboBox.addItem("")
        self.actionComboBox.addItem("")
        self.actionComboBox.addItem("")
        self.actionComboBox.addItem("")
        self.actionComboBox.addItem("")
        self.actionComboBox.setObjectName(u"actionComboBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.actionComboBox.sizePolicy().hasHeightForWidth())
        self.actionComboBox.setSizePolicy(sizePolicy1)
        self.actionComboBox.setMinimumSize(QSize(0, 0))
        self.actionComboBox.setMaximumSize(QSize(120, 20))
        self.actionComboBox.setBaseSize(QSize(110, 0))
        self.actionComboBox.setEditable(False)
        self.actionComboBox.setDuplicatesEnabled(False)

        self.horizontalLayout_2.addWidget(self.actionComboBox)

        self.toFolderLabel = QLabel(RuleEditWindow)
        self.toFolderLabel.setObjectName(u"toFolderLabel")

        self.horizontalLayout_2.addWidget(self.toFolderLabel)

        self.targetFolderEdit = QLineEdit(RuleEditWindow)
        self.targetFolderEdit.setObjectName(u"targetFolderEdit")
        sizePolicy2 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.targetFolderEdit.sizePolicy().hasHeightForWidth())
        self.targetFolderEdit.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.targetFolderEdit)

        self.subfolderEdit = QLineEdit(RuleEditWindow)
        self.subfolderEdit.setObjectName(u"subfolderEdit")
        sizePolicy2.setHeightForWidth(self.subfolderEdit.sizePolicy().hasHeightForWidth())
        self.subfolderEdit.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.subfolderEdit)

        self.renameEdit = QLineEdit(RuleEditWindow)
        self.renameEdit.setObjectName(u"renameEdit")
        self.renameEdit.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.renameEdit.sizePolicy().hasHeightForWidth())
        self.renameEdit.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.renameEdit)

        self.horizontalSpacer_2 = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 1)
        self.horizontalLayout_2.setStretch(2, 5)
        self.horizontalLayout_2.setStretch(3, 5)
        self.horizontalLayout_2.setStretch(4, 5)

        self.gridLayout.addLayout(self.horizontalLayout_2, 6, 0, 1, 1)

        self.conditionListWidget = QListWidget(RuleEditWindow)
        self.conditionListWidget.setObjectName(u"conditionListWidget")

        self.gridLayout.addWidget(self.conditionListWidget, 4, 0, 1, 1)

        self.formLayout_7 = QFormLayout()
        self.formLayout_7.setObjectName(u"formLayout_7")
        self.conditionAddButton = QPushButton(RuleEditWindow)
        self.conditionAddButton.setObjectName(u"conditionAddButton")

        self.formLayout_7.setWidget(0, QFormLayout.LabelRole, self.conditionAddButton)

        self.conditionRemoveButton = QPushButton(RuleEditWindow)
        self.conditionRemoveButton.setObjectName(u"conditionRemoveButton")

        self.formLayout_7.setWidget(1, QFormLayout.LabelRole, self.conditionRemoveButton)

        self.conditionSaveButton = QPushButton(RuleEditWindow)
        self.conditionSaveButton.setObjectName(u"conditionSaveButton")

        self.formLayout_7.setWidget(2, QFormLayout.LabelRole, self.conditionSaveButton)

        self.conditionLoadButton = QPushButton(RuleEditWindow)
        self.conditionLoadButton.setObjectName(u"conditionLoadButton")

        self.formLayout_7.setWidget(3, QFormLayout.LabelRole, self.conditionLoadButton)


        self.gridLayout.addLayout(self.formLayout_7, 4, 1, 1, 1)

        self.label_5 = QLabel(RuleEditWindow)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 5, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(RuleEditWindow)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.ruleNameEdit = QLineEdit(RuleEditWindow)
        self.ruleNameEdit.setObjectName(u"ruleNameEdit")

        self.horizontalLayout.addWidget(self.ruleNameEdit)

        self.enabledCheckBox = QCheckBox(RuleEditWindow)
        self.enabledCheckBox.setObjectName(u"enabledCheckBox")

        self.horizontalLayout.addWidget(self.enabledCheckBox)

        self.recursiveCheckBox = QCheckBox(RuleEditWindow)
        self.recursiveCheckBox.setObjectName(u"recursiveCheckBox")

        self.horizontalLayout.addWidget(self.recursiveCheckBox)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 2)

        self.sourceListWidget = QListWidget(RuleEditWindow)
        self.sourceListWidget.setObjectName(u"sourceListWidget")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy3.setHorizontalStretch(200)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.sourceListWidget.sizePolicy().hasHeightForWidth())
        self.sourceListWidget.setSizePolicy(sizePolicy3)

        self.gridLayout.addWidget(self.sourceListWidget, 2, 0, 1, 1)

        self.tagsView = TagTree(RuleEditWindow)
        self.tagsView.setObjectName(u"tagsView")
        sizePolicy4 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.tagsView.sizePolicy().hasHeightForWidth())
        self.tagsView.setSizePolicy(sizePolicy4)

        self.gridLayout.addWidget(self.tagsView, 11, 0, 1, 1)

        self.formLayout_3 = QFormLayout()
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.folderAddButton = QPushButton(RuleEditWindow)
        self.folderAddButton.setObjectName(u"folderAddButton")

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.folderAddButton)

        self.sourceRemoveButton = QPushButton(RuleEditWindow)
        self.sourceRemoveButton.setObjectName(u"sourceRemoveButton")

        self.formLayout_3.setWidget(2, QFormLayout.LabelRole, self.sourceRemoveButton)

        self.allTaggedAddButton = QPushButton(RuleEditWindow)
        self.allTaggedAddButton.setObjectName(u"allTaggedAddButton")

        self.formLayout_3.setWidget(1, QFormLayout.LabelRole, self.allTaggedAddButton)


        self.gridLayout.addLayout(self.formLayout_3, 2, 1, 1, 1)

        self.label_2 = QLabel(RuleEditWindow)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.fileWithSameNameLabel = QLabel(RuleEditWindow)
        self.fileWithSameNameLabel.setObjectName(u"fileWithSameNameLabel")

        self.horizontalLayout_7.addWidget(self.fileWithSameNameLabel)

        self.overwriteComboBox = QComboBox(RuleEditWindow)
        self.overwriteComboBox.addItem("")
        self.overwriteComboBox.addItem("")
        self.overwriteComboBox.setObjectName(u"overwriteComboBox")

        self.horizontalLayout_7.addWidget(self.overwriteComboBox)

        self.horizontalSpacer_4 = QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_4)


        self.gridLayout.addLayout(self.horizontalLayout_7, 10, 0, 1, 1)

        self.selectedTagsLabel = QLabel(RuleEditWindow)
        self.selectedTagsLabel.setObjectName(u"selectedTagsLabel")

        self.gridLayout.addWidget(self.selectedTagsLabel, 12, 0, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 1, 0, 1, 1)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer)

        self.advancedButton = QPushButton(RuleEditWindow)
        self.advancedButton.setObjectName(u"advancedButton")

        self.horizontalLayout_8.addWidget(self.advancedButton)

        self.testButton = QPushButton(RuleEditWindow)
        self.testButton.setObjectName(u"testButton")

        self.horizontalLayout_8.addWidget(self.testButton)

        self.buttonBox = QDialogButtonBox(RuleEditWindow)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)

        self.horizontalLayout_8.addWidget(self.buttonBox)


        self.gridLayout_2.addLayout(self.horizontalLayout_8, 6, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 5, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.ignoreNewestCheckBox = QCheckBox(RuleEditWindow)
        self.ignoreNewestCheckBox.setObjectName(u"ignoreNewestCheckBox")

        self.horizontalLayout_3.addWidget(self.ignoreNewestCheckBox)

        self.numberNewestEdit = QLineEdit(RuleEditWindow)
        self.numberNewestEdit.setObjectName(u"numberNewestEdit")
        self.numberNewestEdit.setMaximumSize(QSize(40, 16777215))

        self.horizontalLayout_3.addWidget(self.numberNewestEdit)

        self.newestLabel = QLabel(RuleEditWindow)
        self.newestLabel.setObjectName(u"newestLabel")

        self.horizontalLayout_3.addWidget(self.newestLabel)

        self.horizontalSpacer_3 = QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)


        self.gridLayout_2.addLayout(self.horizontalLayout_3, 3, 0, 1, 1)

        self.line = QFrame(RuleEditWindow)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout_2.addWidget(self.line, 2, 0, 1, 1)


        self.retranslateUi(RuleEditWindow)

        QMetaObject.connectSlotsByName(RuleEditWindow)
    # setupUi

    def retranslateUi(self, RuleEditWindow):
        RuleEditWindow.setWindowTitle(QCoreApplication.translate("RuleEditWindow", u"Add/Edit Rule", None))
        self.keepTagsCheckBox.setText(QCoreApplication.translate("RuleEditWindow", u"keep tags", None))
        self.keepFolderStructureCheckBox.setText(QCoreApplication.translate("RuleEditWindow", u"keep folder structure", None))
        self.folderBrowseButton.setText(QCoreApplication.translate("RuleEditWindow", u"Browse...", None))
        self.label_3.setText(QCoreApplication.translate("RuleEditWindow", u"If", None))
        self.conditionSwitchComboBox.setItemText(0, QCoreApplication.translate("RuleEditWindow", u"any", None))
        self.conditionSwitchComboBox.setItemText(1, QCoreApplication.translate("RuleEditWindow", u"all", None))
        self.conditionSwitchComboBox.setItemText(2, QCoreApplication.translate("RuleEditWindow", u"none", None))

        self.label_4.setText(QCoreApplication.translate("RuleEditWindow", u"of the conditions apply:", None))
        self.actionComboBox.setItemText(0, QCoreApplication.translate("RuleEditWindow", u"Move", None))
        self.actionComboBox.setItemText(1, QCoreApplication.translate("RuleEditWindow", u"Delete", None))
        self.actionComboBox.setItemText(2, QCoreApplication.translate("RuleEditWindow", u"Send to Trash", None))
        self.actionComboBox.setItemText(3, QCoreApplication.translate("RuleEditWindow", u"Rename", None))
        self.actionComboBox.setItemText(4, QCoreApplication.translate("RuleEditWindow", u"Copy", None))
        self.actionComboBox.setItemText(5, QCoreApplication.translate("RuleEditWindow", u"Tag", None))
        self.actionComboBox.setItemText(6, QCoreApplication.translate("RuleEditWindow", u"Remove tags", None))
        self.actionComboBox.setItemText(7, QCoreApplication.translate("RuleEditWindow", u"Clear all tags", None))
        self.actionComboBox.setItemText(8, QCoreApplication.translate("RuleEditWindow", u"Move to subfolder", None))

        self.toFolderLabel.setText(QCoreApplication.translate("RuleEditWindow", u"to folder", None))
#if QT_CONFIG(tooltip)
        self.targetFolderEdit.setToolTip(QCoreApplication.translate("RuleEditWindow", u"<html><head/><body><p>You can use the following tokens:</p><p>&lt;type&gt; will be replaced with file type</p><p>&lt;group:MyGroup&gt; will be replaced with the (first) tag of the file in MyGroup or 'None' if the file doesn't have tags from MyGroup</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.subfolderEdit.setToolTip(QCoreApplication.translate("RuleEditWindow", u"<html><head/><body><p>You can use the following tokens:</p><p>&lt;type&gt; will be replaced with file type</p><p>&lt;group:MyGroup&gt; will be replaced with the (first) tag of the file in MyGroup or 'None' if the file doesn't have tags from MyGroup</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.renameEdit.setToolTip(QCoreApplication.translate("RuleEditWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; line-height:19px;\">You can use the following tokens:</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; line-height:19px;\">&lt;filename&gt; will be replaced with file/folder name</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; line-height:19px;\">&lt;folder&gt; will be replaced with the parent folder name</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-i"
                        "ndent:0; text-indent:0px; line-height:19px;\">&lt;replace:ABC:XYZ&gt; will replace ABC with XYZ in file/folder name</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.renameEdit.setText(QCoreApplication.translate("RuleEditWindow", u"<filename>", None))
        self.conditionAddButton.setText(QCoreApplication.translate("RuleEditWindow", u"Add", None))
        self.conditionRemoveButton.setText(QCoreApplication.translate("RuleEditWindow", u"Remove", None))
        self.conditionSaveButton.setText(QCoreApplication.translate("RuleEditWindow", u"Save", None))
        self.conditionLoadButton.setText(QCoreApplication.translate("RuleEditWindow", u"Load", None))
        self.label_5.setText(QCoreApplication.translate("RuleEditWindow", u"Do the following:", None))
        self.label.setText(QCoreApplication.translate("RuleEditWindow", u"Rule name", None))
        self.enabledCheckBox.setText(QCoreApplication.translate("RuleEditWindow", u"Enabled", None))
        self.recursiveCheckBox.setText(QCoreApplication.translate("RuleEditWindow", u"Recursive", None))
        self.folderAddButton.setText(QCoreApplication.translate("RuleEditWindow", u"Add Folder", None))
        self.sourceRemoveButton.setText(QCoreApplication.translate("RuleEditWindow", u"Remove", None))
        self.allTaggedAddButton.setText(QCoreApplication.translate("RuleEditWindow", u"All tagged", None))
        self.label_2.setText(QCoreApplication.translate("RuleEditWindow", u"Sources to process", None))
        self.fileWithSameNameLabel.setText(QCoreApplication.translate("RuleEditWindow", u"If file with same name and different size exists:", None))
        self.overwriteComboBox.setItemText(0, QCoreApplication.translate("RuleEditWindow", u"increment name", None))
        self.overwriteComboBox.setItemText(1, QCoreApplication.translate("RuleEditWindow", u"overwrite", None))

        self.selectedTagsLabel.setText(QCoreApplication.translate("RuleEditWindow", u"Selected tags:", None))
        self.advancedButton.setText(QCoreApplication.translate("RuleEditWindow", u"Advanced...", None))
        self.testButton.setText(QCoreApplication.translate("RuleEditWindow", u"Test", None))
        self.ignoreNewestCheckBox.setText(QCoreApplication.translate("RuleEditWindow", u"Ignore", None))
        self.newestLabel.setText(QCoreApplication.translate("RuleEditWindow", u"newest file(s) in every folder", None))
    # retranslateUi

