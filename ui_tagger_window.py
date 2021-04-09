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

from slider import Slider
from file_tree import FileTree

import DeClutter_rc

class Ui_taggerWindow(object):
    def setupUi(self, taggerWindow):
        if not taggerWindow.objectName():
            taggerWindow.setObjectName(u"taggerWindow")
        taggerWindow.resize(1269, 817)
        icon = QIcon()
        icon.addFile(u":/images/DeClutter.ico", QSize(), QIcon.Normal, QIcon.Off)
        taggerWindow.setWindowIcon(icon)
        self.actionManage_Tags = QAction(taggerWindow)
        self.actionManage_Tags.setObjectName(u"actionManage_Tags")
        self.actionNone = QAction(taggerWindow)
        self.actionNone.setObjectName(u"actionNone")
        self.actionNone.setEnabled(False)
        self.actionNew_tagger_window = QAction(taggerWindow)
        self.actionNew_tagger_window.setObjectName(u"actionNew_tagger_window")
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
        self.sourceComboBox.setObjectName(u"sourceComboBox")

        self.horizontalLayout_3.addWidget(self.sourceComboBox)

        self.pathEdit = QLineEdit(self.centralwidget)
        self.pathEdit.setObjectName(u"pathEdit")

        self.horizontalLayout_3.addWidget(self.pathEdit)

        self.browseButton = QPushButton(self.centralwidget)
        self.browseButton.setObjectName(u"browseButton")

        self.horizontalLayout_3.addWidget(self.browseButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.treeView = FileTree(self.centralwidget)
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
        self.menubar.setGeometry(QRect(0, 0, 1269, 21))
        self.menuOptions = QMenu(self.menubar)
        self.menuOptions.setObjectName(u"menuOptions")
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.recent_menu = QMenu(self.menuFile)
        self.recent_menu.setObjectName(u"recent_menu")
        self.recent_menu.setMaximumSize(QSize(600, 500))
        self.recent_menu.setTearOffEnabled(False)
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName(u"menuView")
        taggerWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(taggerWindow)
        self.statusbar.setObjectName(u"statusbar")
        taggerWindow.setStatusBar(self.statusbar)
        self.tagsDockWidget = QDockWidget(taggerWindow)
        self.tagsDockWidget.setObjectName(u"tagsDockWidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.tagsDockWidget.sizePolicy().hasHeightForWidth())
        self.tagsDockWidget.setSizePolicy(sizePolicy1)
        self.tagsDockWidget.setMinimumSize(QSize(180, 500))
        self.tagsDockWidget.setStyleSheet(u"")
        self.tagsDockWidget.setFeatures(QDockWidget.AllDockWidgetFeatures)
        self.tagsDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        sizePolicy2 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.dockWidgetContents.sizePolicy().hasHeightForWidth())
        self.dockWidgetContents.setSizePolicy(sizePolicy2)
        self.gridLayout_2 = QGridLayout(self.dockWidgetContents)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.tagsScrollArea = QScrollArea(self.dockWidgetContents)
        self.tagsScrollArea.setObjectName(u"tagsScrollArea")
        sizePolicy3 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.tagsScrollArea.sizePolicy().hasHeightForWidth())
        self.tagsScrollArea.setSizePolicy(sizePolicy3)
        self.tagsScrollArea.setFrameShape(QFrame.Box)
        self.tagsScrollArea.setFrameShadow(QFrame.Plain)
        self.tagsScrollArea.setLineWidth(0)
        self.tagsScrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 180, 478))
        sizePolicy2.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy2)
        self.gridLayout_3 = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.tagsLayout = QVBoxLayout()
        self.tagsLayout.setSpacing(4)
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

        self.mediaPositionSlider = Slider(self.mediaDockWidgetContent)
        self.mediaPositionSlider.setObjectName(u"mediaPositionSlider")
        self.mediaPositionSlider.setOrientation(Qt.Horizontal)

        self.horizontalLayout_2.addWidget(self.mediaPositionSlider)

        self.mediaVolumeDial = QDial(self.mediaDockWidgetContent)
        self.mediaVolumeDial.setObjectName(u"mediaVolumeDial")
        self.mediaVolumeDial.setMaximumSize(QSize(30, 30))
        self.mediaVolumeDial.setMaximum(100)
        self.mediaVolumeDial.setValue(100)
        self.mediaVolumeDial.setWrapping(False)
        self.mediaVolumeDial.setNotchTarget(10.000000000000000)
        self.mediaVolumeDial.setNotchesVisible(True)

        self.horizontalLayout_2.addWidget(self.mediaVolumeDial)


        self.gridLayout_4.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)

        self.playerLayout = QGridLayout()
        self.playerLayout.setObjectName(u"playerLayout")

        self.gridLayout_4.addLayout(self.playerLayout, 0, 0, 1, 1)

        self.mediaDurationLabel = QLabel(self.mediaDockWidgetContent)
        self.mediaDurationLabel.setObjectName(u"mediaDurationLabel")
        self.mediaDurationLabel.setAlignment(Qt.AlignCenter)

        self.gridLayout_4.addWidget(self.mediaDurationLabel, 2, 0, 1, 1)

        self.gridLayout_4.setRowStretch(0, 30)
        self.gridLayout_4.setRowStretch(1, 1)
        self.gridLayout_4.setRowStretch(2, 1)

        self.gridLayout_5.addLayout(self.gridLayout_4, 0, 0, 1, 1)

        self.mediaDockWidget.setWidget(self.mediaDockWidgetContent)
        taggerWindow.addDockWidget(Qt.LeftDockWidgetArea, self.mediaDockWidget)
        self.tagsFilterDockWidget = QDockWidget(taggerWindow)
        self.tagsFilterDockWidget.setObjectName(u"tagsFilterDockWidget")
        sizePolicy1.setHeightForWidth(self.tagsFilterDockWidget.sizePolicy().hasHeightForWidth())
        self.tagsFilterDockWidget.setSizePolicy(sizePolicy1)
        self.tagsFilterDockWidget.setMinimumSize(QSize(180, 500))
        self.tagsFilterDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName(u"dockWidgetContents_2")
        self.gridLayout_7 = QGridLayout(self.dockWidgetContents_2)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_7.addItem(self.verticalSpacer_2, 2, 0, 1, 1)

        self.tagsFilterLayout = QGridLayout()
        self.tagsFilterLayout.setSpacing(4)
        self.tagsFilterLayout.setObjectName(u"tagsFilterLayout")

        self.gridLayout_7.addLayout(self.tagsFilterLayout, 1, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.tagsFilterCombo = QComboBox(self.dockWidgetContents_2)
        self.tagsFilterCombo.addItem("")
        self.tagsFilterCombo.addItem("")
        self.tagsFilterCombo.addItem("")
        self.tagsFilterCombo.addItem("")
        self.tagsFilterCombo.addItem("")
        self.tagsFilterCombo.addItem("")
        self.tagsFilterCombo.setObjectName(u"tagsFilterCombo")

        self.horizontalLayout_4.addWidget(self.tagsFilterCombo)

        self.tagsFilterLabel = QLabel(self.dockWidgetContents_2)
        self.tagsFilterLabel.setObjectName(u"tagsFilterLabel")
        sizePolicy4 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.tagsFilterLabel.sizePolicy().hasHeightForWidth())
        self.tagsFilterLabel.setSizePolicy(sizePolicy4)

        self.horizontalLayout_4.addWidget(self.tagsFilterLabel)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_7)


        self.gridLayout_7.addLayout(self.horizontalLayout_4, 0, 0, 1, 1)

        self.tagsFilterDockWidget.setWidget(self.dockWidgetContents_2)
        taggerWindow.addDockWidget(Qt.RightDockWidgetArea, self.tagsFilterDockWidget)
        self.otherFiltersDockWidget = QDockWidget(taggerWindow)
        self.otherFiltersDockWidget.setObjectName(u"otherFiltersDockWidget")
        sizePolicy2.setHeightForWidth(self.otherFiltersDockWidget.sizePolicy().hasHeightForWidth())
        self.otherFiltersDockWidget.setSizePolicy(sizePolicy2)
        self.otherFiltersDockWidget.setMinimumSize(QSize(216, 150))
        self.otherFiltersDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)
        self.dockWidgetContents_3 = QWidget()
        self.dockWidgetContents_3.setObjectName(u"dockWidgetContents_3")
        self.verticalLayout = QVBoxLayout(self.dockWidgetContents_3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.nameLabel = QLabel(self.dockWidgetContents_3)
        self.nameLabel.setObjectName(u"nameLabel")
        sizePolicy5 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.nameLabel.sizePolicy().hasHeightForWidth())
        self.nameLabel.setSizePolicy(sizePolicy5)

        self.horizontalLayout_6.addWidget(self.nameLabel)

        self.nameCombo = QComboBox(self.dockWidgetContents_3)
        self.nameCombo.addItem("")
        self.nameCombo.addItem("")
        self.nameCombo.setObjectName(u"nameCombo")
        sizePolicy6 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.nameCombo.sizePolicy().hasHeightForWidth())
        self.nameCombo.setSizePolicy(sizePolicy6)
        self.nameCombo.setMinimumSize(QSize(42, 0))
        self.nameCombo.setMaximumSize(QSize(42, 16777215))

        self.horizontalLayout_6.addWidget(self.nameCombo)

        self.filemask = QLineEdit(self.dockWidgetContents_3)
        self.filemask.setObjectName(u"filemask")
        sizePolicy6.setHeightForWidth(self.filemask.sizePolicy().hasHeightForWidth())
        self.filemask.setSizePolicy(sizePolicy6)
        self.filemask.setMinimumSize(QSize(60, 0))

        self.horizontalLayout_6.addWidget(self.filemask)


        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.ageLayout = QHBoxLayout()
        self.ageLayout.setObjectName(u"ageLayout")
        self.ageLabel = QLabel(self.dockWidgetContents_3)
        self.ageLabel.setObjectName(u"ageLabel")

        self.ageLayout.addWidget(self.ageLabel)

        self.ageCombo = QComboBox(self.dockWidgetContents_3)
        self.ageCombo.addItem("")
        self.ageCombo.addItem("")
        self.ageCombo.setObjectName(u"ageCombo")
        self.ageCombo.setMinimumSize(QSize(40, 0))
        self.ageCombo.setMaximumSize(QSize(40, 16777215))

        self.ageLayout.addWidget(self.ageCombo)

        self.age = QLineEdit(self.dockWidgetContents_3)
        self.age.setObjectName(u"age")
        sizePolicy6.setHeightForWidth(self.age.sizePolicy().hasHeightForWidth())
        self.age.setSizePolicy(sizePolicy6)
        self.age.setMinimumSize(QSize(45, 0))
        self.age.setMaxLength(8)

        self.ageLayout.addWidget(self.age)

        self.ageUnitsCombo = QComboBox(self.dockWidgetContents_3)
        self.ageUnitsCombo.addItem("")
        self.ageUnitsCombo.addItem("")
        self.ageUnitsCombo.addItem("")
        self.ageUnitsCombo.addItem("")
        self.ageUnitsCombo.setObjectName(u"ageUnitsCombo")
        self.ageUnitsCombo.setMinimumSize(QSize(60, 0))

        self.ageLayout.addWidget(self.ageUnitsCombo)


        self.verticalLayout.addLayout(self.ageLayout)

        self.sizeLayout = QHBoxLayout()
        self.sizeLayout.setObjectName(u"sizeLayout")
        self.sizeLabel = QLabel(self.dockWidgetContents_3)
        self.sizeLabel.setObjectName(u"sizeLabel")

        self.sizeLayout.addWidget(self.sizeLabel)

        self.sizeCombo = QComboBox(self.dockWidgetContents_3)
        self.sizeCombo.addItem("")
        self.sizeCombo.addItem("")
        self.sizeCombo.setObjectName(u"sizeCombo")
        self.sizeCombo.setMinimumSize(QSize(40, 0))
        self.sizeCombo.setMaximumSize(QSize(40, 16777215))

        self.sizeLayout.addWidget(self.sizeCombo)

        self.size = QLineEdit(self.dockWidgetContents_3)
        self.size.setObjectName(u"size")
        sizePolicy6.setHeightForWidth(self.size.sizePolicy().hasHeightForWidth())
        self.size.setSizePolicy(sizePolicy6)
        self.size.setMinimumSize(QSize(45, 0))
        self.size.setMaxLength(10)

        self.sizeLayout.addWidget(self.size)

        self.sizeUnitsCombo = QComboBox(self.dockWidgetContents_3)
        self.sizeUnitsCombo.addItem("")
        self.sizeUnitsCombo.addItem("")
        self.sizeUnitsCombo.addItem("")
        self.sizeUnitsCombo.addItem("")
        self.sizeUnitsCombo.addItem("")
        self.sizeUnitsCombo.setObjectName(u"sizeUnitsCombo")
        self.sizeUnitsCombo.setMinimumSize(QSize(40, 0))

        self.sizeLayout.addWidget(self.sizeUnitsCombo)


        self.verticalLayout.addLayout(self.sizeLayout)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.typeLabel = QLabel(self.dockWidgetContents_3)
        self.typeLabel.setObjectName(u"typeLabel")

        self.horizontalLayout_9.addWidget(self.typeLabel)

        self.typeSwitchCombo = QComboBox(self.dockWidgetContents_3)
        self.typeSwitchCombo.addItem("")
        self.typeSwitchCombo.addItem("")
        self.typeSwitchCombo.setObjectName(u"typeSwitchCombo")
        self.typeSwitchCombo.setMinimumSize(QSize(42, 0))
        self.typeSwitchCombo.setMaximumSize(QSize(42, 16777215))
        self.typeSwitchCombo.setBaseSize(QSize(0, 0))

        self.horizontalLayout_9.addWidget(self.typeSwitchCombo)

        self.typeCombo = QComboBox(self.dockWidgetContents_3)
        self.typeCombo.setObjectName(u"typeCombo")
        sizePolicy6.setHeightForWidth(self.typeCombo.sizePolicy().hasHeightForWidth())
        self.typeCombo.setSizePolicy(sizePolicy6)

        self.horizontalLayout_9.addWidget(self.typeCombo)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_6)


        self.verticalLayout.addLayout(self.horizontalLayout_9)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Preferred)

        self.verticalLayout.addItem(self.verticalSpacer_3)

        self.otherFiltersDockWidget.setWidget(self.dockWidgetContents_3)
        taggerWindow.addDockWidget(Qt.RightDockWidgetArea, self.otherFiltersDockWidget)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuOptions.menuAction())
        self.menuOptions.addAction(self.actionManage_Tags)
        self.menuFile.addAction(self.actionNew_tagger_window)
        self.menuFile.addAction(self.recent_menu.menuAction())
        self.menuFile.addSeparator()
        self.recent_menu.addAction(self.actionNone)

        self.retranslateUi(taggerWindow)
        self.mediaPositionSlider.sliderMoved.connect(taggerWindow.seek_position)

        QMetaObject.connectSlotsByName(taggerWindow)
    # setupUi

    def retranslateUi(self, taggerWindow):
        taggerWindow.setWindowTitle(QCoreApplication.translate("taggerWindow", u"DeClutter (beta): Tagger", None))
        self.actionManage_Tags.setText(QCoreApplication.translate("taggerWindow", u"Manage Tags", None))
        self.actionNone.setText(QCoreApplication.translate("taggerWindow", u"None", None))
        self.actionNew_tagger_window.setText(QCoreApplication.translate("taggerWindow", u"New tagger window", None))
#if QT_CONFIG(shortcut)
        self.actionNew_tagger_window.setShortcut(QCoreApplication.translate("taggerWindow", u"Ctrl+N", None))
#endif // QT_CONFIG(shortcut)
        self.sourceComboBox.setItemText(0, QCoreApplication.translate("taggerWindow", u"Folder", None))
        self.sourceComboBox.setItemText(1, QCoreApplication.translate("taggerWindow", u"Tag(s)", None))

        self.browseButton.setText(QCoreApplication.translate("taggerWindow", u"Browse...", None))
        self.menuOptions.setTitle(QCoreApplication.translate("taggerWindow", u"Options", None))
        self.menuFile.setTitle(QCoreApplication.translate("taggerWindow", u"File", None))
        self.recent_menu.setTitle(QCoreApplication.translate("taggerWindow", u"Recent folders", None))
        self.menuView.setTitle(QCoreApplication.translate("taggerWindow", u"View", None))
        self.tagsDockWidget.setWindowTitle(QCoreApplication.translate("taggerWindow", u"Tags", None))
        self.mediaDockWidget.setWindowTitle(QCoreApplication.translate("taggerWindow", u"Media Preview", None))
#if QT_CONFIG(tooltip)
        self.mediaPlayButton.setToolTip(QCoreApplication.translate("taggerWindow", u"Play", None))
#endif // QT_CONFIG(tooltip)
        self.mediaPlayButton.setText("")
        self.mediaDurationLabel.setText(QCoreApplication.translate("taggerWindow", u"0:00 / 0:00", None))
        self.tagsFilterDockWidget.setWindowTitle(QCoreApplication.translate("taggerWindow", u"Tags Filter", None))
        self.tagsFilterCombo.setItemText(0, QCoreApplication.translate("taggerWindow", u"-no filter-", None))
        self.tagsFilterCombo.setItemText(1, QCoreApplication.translate("taggerWindow", u"any tags", None))
        self.tagsFilterCombo.setItemText(2, QCoreApplication.translate("taggerWindow", u"any of", None))
        self.tagsFilterCombo.setItemText(3, QCoreApplication.translate("taggerWindow", u"all of", None))
        self.tagsFilterCombo.setItemText(4, QCoreApplication.translate("taggerWindow", u"none of", None))
        self.tagsFilterCombo.setItemText(5, QCoreApplication.translate("taggerWindow", u"no tags", None))

        self.tagsFilterLabel.setText(QCoreApplication.translate("taggerWindow", u"selected:", None))
        self.otherFiltersDockWidget.setWindowTitle(QCoreApplication.translate("taggerWindow", u"Other Filters", None))
        self.nameLabel.setText(QCoreApplication.translate("taggerWindow", u"Name", None))
        self.nameCombo.setItemText(0, QCoreApplication.translate("taggerWindow", u"isn't", None))
        self.nameCombo.setItemText(1, QCoreApplication.translate("taggerWindow", u"is", None))

        self.filemask.setText(QCoreApplication.translate("taggerWindow", u"*", None))
        self.ageLabel.setText(QCoreApplication.translate("taggerWindow", u"Age", None))
        self.ageCombo.setItemText(0, QCoreApplication.translate("taggerWindow", u">=", None))
        self.ageCombo.setItemText(1, QCoreApplication.translate("taggerWindow", u"<", None))

        self.ageUnitsCombo.setItemText(0, QCoreApplication.translate("taggerWindow", u"days", None))
        self.ageUnitsCombo.setItemText(1, QCoreApplication.translate("taggerWindow", u"weeks", None))
        self.ageUnitsCombo.setItemText(2, QCoreApplication.translate("taggerWindow", u"months", None))
        self.ageUnitsCombo.setItemText(3, QCoreApplication.translate("taggerWindow", u"years", None))

        self.sizeLabel.setText(QCoreApplication.translate("taggerWindow", u"Size", None))
        self.sizeCombo.setItemText(0, QCoreApplication.translate("taggerWindow", u">=", None))
        self.sizeCombo.setItemText(1, QCoreApplication.translate("taggerWindow", u"<", None))

        self.sizeUnitsCombo.setItemText(0, QCoreApplication.translate("taggerWindow", u"B", None))
        self.sizeUnitsCombo.setItemText(1, QCoreApplication.translate("taggerWindow", u"KB", None))
        self.sizeUnitsCombo.setItemText(2, QCoreApplication.translate("taggerWindow", u"MB", None))
        self.sizeUnitsCombo.setItemText(3, QCoreApplication.translate("taggerWindow", u"GB", None))
        self.sizeUnitsCombo.setItemText(4, QCoreApplication.translate("taggerWindow", u"TB", None))

        self.typeLabel.setText(QCoreApplication.translate("taggerWindow", u"Type ", None))
        self.typeSwitchCombo.setItemText(0, QCoreApplication.translate("taggerWindow", u"is", None))
        self.typeSwitchCombo.setItemText(1, QCoreApplication.translate("taggerWindow", u"isn't", None))

    # retranslateUi

