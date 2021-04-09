import sys
from PySide2.QtGui import QIcon, QColor, QCursor, QStandardItemModel, QStandardItem
from PySide2.QtWidgets import QWidget, QApplication, QMainWindow, QFileSystemModel, QFileIconProvider, QMenu, QAbstractItemView, QAction, QFrame, QTreeView
from PySide2.QtWidgets import QWidgetAction, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QDialog, QFileDialog, QListWidget, QDialogButtonBox, QSpacerItem, QSlider, QAbstractSlider
from PySide2.QtCore import QObject, QDir, Qt, QModelIndex, QSortFilterProxyModel, QUrl, QRect, QSize, QEvent, QSignalBlocker, QMimeData, QUrl, QDateTime, QMimeDatabase
from PySide2.QtMultimedia import QMediaPlayer, QMediaPlaylist
from PySide2.QtMultimediaWidgets import QVideoWidget
from ui_tagger_window import Ui_taggerWindow
from tags_dialog import TagsDialog, generate_tag_model
from declutter_lib import *
from os.path import normpath
from pathlib import Path
from send2trash import send2trash

class TaggerWindow(QMainWindow):
    def __init__(self):
        super(TaggerWindow, self).__init__()
        self.ui = Ui_taggerWindow()
        self.ui.setupUi(self)

        # media played init
        self.playlist = QMediaPlaylist()
        self.player = QMediaPlayer()
        # self.player.setNotifyInterval(500)
        self.videoWidget = QVideoWidget()
        self.ui.playerLayout.addWidget(self.videoWidget)
        self.player.setVideoOutput(self.videoWidget)
        self.player.setPlaylist(self.playlist)
        self.ui.mediaVolumeDial.valueChanged.connect(self.player.setVolume)
        self.ui.mediaPlayButton.clicked.connect(self.play_media)
        # self.ui.mediaPauseButton.clicked.connect(self.pause_media)
        self.player.durationChanged.connect(self.change_duration)
        self.player.positionChanged.connect(self.change_position)
        self.player.stateChanged.connect(self.media_update_play_button)
        
        self.ui.mediaPositionSlider.actionTriggered.connect(self.action_trig)

        self.ui.mediaDockWidget.installEventFilter(self)
        self.ui.treeView.installEventFilter(self)

        # self.ui.mediaPositionSlider.valueChanged.connect(self.val_changed)
        self.ui.treeView.setDragDropMode(QAbstractItemView.DragDrop)
        self.ui.treeView.setAcceptDrops(True)
        self.ui.treeView.setDefaultDropAction(Qt.MoveAction)
        self.ui.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.treeView.customContextMenuRequested.connect(self.context_menu)
        self.filter_tags = []
        self.filter_tags_checkboxes = {}
        self.prev_indexes = []

        self.ui.menuView.addAction(self.ui.tagsDockWidget.toggleViewAction())
        self.ui.menuView.addAction(self.ui.tagsFilterDockWidget.toggleViewAction())
        self.ui.menuView.addAction(self.ui.mediaDockWidget.toggleViewAction())
        self.ui.menuView.addAction(self.ui.otherFiltersDockWidget.toggleViewAction())
        self.ui.otherFiltersDockWidget.hide()

        self.populate() # TBD can't it be just a part of init()?

    def closeEvent(self, event):
        self.player.stop()
        self.playlist.clear()
        # print(event)

    # def dropEvent(self, event):
    #     print('dropevent')
    #     # lines = []
    #     for url in event.mimeData().urls():
    #         print(url.toLocalFile())
            # lines.append('dropped: %r' % url.toLocalFile())
        # print('\n'.join(lines))

    # volume knob controlled by mouse wheel if the playback is on, click on media dock widget controls play/pause
    def eventFilter(self, source, event):
        # print(source,event,event.type())
        if source == self.ui.treeView:
            # print(event,event.type())
            if event.type() == QEvent.KeyPress:
                if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    # self.model.filePath(self.sorting_model.mapToSource(self.ui.treeView.selectionModel().selectedRows()[0]))
                    if self.ui.treeView.state() is not QAbstractItemView.EditingState:
                        self.open()
                if event.key() == Qt.Key_Delete:
                    # print(self.ui.treeView.selectionModel().selectedRows())
                    # indexes = self.ui.treeView.selectedIndexes()
                    indexes = self.ui.treeView.selectionModel().selectedRows()
                    # print(indexes)
                    self.player.stop()
                    self.playlist.clear()
                    if event.modifiers() == Qt.ShiftModifier:
                        for index in indexes: #TBD add try/except here
                            self.model.remove(self.sorting_model.mapToSource(index))
                            remove_all_tags(os.path.normpath(self.model.filePath(self.sorting_model.mapToSource(index))))
                        self.ui.statusbar.showMessage(str(len(indexes))+" item(s) deleted")
                    else:
                        for index in indexes: #TBD add try/except here
                            send2trash(os.path.normpath(self.model.filePath(self.sorting_model.mapToSource(index))))
                            remove_all_tags(os.path.normpath(self.model.filePath(self.sorting_model.mapToSource(index))))
                        self.ui.statusbar.showMessage(str(len(indexes))+" item(s) sent to trash")                
                elif event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
                    indexes = self.ui.treeView.selectionModel().selectedRows()
                    urls = [QUrl(self.model.filePath(self.sorting_model.mapToSource(index))) for index in indexes]
                    print(urls)
                    # clipboard = QApplication.clipboard()
                    # clipboard.setMimeData()
                    mime_data = QMimeData()
                    mime_data.setUrls(urls)
                    clipboard = QApplication.clipboard()
                    clipboard.setMimeData(mime_data)
                    # print(QApplication.clipboard().mimeData().urls())
                    print(clipboard.mimeData().urls())
                elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
                    # print(self.clipboard().mimeData().urls())
                    # print(QApplication.clipboard().text())
                    # print(QApplication.clipboard().mimeData().urls())
                    clipboard = QApplication.clipboard()
                    html = clipboard.mimeData().html()
                    print(clipboard.mimeData().urls())
                    print(clipboard.mimeData().text())
                    # print(html)
                    # mime_data = QApplication.clipboard().mimeData()
                    # print(mime_data)
                    for url in clipboard.mimeData().urls():
                        # self.model
                        print(url.toLocalFile())
                    # print('enter')
                    # print(QApplication.clipboard().text())
                    #  if index.column() == 0
                    # for index in indexes:
                    #     os.remove(self.model.filePath(self.sorting_model.mapToSource(index)))
                    # this works with errors for some reason
                    # for index in indexes:
                    #     self.model.remove(self.sorting_model.mapToSource(index))         
                         

                # self.update_status()
                return False
            if event.type() == QEvent.Drop:
                print('drop')
                for url in event.mimeData().urls():
                    print(url.toLocalFile())
        else: 
            if event.type() == QEvent.MouseButtonPress:
                self.play_media()
            if event.type() == QEvent.Wheel:
                if event.delta(): #and self.player.state() == QMediaPlayer.State.PlayingState:
                        self.ui.mediaVolumeDial.triggerAction(QAbstractSlider.SliderAction.SliderPageStepAdd if event.delta()>0 else QAbstractSlider.SliderAction.SliderPageStepSub)            
                        return False
        # return super(TaggerWindow, self).eventFilter(source, event)
        return super(TaggerWindow, self).eventFilter(source, event)

    # aux function, required for smooth navigation using slider
    def action_trig(self, action):    
        if action == 1:
            self.seek_position(self.ui.mediaPositionSlider.value())

    # def print_model(self):
    #     for i in range(0,self.tag_model.rowCount()):
    #     # i = 0
    #     # for group in data.keys():
    #         group = self.tag_model.item(i).data(Qt.UserRole)
    #         print('group:',group['name'])
    #         for k in range(0,self.tag_model.item(i).rowCount()):
    #             tag = self.tag_model.item(i).child(k).data(Qt.UserRole)
    #             print('tag:',tag['name'])

##### Begin Media Player section
    def media_update_play_button(self,state):
        icon1 = QIcon()
        icon1.addFile(u":/images/icons/media-pause.svg" if state == QMediaPlayer.State.PlayingState else u":/images/icons/media-play.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.ui.mediaPlayButton.setIcon(icon1)

    def play_media(self):
        file_url = QUrl.fromLocalFile(self.model.filePath(self.sorting_model.mapToSource(self.ui.treeView.currentIndex())))
        if self.player.state() == QMediaPlayer.State.PlayingState and self.player.currentMedia().canonicalUrl() == file_url:
            self.player.pause()
        elif self.player.state() != QMediaPlayer.State.PausedState and self.player.currentMedia().canonicalUrl() != file_url:
            self.playlist.clear()
            self.playlist.addMedia(file_url)
            self.player.play()
        else:
            self.player.play()

    def change_position(self, position):
        self.ui.mediaPositionSlider.setValue(position)
        self.ui.mediaDurationLabel.setText(millis_to_str(position)+" / "+millis_to_str(self.player.duration()))

    def seek_position(self,position):
        self.player.setPosition(position)

    def change_duration(self, duration):
        self.ui.mediaDurationLabel.setText("0:00 / "+millis_to_str(duration))
        self.ui.mediaPositionSlider.setRange(0, duration)
        self.ui.mediaPositionSlider.setPageStep(int(duration/20))
##### End Media Player section

    def populate(self):
        #path = r"D:\DIM\WinFiles\Downloads"
        self.settings = load_settings()
        self.checkAction = {}  # checkboxes in context menu
        self.tag_checkboxes = {} # checkboxes in the dock widget
        self.tag_model = QStandardItemModel()
        generate_tag_model(self.tag_model, get_tags_and_groups())

        self.ui.actionNone1 = QAction(self)
        #self.ui.actionNone1.setObjectName(u"actionNone1")
        # self.ui.actionNone1.setText(r"C:\Users\DIM\AppData\Roaming\DeClutter\Users\DIM\AppData\Roaming\DeClutter\Users\DIM\AppData\Roaming\DeClutter\Users\DIM\AppData\Roaming\DeClutter")
        # self.ui.actionNone1.triggered.connect(self.open_recent)
        self.ui.recent_menu.aboutToShow.connect(self.update_recent_menu)
        self.ui.recent_menu.triggered.connect(self.open_file_from_recent)
        #self.ui.menuRecent_folders.addAction(self.ui.actionNone1)
        #self.actionNone.setEnabled(False)

        path = self.settings['current_folder'] if 'current_folder' in self.settings.keys() and self.settings['current_folder'] != '' else normpath(QDir.homePath())
        #path = r"D:\Projects.other\Mikhail Beloglazov"
        #path = r"D:\DIM\WinFiles\Downloads"
        #path = r"."
        
        self.model = TagFSModel()
        # self.model = QFileSystemModel()
        self.model.setRootPath(path)
        self.model.setReadOnly(False)
        self.model.setFilter(QDir.NoDot | QDir.AllEntries | QDir.Hidden)
        self.model.sort(0,Qt.SortOrder.AscendingOrder)

        self.sorting_model = SortingModel()
        self.sorting_model.mode = "Folder"
        #self.sorting_model.filter_paths = []
        self.sorting_model.setSourceModel(self.model)

        self.ui.treeView.setModel(self.sorting_model)
        # self.ui.treeView.setModel(self.model)

        self.ui.treeView.setRootIndex(self.sorting_model.mapFromSource(self.model.index(path)))
        # self.ui.treeView.setRootIndex(self.model.index(path))

        self.model.setIconProvider(QFileIconProvider())
              
        self.ui.treeView.header().resizeSection(0,350)
        
        #self.ui.treeView.header().setSortIndicator(0, Qt.AscendingOrder)
        
        # self.ui.treeView.setSortingEnabled(True)
        # self.ui.treeView.setRootIsDecorated(False)
        # self.ui.treeView.setItemsExpandable(False)        
                
        self.ui.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.ui.treeView.selectionModel().selectionChanged.connect(self.update_status)

        self.ui.treeView.doubleClicked.connect(self.open)
        self.ui.actionManage_Tags.triggered.connect(self.manage_tags)

        self.ui.pathEdit.setText(path)
        self.ui.pathEdit.returnPressed.connect(self.change_path)
        self.ui.browseButton.clicked.connect(self.choose_path)
        self.ui.sourceComboBox.currentIndexChanged.connect(self.update_ui)
        self.ui.selectTagsButton.clicked.connect(self.select_tags)
        self.model.directoryLoaded.connect(self.dir_loaded)

        # self.ui.treeView.installEventFilter(self)
        # self.setStyleSheet("QDockWidget::title {position: relative; top: 100px;}")
        # self.setStyleSheet("QMainWindow::separator{ margin: 100px;}");
        
        self.init_tag_checkboxes()
        self.update_ui()

    # def test(self, state):
    #     print('test')
    #     print(self.sender().checkState())
    #     print(state)

    # def test2(self):
    #     print('test2')
    #     print(self.sender().checkState())

    def mouseDoubleClickEvent(self, event):  # TBD maybe remove this
        widget = self.childAt(event.pos())
        if widget is not None and widget.objectName() == "scrollAreaWidgetContents":
            self.manage_tags()

    def init_tag_checkboxes(self):
        
        while True:
            if self.ui.tagsLayout.itemAt(0):
                self.ui.tagsLayout.itemAt(0).widget().deleteLater()       
            if not self.ui.tagsLayout.takeAt(0):
                break

        for i in range(0,self.tag_model.rowCount()):
        # i = 0
        # for group in data.keys():
            group = self.tag_model.item(i).data(Qt.UserRole)
            if group['name_shown']:
                self.ui.tagsLayout.addWidget(QLabel('<b>'+group['name']+'</b>'))
            for k in range(0,self.tag_model.item(i).rowCount()):
                tag = self.tag_model.item(i).child(k).data(Qt.UserRole)
                self.tag_checkboxes[tag['name']] = QCheckBox(tag['name'])
                self.ui.tagsLayout.addWidget(self.tag_checkboxes[tag['name']])
                # self.tag_checkboxes[tag['name']].stateChanged.connect(self.set_tags)
                # self.tag_checkboxes[tag['name']].stateChanged.connect(self.test)
                self.tag_checkboxes[tag['name']].clicked.connect(self.set_tags)
                # self.tag_checkboxes[tag['name']].toggled.connect(self.test2)
                if tag['color']:
                    color = QColor()
                    color.setRgba(tag['color'])
                    # color.setAlpha(100)
                    self.tag_checkboxes[tag['name']].setPalette(color)
                    self.tag_checkboxes[tag['name']].setAutoFillBackground(True) 
            if i<self.tag_model.rowCount()-1:
                self.ui.tagsLayout.addWidget(QHLine())

    def update_tag_checkboxes(self):
        # print('update_tag_checkboxes called')
        indexes = self.ui.treeView.selectionModel().selectedRows()
        cur_selection = [normpath(self.model.filePath(self.sorting_model.mapToSource(index))) for index in indexes]       

        all_files_tags = []
        for f in cur_selection:  # TBD v3 not the most efficient procedure maybe
            all_files_tags.extend(get_tags(f))
      
        for t in get_all_tags():
            # blocker = QSignalBlocker(self.tag_checkboxes[t])
            if t not in all_files_tags:
                self.tag_checkboxes[t].setTristate(False)
                if self.tag_checkboxes[t].checkState() is not Qt.CheckState.Unchecked:
                    self.tag_checkboxes[t].setChecked(False)
            elif all_files_tags.count(t) < len(cur_selection):
                self.tag_checkboxes[t].setTristate(True)
                if self.tag_checkboxes[t].checkState() is not Qt.CheckState.PartiallyChecked:
                    self.tag_checkboxes[t].setCheckState(Qt.CheckState.PartiallyChecked)
            else:
                if self.tag_checkboxes[t].checkState() is not Qt.CheckState.Checked:
                    self.tag_checkboxes[t].setChecked(True)

    def update_recent_menu(self):
        self.ui.recent_menu.clear()
        for row, foldername in enumerate(self.settings['recent_folders'], 1):
            recent_action = self.ui.recent_menu.addAction('&{}. {}'.format(
                row, foldername))
            recent_action.setData(foldername)

    def open_file_from_recent(self, action):
        # print('opening from')
        #self.open_file(action.data())
        self.ui.pathEdit.setText(normpath(action.data()))
        self.change_path()
        self.ui.sourceComboBox.setCurrentText("Folder")
        # self.sorting_model.mode = "Folder"
        self.update_ui()

    def dir_loaded(self):
        #print("dir loaded")
        if self.ui.sourceComboBox.currentText() == "Tag(s)":
            self.ui.treeView.expandAll()

    def update_filter_tags(self):
        # print(self.filter_tags)
        # print(self.filter_tags_checkboxes)
        for t in self.filter_tags_checkboxes:
            self.ui.horizontalLayout.takeAt(self.ui.horizontalLayout.indexOf(self.filter_tags_checkboxes[t]))    
            self.filter_tags_checkboxes[t].deleteLater()
        self.filter_tags_checkboxes = {}
        self.filter_tags.reverse()
        for t in self.filter_tags:            
            self.filter_tags_checkboxes[t] = QCheckBox(t)
            if tag_get_color(t):
                color = QColor()
                color.setRgba(tag_get_color(t))                
                self.filter_tags_checkboxes[t].setPalette(color)
                self.filter_tags_checkboxes[t].setAutoFillBackground(True)            
            self.filter_tags_checkboxes[t].setChecked(True)
            self.filter_tags_checkboxes[t].stateChanged.connect(self.update_treeview)
            self.ui.horizontalLayout.insertWidget(1,self.filter_tags_checkboxes[t])
        self.update_treeview()

    # def apply_filter_tags(self):
          
    #     all_tags=[]
    #     for t in self.filter_tags_checkboxes:
    #         if self.filter_tags_checkboxes[t].isChecked():
    #             all_tags.append(t)
    #     self.sorting_model.filter_tags = all_tags
    #     self.update_treeview()

    def select_tags(self):
        tags_dialog = QDialog()
        tags_dialog.setWindowTitle("Select Tags")
        tags_dialog.setMinimumHeight(400)
        treeView = QTreeView(tags_dialog)
        treeView.setModel(self.tag_model)

        treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        treeView.setHeaderHidden(True)
        treeView.expandAll()
        layout = QVBoxLayout(tags_dialog)
        layout.addWidget(treeView)        
        buttonBox = QDialogButtonBox(tags_dialog)
        buttonBox.setObjectName(u"buttonBox")
        buttonBox.setOrientation(Qt.Horizontal)
        buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(tags_dialog.accept)
        buttonBox.rejected.connect(tags_dialog.reject)

        layout.addWidget(buttonBox)

        tags_dialog.setLayout(layout)
        tags_dialog.treeView = treeView
        
        tags_dialog.setWindowIcon(QIcon('DeClutter.ico'))
        
        if tags_dialog.exec_():
            self.filter_tags = [t.data() for t in tags_dialog.treeView.selectedIndexes()]
            self.update_filter_tags()

    def update_ui(self):
        mode = self.ui.sourceComboBox.currentText()
        #self.sorting_model.mode = mode
        # print('mode',self.sorting_model.mode)
        self.ui.selectTagsButton.setVisible(mode in ('Folder & tags', 'Tag(s)'))
        self.ui.pathEdit.setEnabled(mode in ('Folder', 'Folder & tags', 'Folder (untagged)'))
        self.ui.browseButton.setEnabled(mode in ('Folder', 'Folder & tags','Folder (untagged)'))
        if mode in ('Folder', 'Folder & tags'):
            for t in self.filter_tags_checkboxes:
                self.ui.horizontalLayout.takeAt(self.ui.horizontalLayout.indexOf(self.filter_tags_checkboxes[t]))    
                self.filter_tags_checkboxes[t].deleteLater()                
                # self.filter_tags_checkboxes[t].hide()
                # self.filter_tags_checkboxes[t].destroy()
                # self.filter_tags_checkboxes[t].setVisible(False)
            self.filter_tags = {}
            self.filter_tags_checkboxes = [] # TBD this is inefficient
        self.update_treeview()

    def update_treeview(self):
        # print('updating treeview')
        #print(self.sorting_model.filter_paths)
        all_tags=[]
        for t in self.filter_tags_checkboxes:
            if self.filter_tags_checkboxes[t].isChecked():
                all_tags.append(t)
        self.sorting_model.filter_tags = all_tags
        mode = self.ui.sourceComboBox.currentText()
        # self.sorting_model.mode = mode
        if mode == 'Tag(s)': # TBD simplify this
            # print('tags')
            self.model = TagFSModel()
            path = "."
            self.model.setRootPath(path)
            self.model.setFilter(QDir.NoDotAndDotDot | QDir.AllEntries | QDir.Hidden)           
            self.model.sort(0,Qt.SortOrder.AscendingOrder)

            #path = load_settings()['current_folder']            
            #print('path',path)
            self.sorting_model = SortingModel()
            # self.sorting_model = QSortFilterProxyModel()
            self.sorting_model.setSourceModel(self.model)            
            self.sorting_model.setSortCaseSensitivity(Qt.CaseInsensitive)
            self.sorting_model.mode = mode
            self.sorting_model.filter_tags = all_tags
            self.sorting_model.recalc_tagged_paths(True)
            # self.ui.treeView.setRootIndex(self.model.index(path))
            self.ui.treeView.setModel(self.sorting_model)
            self.ui.treeView.setRootIndex(self.sorting_model.mapFromSource(self.model.index(path)))           
            self.model.setIconProvider(QFileIconProvider())
            self.ui.treeView.header().setSortIndicator(0, Qt.AscendingOrder)                        
            self.ui.treeView.setItemsExpandable(True)
            self.ui.treeView.setRootIsDecorated(True)            
            self.ui.treeView.selectionModel().selectionChanged.connect(self.update_status)
            self.ui.treeView.expandAll()
            self.model.directoryLoaded.connect(self.dir_loaded)            
            #self.ui.treeView.expand(self.sorting_model.mapFromSource(self.model.index(path)))
        else:
            # print('not tags')
            self.model = TagFSModel()
            # self.model = QFileSystemModel()
            self.model.setReadOnly(False)
            path = load_settings()['current_folder']            
            self.model.setRootPath(path)
            self.model.setFilter(QDir.NoDot | QDir.AllEntries | QDir.Hidden)
            self.model.sort(0,Qt.SortOrder.AscendingOrder)          
            self.sorting_model = SortingModel(self)
            self.sorting_model.mode = mode
            self.sorting_model.filter_tags = all_tags
            self.sorting_model.recalc_tagged_paths()
            # print(self.sorting_model.filter_tags)
            # print(self.sorting_model.tagged_paths)
            self.sorting_model.setSourceModel(self.model)   
            self.sorting_model.setSortCaseSensitivity(Qt.CaseInsensitive)
            self.sorting_model.setSortLocaleAware(True)           
            
            self.ui.treeView.setModel(self.sorting_model)
            # self.ui.treeView.setModel(self.model)
            
            self.ui.treeView.setRootIndex(self.sorting_model.mapFromSource(self.model.index(path)))
            # self.ui.treeView.setRootIndex(self.model.index(path))

            self.model.setIconProvider(QFileIconProvider())
            self.ui.treeView.header().setSortIndicator(0, Qt.AscendingOrder)
            self.ui.treeView.setItemsExpandable(False)
            self.ui.treeView.setRootIsDecorated(False)
            self.ui.treeView.selectionModel().selectionChanged.connect(self.update_status)
            self.ui.treeView.setDragDropMode(QAbstractItemView.DragDrop) # TBD this is duplicated in __init__, not good
            self.ui.treeView.setAcceptDrops(True)
            self.ui.treeView.setDefaultDropAction(Qt.MoveAction)
            # print('drop action set to',self.ui.treeView.defaultDropAction())
            # print(self.ui.treeView.acceptDrops())

    def update_status(self):
        # print('update status')
        indexes = self.ui.treeView.selectionModel().selectedRows()
        # indexes = self.ui.treeView.selectedIndexes()
        indexes.sort()
        self.prev_indexes.sort()
        if indexes != self.prev_indexes:
            # print('selection changed')
            self.player.stop()
            path = self.model.filePath(self.sorting_model.mapToSource(self.ui.treeView.currentIndex()))
            ftype = get_file_type(path)
            if os.path.isfile(path) and ftype in ('Audio','Video','Image'):
                # print(self.model.filePath(self.sorting_model.mapToSource(self.ui.treeView.currentIndex())))
                file_url = QUrl.fromLocalFile(self.model.filePath(self.sorting_model.mapToSource(self.ui.treeView.currentIndex())))
                # file_ext = self.model.filePath(self.sorting_model.mapToSource(self.ui.treeView.currentIndex()))[-3:]
                if ftype == 'Audio': # TBD change this to audio file type
                    self.ui.playerLayout.setGeometry(QRect(0,0,0,0))
                if ftype == 'Image':
                    self.ui.playerLayout.update()
                self.playlist.clear()
                self.playlist.addMedia(file_url)
                self.player.play()
                self.player.pause()
                self.ui.mediaPlayButton.setVisible(ftype in ('Video','Audio'))
                self.ui.mediaPositionSlider.setVisible(ftype in ('Video','Audio'))
                self.ui.mediaVolumeDial.setVisible(ftype in ('Video','Audio'))
                self.ui.mediaDurationLabel.setVisible(ftype in ('Video','Audio'))
            else:
                # print('other file type')
                self.playlist.clear()
                self.ui.playerLayout.setGeometry(QRect(0,0,0,0))
                self.ui.mediaPlayButton.setVisible(False)
                self.ui.mediaPositionSlider.setVisible(False)
                self.ui.mediaVolumeDial.setVisible(False)
                self.ui.mediaDurationLabel.setVisible(False)                
        self.prev_indexes = indexes
        num_selected = len(self.ui.treeView.selectionModel().selectedRows())  # TBD I don't like this /5
        self.ui.statusbar.showMessage(str(num_selected)+" item(s) selected")
        self.update_tag_checkboxes()

    def choose_path(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
            "QFileDialog.getExistingDirectory()",
            self.ui.pathEdit.text(), options)
        if directory:
            self.ui.pathEdit.setText(normpath(directory))
            self.change_path()

    def change_path(self):
        self.player.stop()
        self.playlist.clear()
        file_path = self.ui.pathEdit.text()
        if os.path.isdir(file_path):
            self.ui.statusbar.clearMessage()
            self.model.setRootPath(normpath(file_path)) # TBD reuse this in a function
            self.ui.treeView.setRootIndex(self.sorting_model.mapFromSource(self.model.index(file_path)))
            self.ui.pathEdit.setText(file_path)
            if normpath(self.settings['current_folder']) != normpath(file_path):
                self.settings['current_folder'] = file_path
                if file_path in self.settings['recent_folders']:
                    self.settings['recent_folders'].remove(file_path)
                self.settings['recent_folders'].insert(0,file_path)
                if len(self.settings['recent_folders'])>15:
                    del self.settings['recent_folders'][-1]
            save_settings(SETTINGS_FILE,self.settings)

    def manage_tags(self):
        self.tags_dialog = TagsDialog(self.tag_model)
        # self.tags_dialog.model = self.tag_model
        self.tags_dialog.exec_()
        self.init_tag_checkboxes()
        self.update_tag_checkboxes()

    def open(self):
        index = self.ui.treeView.currentIndex()
        # print(index.data(Qt.UserRole))
        # print(self.sorting_model.mapToSource(index).data())
        #file_path = normpath(self.model.filePath(index))
        file_path = normpath(self.model.filePath(self.sorting_model.mapToSource(index)))
        if os.path.isdir(file_path):
            self.ui.statusbar.clearMessage()
            self.model.setRootPath(normpath(file_path)) # TBD reuse this in a function
            self.ui.treeView.setRootIndex(self.sorting_model.mapFromSource(self.model.index(file_path)))
            self.ui.pathEdit.setText(file_path)
            self.settings['current_folder'] = file_path
            save_settings(SETTINGS_FILE,self.settings)
        elif os.path.isfile(file_path):
            os.startfile(file_path)

    def context_menu(self, position):
        #index = self.ui.treeView.currentIndex()
        indexes = self.ui.treeView.selectionModel().selectedRows()
        cur_selection = [normpath(self.model.filePath(self.sorting_model.mapToSource(index))) for index in indexes]

        all_files_tags = []
        for f in cur_selection:  # TBD v3 not the most efficient procedure maybe
            all_files_tags.extend(get_tags(f))

        menu = QMenu()
        
        self.checkAction = {}

        for i in range(0,self.tag_model.rowCount()):
            group = self.tag_model.item(i).data(Qt.UserRole)
            if group['name_shown']:
                menu.addAction(group['name'])
                # self.ui.tagsLayout.addWidget(QLabel('<b>'+group['name']+'</b>'))
            for k in range(0,self.tag_model.item(i).rowCount()):
                tag = self.tag_model.item(i).child(k).data(Qt.UserRole)  
                t = tag['name']              
                self.checkAction[t] = CheckBoxAction(self,t)
                self.checkAction[t].checkbox.clicked.connect(self.set_tags)
                if t not in all_files_tags:
                    pass
                    #window[r].update(text = CHAR_UNCHECKED + " " + r)
                elif all_files_tags.count(t) < len(cur_selection):
                    self.checkAction[t].checkbox.setTristate(True)
                    if self.checkAction[t].checkbox.checkState() is not Qt.CheckState.PartiallyChecked:
                        self.checkAction[t].checkbox.setCheckState(Qt.CheckState.PartiallyChecked)
                else:
                    if self.checkAction[t].checkbox.checkState() is not Qt.CheckState.Checked:
                        self.checkAction[t].checkbox.setChecked(True)

                menu.addAction(self.checkAction[t])
                # self.tag_checkboxes[tag['name']] = QCheckBox(tag['name'])
                # self.ui.tagsLayout.addWidget(self.tag_checkboxes[tag['name']])

        # for t in get_all_tags():
        #     self.checkAction[t] = CheckBoxAction(self,t)           
        #     self.checkAction[t].checkbox.stateChanged.connect(self.set_tags)
        #     #print(t)
        #     # if t in file_tags:
        #     #     self.checkAction[t].checkbox.setCheckState(Qt.CheckState.Checked)
        #     #     self.checkAction[t].checkbox.setChecked(True)
        #     if t not in all_files_tags:
        #         pass
        #         #window[r].update(text = CHAR_UNCHECKED + " " + r)
        #     elif all_files_tags.count(t) < len(cur_selection):
        #         self.checkAction[t].checkbox.setTristate(True)
        #         if self.checkAction[t].checkbox.checkState() is not Qt.CheckState.PartiallyChecked:
        #             self.checkAction[t].checkbox.setCheckState(Qt.CheckState.PartiallyChecked)
        #     else:
        #         if self.checkAction[t].checkbox.checkState() is not Qt.CheckState.Checked:
        #             self.checkAction[t].checkbox.setChecked(True)


        #     menu.addAction(self.checkAction[t])

        cursor = QCursor()
        menu.exec_(cursor.pos())

    def set_tags(self, state):
        # print('set_tags called')
        sender = self.sender()
        # print(sender)
        # print("clicked",state)
        # index = self.ui.treeView.currentIndex()
        # file_path = normpath(self.model.filePath(self.sorting_model.mapToSource(index)))      
        
        indexes = self.ui.treeView.selectionModel().selectedRows()

        # for index in indexes:
        #     print(index)

        # print(indexes)
        cur_selection = [normpath(self.model.filePath(self.sorting_model.mapToSource(index))) for index in indexes] # TBD not very optimal
        # print(cur_selection)

        for file_path in cur_selection:
            # print(file_path)
            if state: #checked - it was 2 when used with stateChanged
                add_tag(file_path,sender.text())
            elif not state: #unchecked - it was 0 when used with stateChanged
                remove_tag(file_path,sender.text())
        # print('tags set, updating checkboxes')
        # self.update_tag_checkboxes()
        # print('done')

class TagFSModel(QFileSystemModel):
    def columnCount(self, parent = QModelIndex()):
        return super(TagFSModel, self).columnCount()+1

    # def supportedDropActions(self) -> Qt.DropActions:
    #     # print("supportedDropActions")
    #     return Qt.MoveAction  | super(TagFSModel, self).supportedDropActions()
    
    def supportedDragActions(self) -> Qt.DropActions:
        # print("supportedDragActions")
        return Qt.MoveAction # | super(TagFSModel, self).supportedDropActions()         

    def headerData(self, section, orientation, role):
        if section == 4 and role == Qt.DisplayRole:
            return "Tag(s)"
        else:
            return super(TagFSModel, self).headerData(section, orientation, role)        

    def data(self, index, role):
        # if index.column() == 0: #displays full path instead of the name
        #     if role == Qt.DisplayRole:
        #         return self.filePath(index)
        # if index.column() == 1 and role == Qt.DisplayRole:
        #     return self.size(index)

        # if index.column() == 3 and role == Qt.DisplayRole:
        #     return QDateTime.toString(self.lastModified(index),"dd.MM.yyyy hh:mm")

        if index.column() == 2 and role == Qt.DisplayRole:
            return QMimeDatabase().mimeTypeForFile(self.filePath(index)).comment()

        if index.column() == self.columnCount() - 1:
            if role == Qt.DisplayRole:
                #return self.fileName(index)
                return ', '.join(get_tags(normpath(self.filePath(index))))
            if role == Qt.TextAlignmentRole:
                return Qt.AlignLeft
        if role == Qt.BackgroundRole and get_tags(normpath(self.filePath(index))) and tag_get_color(get_tags(normpath(self.filePath(index)))[0]):
            #return QColor("#ccffff")
            color = QColor()
            color.setRgba(tag_get_color(get_tags(normpath(self.filePath(index)))[0]))
            return color

        return super(TagFSModel, self).data(index, role)

    # def dropMimeData(self, data: QMimeData, action: Qt.DropAction,
    #                 row: int, column: int, parent: QModelIndex) -> bool:
    #     print(row,column)

    # def sort(self, index, order):
    #     return super(TagFSModel, self).sort(index, order)

class CheckBoxAction(QWidgetAction):
    def __init__(self, parent, text):
        #print(text)
        #super(CheckBoxAction, parent=QAction).__init__()
        super(CheckBoxAction, self).__init__(parent)
        layout = QHBoxLayout()       
        self.widget = QWidget()
        #self.tag = text
        #label = QLabel(text)
        #label.setAlignment(Qt.AlignLeft)
        self.checkbox = QCheckBox()
        self.checkbox.setText(text)
        if tag_get_color(text):
            self.checkbox.setPalette(QColor(tag_get_color(text)))
            self.checkbox.setAutoFillBackground(True)
        #self.checkbox.setTristate()
        layout.addWidget(self.checkbox)
        #layout.addWidget(label)
        layout.addStretch()
        layout.setContentsMargins(3,3,6,3)
        
        self.widget.setLayout(layout)

        self.setDefaultWidget(self.widget)

    # def createWidget(self,text):
    #     print("testing")
    #     return self.widget

class SortingModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        # print(parent)
        self.mode = ""
        self.filter_tags = []
        self.tagged_paths = []

    # def sort(self, column, order):
    #     print('sort')
    #     # super(SortingModel, self).sort(column, order)

    #     if column not in (0,4):
    #         print('here')
    #         self.sourceModel().sort(column, order)
    #         self.parent().sorting_model.setSourceModel(self.parent().model)
    #         self.parent().ui.treeView.setModel(self.parent().sorting_model)            
    #         # super(SortingModel, self).sort(column, order)
    #     else:
    #         super(SortingModel, self).sort(column, order)


    def recalc_tagged_paths(self, tree=False):
        # print('tagged_paths called')
        all_paths=[]
        # print('here')
        # print(self.filter_tags)
        for t in self.filter_tags:
            all_paths = list(set(all_paths + get_files_by_tag(t)))
        # print(all_paths)
        if not tree:
            self.tagged_paths = all_paths
            return
        for t in all_paths:
            if str(Path(t).parent).lower() not in all_paths:
                all_paths.append(str(Path(t).parent).lower())
        # print(all_paths)
        #return all_paths
        self.tagged_paths = all_paths

    def lessThan(self, source_left: QModelIndex, source_right: QModelIndex):
        assert source_left.column() == source_right.column()
        # if source_left.column() == 3:
        #     print(QDateTime.fromString(source_left.data(),"dd.MM.yy hh:mm"))
            # print(type(source_left.data()))
        file_info1 = self.sourceModel().fileInfo(source_left)
        file_info2 = self.sourceModel().fileInfo(source_right)

        # return QFileSystemModel.lessThan(self.mapToSource(source_left), self.mapToSource(source_right))

        #print(self.sourceModel() )
        
        if file_info1.fileName() == "..":
            return self.sortOrder() == Qt.SortOrder.AscendingOrder

        if file_info2.fileName() == "..":
            return self.sortOrder() == Qt.SortOrder.DescendingOrder

        # size
        if source_left.column() == 1:
            return self.sourceModel().size(source_left) < self.sourceModel().size(source_right)

        # date
        if source_left.column() == 3: # and source_right.column() == 3:
            return self.sourceModel().lastModified(source_left).__le__(self.sourceModel().lastModified(source_right))

        if (file_info1.isDir() and file_info2.isDir()) or (file_info1.isFile() and file_info2.isFile()):
            return super().lessThan(source_left, source_right)

        return file_info1.isDir() and self.sortOrder() == Qt.SortOrder.AscendingOrder

    def filterAcceptsRow(self, source_row, source_parent):
        # print(self.mode)
        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        path = index.data(QFileSystemModel.FilePathRole)

        if self.mode == "Tag(s)": # and source_parent == source_model.index(source_model.rootPath()):
            # print(normpath(path))
            return normpath(path).lower() in self.tagged_paths
        elif self.mode == "Folder & tags" and source_parent == source_model.index(source_model.rootPath()):
            source_model = self.sourceModel()
            index = source_model.index(source_row, 0, source_parent)
            path = index.data(QFileSystemModel.FilePathRole)
            return normpath(path).lower() in self.tagged_paths
        elif self.mode == "Folder (untagged)" and source_parent == source_model.index(source_model.rootPath()):
            source_model = self.sourceModel()
            index = source_model.index(source_row, 0, source_parent)
            path = index.data(QFileSystemModel.FilePathRole)
            return get_tags(normpath(path).lower()) == []
        else:
            return True

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

def millis_to_str(duration):
    millis = int(duration)
    seconds=(millis/1000)%60
    seconds = str(int(seconds))
    if len(seconds) == 1:
        seconds = "0"+seconds
    minutes=(millis/(1000*60))%60
    minutes = str(int(minutes))
    # if len(minutes) == 1:
    #     minutes = "0"+minutes    
    hours=str(int((millis/(1000*60*60))%24))
    return (hours+":" if hours != "0" else "")+minutes+":"+seconds

def main():
    app = QApplication(sys.argv)
    #QApplication.setQuitOnLastWindowClosed(False)

    window = TaggerWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()