# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tags_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGridLayout, QHBoxLayout, QHeaderView, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

from ..tag_tree import TagTree
from . import DeClutter_rc

class Ui_tagsDialog(object):
    def setupUi(self, tagsDialog):
        if not tagsDialog.objectName():
            tagsDialog.setObjectName(u"tagsDialog")
        tagsDialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        tagsDialog.resize(291, 486)
        icon = QIcon()
        icon.addFile(u":/images/icons/DeClutter.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        tagsDialog.setWindowIcon(icon)
        self.gridLayout = QGridLayout(tagsDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.buttonBox = QDialogButtonBox(tagsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setCenterButtons(False)

        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.addButton = QPushButton(tagsDialog)
        self.addButton.setObjectName(u"addButton")
        icon1 = QIcon()
        if QIcon.hasThemeIcon(QIcon.ThemeIcon.DocumentNew):
            icon1 = QIcon.fromTheme(QIcon.ThemeIcon.DocumentNew)
        else:
            icon1.addFile(u":/images/icons/tag.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.addButton.setIcon(icon1)

        self.horizontalLayout.addWidget(self.addButton)

        self.addGroupButton = QPushButton(tagsDialog)
        self.addGroupButton.setObjectName(u"addGroupButton")
        icon2 = QIcon()
        if QIcon.hasThemeIcon(QIcon.ThemeIcon.FolderNew):
            icon2 = QIcon.fromTheme(QIcon.ThemeIcon.FolderNew)
        else:
            icon2.addFile(u":/images/icons/folder.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.addGroupButton.setIcon(icon2)

        self.horizontalLayout.addWidget(self.addGroupButton)

        self.editButton = QPushButton(tagsDialog)
        self.editButton.setObjectName(u"editButton")
        icon3 = QIcon()
        if QIcon.hasThemeIcon(QIcon.ThemeIcon.DocumentProperties):
            icon3 = QIcon.fromTheme(QIcon.ThemeIcon.DocumentProperties)
        else:
            icon3.addFile(u":/images/icons/brush.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.editButton.setIcon(icon3)

        self.horizontalLayout.addWidget(self.editButton)

        self.removeButton = QPushButton(tagsDialog)
        self.removeButton.setObjectName(u"removeButton")
        icon4 = QIcon()
        if QIcon.hasThemeIcon(QIcon.ThemeIcon.EditDelete):
            icon4 = QIcon.fromTheme(QIcon.ThemeIcon.EditDelete)
        else:
            icon4.addFile(u":/images/icons/trash.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.removeButton.setIcon(icon4)

        self.horizontalLayout.addWidget(self.removeButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.treeView = TagTree(tagsDialog)
        self.treeView.setObjectName(u"treeView")

        self.verticalLayout.addWidget(self.treeView)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        QWidget.setTabOrder(self.addButton, self.addGroupButton)
        QWidget.setTabOrder(self.addGroupButton, self.removeButton)
        QWidget.setTabOrder(self.removeButton, self.treeView)

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
        self.editButton.setToolTip(QCoreApplication.translate("tagsDialog", u"Edit", None))
#endif // QT_CONFIG(tooltip)
        self.editButton.setText("")
#if QT_CONFIG(tooltip)
        self.removeButton.setToolTip(QCoreApplication.translate("tagsDialog", u"Delete", None))
#endif // QT_CONFIG(tooltip)
        self.removeButton.setText("")
    # retranslateUi

