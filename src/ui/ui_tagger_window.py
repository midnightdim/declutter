# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tagger_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDial, QDockWidget,
    QFrame, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QStatusBar,
    QVBoxLayout, QWidget)

from ..file_tree import FileTree
from ..slider import Slider
from . import DeClutter_rc

class Ui_taggerWindow(object):
    def setupUi(self, taggerWindow):
        if not taggerWindow.objectName():
            taggerWindow.setObjectName(u"taggerWindow")
        taggerWindow.resize(1302, 818)
        icon = QIcon()
        icon.addFile(u":/images/DeClutter.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
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
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
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
        self.menubar.setGeometry(QRect(0, 0, 1302, 22))
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
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.tagsDockWidget.sizePolicy().hasHeightForWidth())
        self.tagsDockWidget.setSizePolicy(sizePolicy1)
        self.tagsDockWidget.setMinimumSize(QSize(180, 500))
        self.tagsDockWidget.setStyleSheet(u"")
        self.tagsDockWidget.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea|Qt.DockWidgetArea.RightDockWidgetArea)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
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
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.tagsScrollArea.sizePolicy().hasHeightForWidth())
        self.tagsScrollArea.setSizePolicy(sizePolicy3)
        self.tagsScrollArea.setFrameShape(QFrame.Shape.Box)
        self.tagsScrollArea.setFrameShadow(QFrame.Shadow.Plain)
        self.tagsScrollArea.setLineWidth(0)
        self.tagsScrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 180, 476))
        sizePolicy2.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy2)
        self.gridLayout_3 = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.tagsLayout = QVBoxLayout()
        self.tagsLayout.setSpacing(3)
        self.tagsLayout.setObjectName(u"tagsLayout")

        self.gridLayout_3.addLayout(self.tagsLayout, 0, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer, 1, 0, 1, 1)

        self.tagsScrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_2.addWidget(self.tagsScrollArea, 0, 0, 1, 1)

        self.tagsDockWidget.setWidget(self.dockWidgetContents)
        taggerWindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.tagsDockWidget)
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
        icon1.addFile(u":/images/icons/media-play.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.mediaPlayButton.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.mediaPlayButton)

        self.mediaPositionSlider = Slider(self.mediaDockWidgetContent)
        self.mediaPositionSlider.setObjectName(u"mediaPositionSlider")
        self.mediaPositionSlider.setOrientation(Qt.Orientation.Horizontal)

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
        self.mediaDurationLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_4.addWidget(self.mediaDurationLabel, 2, 0, 1, 1)

        self.gridLayout_4.setRowStretch(0, 30)
        self.gridLayout_4.setRowStretch(1, 1)
        self.gridLayout_4.setRowStretch(2, 1)

        self.gridLayout_5.addLayout(self.gridLayout_4, 0, 0, 1, 1)

        self.mediaDockWidget.setWidget(self.mediaDockWidgetContent)
        taggerWindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.mediaDockWidget)
        self.filtersDockWidget = QDockWidget(taggerWindow)
        self.filtersDockWidget.setObjectName(u"filtersDockWidget")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.filtersDockWidget.sizePolicy().hasHeightForWidth())
        self.filtersDockWidget.setSizePolicy(sizePolicy4)
        self.filtersDockWidget.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea|Qt.DockWidgetArea.LeftDockWidgetArea|Qt.DockWidgetArea.RightDockWidgetArea)
        self.dockWidgetContents_4 = QWidget()
        self.dockWidgetContents_4.setObjectName(u"dockWidgetContents_4")
        self.verticalLayout_3 = QVBoxLayout(self.dockWidgetContents_4)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.filterConditionSwitchCombo = QComboBox(self.dockWidgetContents_4)
        self.filterConditionSwitchCombo.addItem("")
        self.filterConditionSwitchCombo.addItem("")
        self.filterConditionSwitchCombo.setObjectName(u"filterConditionSwitchCombo")
        self.filterConditionSwitchCombo.setMaximumSize(QSize(42, 16777215))

        self.horizontalLayout_6.addWidget(self.filterConditionSwitchCombo)

        self.label = QLabel(self.dockWidgetContents_4)
        self.label.setObjectName(u"label")

        self.horizontalLayout_6.addWidget(self.label)


        self.verticalLayout_3.addLayout(self.horizontalLayout_6)

        self.conditionListWidget = QListWidget(self.dockWidgetContents_4)
        self.conditionListWidget.setObjectName(u"conditionListWidget")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.conditionListWidget.sizePolicy().hasHeightForWidth())
        self.conditionListWidget.setSizePolicy(sizePolicy5)
        self.conditionListWidget.setMinimumSize(QSize(170, 0))
        self.conditionListWidget.setBaseSize(QSize(170, 0))

        self.verticalLayout_3.addWidget(self.conditionListWidget)

        self.filterButtonsLayout = QHBoxLayout()
        self.filterButtonsLayout.setObjectName(u"filterButtonsLayout")
        self.filterAddButton = QPushButton(self.dockWidgetContents_4)
        self.filterAddButton.setObjectName(u"filterAddButton")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.filterAddButton.sizePolicy().hasHeightForWidth())
        self.filterAddButton.setSizePolicy(sizePolicy6)
        self.filterAddButton.setMinimumSize(QSize(50, 0))
        self.filterAddButton.setMaximumSize(QSize(55, 16777215))
        self.filterAddButton.setBaseSize(QSize(0, 0))

        self.filterButtonsLayout.addWidget(self.filterAddButton)

        self.filterRemoveButton = QPushButton(self.dockWidgetContents_4)
        self.filterRemoveButton.setObjectName(u"filterRemoveButton")
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.filterRemoveButton.sizePolicy().hasHeightForWidth())
        self.filterRemoveButton.setSizePolicy(sizePolicy7)
        self.filterRemoveButton.setMaximumSize(QSize(55, 16777215))

        self.filterButtonsLayout.addWidget(self.filterRemoveButton)

        self.filterClearButton = QPushButton(self.dockWidgetContents_4)
        self.filterClearButton.setObjectName(u"filterClearButton")
        self.filterClearButton.setMaximumSize(QSize(55, 16777215))

        self.filterButtonsLayout.addWidget(self.filterClearButton)


        self.verticalLayout_3.addLayout(self.filterButtonsLayout)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_3)

        self.filtersDockWidget.setWidget(self.dockWidgetContents_4)
        taggerWindow.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.filtersDockWidget)

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
        self.sourceComboBox.setItemText(1, QCoreApplication.translate("taggerWindow", u"Tagged", None))

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
        self.filtersDockWidget.setWindowTitle(QCoreApplication.translate("taggerWindow", u"Filters", None))
        self.filterConditionSwitchCombo.setItemText(0, QCoreApplication.translate("taggerWindow", u"any", None))
        self.filterConditionSwitchCombo.setItemText(1, QCoreApplication.translate("taggerWindow", u"all", None))

        self.label.setText(QCoreApplication.translate("taggerWindow", u"of these must be true:", None))
        self.filterAddButton.setText(QCoreApplication.translate("taggerWindow", u"Add", None))
        self.filterRemoveButton.setText(QCoreApplication.translate("taggerWindow", u"Remove", None))
        self.filterClearButton.setText(QCoreApplication.translate("taggerWindow", u"Clear", None))
    # retranslateUi

