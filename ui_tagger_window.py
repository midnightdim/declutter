# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tagger_window.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import DeClutter_rc

class Ui_taggerWindow(object):
    def setupUi(self, taggerWindow):
        if not taggerWindow.objectName():
            taggerWindow.setObjectName(u"taggerWindow")
        taggerWindow.resize(1047, 690)
        icon = QIcon()
        icon.addFile(u":/images/DeClutter.ico", QSize(), QIcon.Normal, QIcon.Off)
        taggerWindow.setWindowIcon(icon)
        self.actionManage_Tags = QAction(taggerWindow)
        self.actionManage_Tags.setObjectName(u"actionManage_Tags")
        self.actionNone = QAction(taggerWindow)
        self.actionNone.setObjectName(u"actionNone")
        self.actionNone.setEnabled(False)
        self.centralwidget = QWidget(taggerWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.sourceComboBox = QComboBox(self.centralwidget)
        self.sourceComboBox.addItem("")
        self.sourceComboBox.addItem("")
        self.sourceComboBox.addItem("")
        self.sourceComboBox.setObjectName(u"sourceComboBox")

        self.horizontalLayout_3.addWidget(self.sourceComboBox)

        self.pathEdit = QLineEdit(self.centralwidget)
        self.pathEdit.setObjectName(u"pathEdit")

        self.horizontalLayout_3.addWidget(self.pathEdit)

        self.browseButton = QPushButton(self.centralwidget)
        self.browseButton.setObjectName(u"browseButton")

        self.horizontalLayout_3.addWidget(self.browseButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.selectTagsButton = QPushButton(self.centralwidget)
        self.selectTagsButton.setObjectName(u"selectTagsButton")

        self.horizontalLayout.addWidget(self.selectTagsButton)

        self.horizontalSpacer = QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.treeView = QTreeView(self.centralwidget)
        self.treeView.setObjectName(u"treeView")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeView.sizePolicy().hasHeightForWidth())
        self.treeView.setSizePolicy(sizePolicy)
        self.treeView.setRootIsDecorated(False)
        self.treeView.setItemsExpandable(False)
        self.treeView.setSortingEnabled(True)
        self.treeView.setExpandsOnDoubleClick(False)

        self.verticalLayout_2.addWidget(self.treeView)


        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 2)

        taggerWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(taggerWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1047, 21))
        self.menuOptions = QMenu(self.menubar)
        self.menuOptions.setObjectName(u"menuOptions")
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.recent_menu = QMenu(self.menuFile)
        self.recent_menu.setObjectName(u"recent_menu")
        self.recent_menu.setMaximumSize(QSize(600, 500))
        self.recent_menu.setTearOffEnabled(False)
        taggerWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(taggerWindow)
        self.statusbar.setObjectName(u"statusbar")
        taggerWindow.setStatusBar(self.statusbar)
        self.tagsDockWidget = QDockWidget(taggerWindow)
        self.tagsDockWidget.setObjectName(u"tagsDockWidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.tagsDockWidget.sizePolicy().hasHeightForWidth())
        self.tagsDockWidget.setSizePolicy(sizePolicy1)
        self.tagsDockWidget.setMinimumSize(QSize(180, 200))
        self.tagsDockWidget.setStyleSheet(u"")
        self.tagsDockWidget.setFeatures(QDockWidget.DockWidgetFloatable|QDockWidget.DockWidgetMovable)
        self.tagsDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        sizePolicy1.setHeightForWidth(self.dockWidgetContents.sizePolicy().hasHeightForWidth())
        self.dockWidgetContents.setSizePolicy(sizePolicy1)
        self.gridLayout_2 = QGridLayout(self.dockWidgetContents)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.tagsScrollArea = QScrollArea(self.dockWidgetContents)
        self.tagsScrollArea.setObjectName(u"tagsScrollArea")
        sizePolicy2 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.tagsScrollArea.sizePolicy().hasHeightForWidth())
        self.tagsScrollArea.setSizePolicy(sizePolicy2)
        self.tagsScrollArea.setFrameShape(QFrame.Box)
        self.tagsScrollArea.setFrameShadow(QFrame.Plain)
        self.tagsScrollArea.setLineWidth(0)
        self.tagsScrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 180, 351))
        sizePolicy1.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy1)
        self.gridLayout_3 = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.tagsLayout = QVBoxLayout()
        self.tagsLayout.setObjectName(u"tagsLayout")

        self.gridLayout_3.addLayout(self.tagsLayout, 0, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer, 1, 0, 1, 1)

        self.tagsScrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_2.addWidget(self.tagsScrollArea, 0, 0, 1, 1)

        self.tagsDockWidget.setWidget(self.dockWidgetContents)
        taggerWindow.addDockWidget(Qt.LeftDockWidgetArea, self.tagsDockWidget)
        self.mediaDockWidget = QDockWidget(taggerWindow)
        self.mediaDockWidget.setObjectName(u"mediaDockWidget")
        self.mediaDockWidgetContent = QWidget()
        self.mediaDockWidgetContent.setObjectName(u"mediaDockWidgetContent")
        self.mediaDockWidgetContent.setMinimumSize(QSize(0, 250))
        self.gridLayout_5 = QGridLayout(self.mediaDockWidgetContent)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.mediaPlayButton = QPushButton(self.mediaDockWidgetContent)
        self.mediaPlayButton.setObjectName(u"mediaPlayButton")
        icon1 = QIcon()
        icon1.addFile(u":/images/icons/media-play.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.mediaPlayButton.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.mediaPlayButton)

        self.mediaPositionSlider = QSlider(self.mediaDockWidgetContent)
        self.mediaPositionSlider.setObjectName(u"mediaPositionSlider")
        self.mediaPositionSlider.setOrientation(Qt.Horizontal)

        self.horizontalLayout_2.addWidget(self.mediaPositionSlider)

        self.mediaVolumeDial = QDial(self.mediaDockWidgetContent)
        self.mediaVolumeDial.setObjectName(u"mediaVolumeDial")
        self.mediaVolumeDial.setMaximumSize(QSize(30, 30))
        self.mediaVolumeDial.setMaximum(100)
        self.mediaVolumeDial.setValue(100)

        self.horizontalLayout_2.addWidget(self.mediaVolumeDial)


        self.gridLayout_4.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)

        self.playerLayout = QGridLayout()
        self.playerLayout.setObjectName(u"playerLayout")

        self.gridLayout_4.addLayout(self.playerLayout, 0, 0, 1, 1)

        self.gridLayout_4.setRowStretch(0, 30)
        self.gridLayout_4.setRowStretch(1, 1)
        self.gridLayout_4.setRowStretch(2, 1)

        self.gridLayout_5.addLayout(self.gridLayout_4, 0, 0, 1, 1)

        self.mediaDockWidget.setWidget(self.mediaDockWidgetContent)
        taggerWindow.addDockWidget(Qt.LeftDockWidgetArea, self.mediaDockWidget)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuOptions.menuAction())
        self.menuOptions.addAction(self.actionManage_Tags)
        self.menuFile.addAction(self.recent_menu.menuAction())
        self.recent_menu.addAction(self.actionNone)

        self.retranslateUi(taggerWindow)

        QMetaObject.connectSlotsByName(taggerWindow)
    # setupUi

    def retranslateUi(self, taggerWindow):
        taggerWindow.setWindowTitle(QCoreApplication.translate("taggerWindow", u"DeClutter (beta): Tagger", None))
        self.actionManage_Tags.setText(QCoreApplication.translate("taggerWindow", u"Manage Tags", None))
        self.actionNone.setText(QCoreApplication.translate("taggerWindow", u"None", None))
        self.sourceComboBox.setItemText(0, QCoreApplication.translate("taggerWindow", u"Folder", None))
        self.sourceComboBox.setItemText(1, QCoreApplication.translate("taggerWindow", u"Tag(s)", None))
        self.sourceComboBox.setItemText(2, QCoreApplication.translate("taggerWindow", u"Folder & tags", None))

        self.browseButton.setText(QCoreApplication.translate("taggerWindow", u"Browse...", None))
        self.selectTagsButton.setText(QCoreApplication.translate("taggerWindow", u"Select tags...", None))
        self.menuOptions.setTitle(QCoreApplication.translate("taggerWindow", u"Options", None))
        self.menuFile.setTitle(QCoreApplication.translate("taggerWindow", u"File", None))
        self.recent_menu.setTitle(QCoreApplication.translate("taggerWindow", u"Recent folders", None))
        self.tagsDockWidget.setWindowTitle(QCoreApplication.translate("taggerWindow", u"Tags", None))
#if QT_CONFIG(tooltip)
        self.mediaPlayButton.setToolTip(QCoreApplication.translate("taggerWindow", u"Play", None))
#endif // QT_CONFIG(tooltip)
        self.mediaPlayButton.setText("")
    # retranslateUi

