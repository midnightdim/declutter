from os import mkdir
import sys, subprocess
from PySide2.QtGui import QIcon, QColor, QCursor, QStandardItemModel
from PySide2.QtWidgets import QWidget, QApplication, QMainWindow, QFileSystemModel, QFileIconProvider, QMenu, QAbstractItemView, QAction, QFrame, QLineEdit, QMessageBox
from PySide2.QtWidgets import QWidgetAction, QHBoxLayout, QLabel, QCheckBox, QFileDialog, QAbstractSlider, QComboBox, QInputDialog
from PySide2.QtCore import QDir, Qt, QModelIndex, QSortFilterProxyModel, QUrl, QRect, QSize, QEvent, QMimeData, QUrl, QMimeDatabase
from PySide2.QtMultimedia import QMediaPlayer, QMediaPlaylist
from PySide2.QtMultimediaWidgets import QVideoWidget
from ui_tagger_window import Ui_taggerWindow
from tags_dialog import TagsDialog, generate_tag_model
from declutter_lib import *
from os.path import normpath
from pathlib import Path
from send2trash import send2trash
# from datetime import datetime
from file_system_model_lite import FileSystemModelLite
from condition_dialog import ConditionDialog
# from qt_material import apply_stylesheet

class TaggerWindow(QMainWindow):
    def __init__(self, parent = None):
        super(TaggerWindow, self).__init__(parent)
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
        # self.filter_tags_checkboxes = {}
        self.prev_indexes = []

        self.ui.menuView.addAction(self.ui.tagsDockWidget.toggleViewAction())
        self.ui.menuView.addAction(self.ui.mediaDockWidget.toggleViewAction())
        self.ui.menuView.addAction(self.ui.filtersDockWidget.toggleViewAction())        
        # self.ui.menuView.addAction(self.ui.tagsFilterDockWidget.toggleViewAction())        
        self.ui.tagsFilterDockWidget.hide()
        self.ui.filterAddButton.clicked.connect(self.add_condition)
        self.ui.filterAddButton.sizeHint()
        self.ui.filterRemoveButton.clicked.connect(self.delete_condition)
        self.ui.filterClearButton.clicked.connect(self.clear_conditions)
        self.ui.filterConditionSwitchCombo.currentIndexChanged.connect(self.update_treeview)
        self.ui.conditionListWidget.itemDoubleClicked.connect(self.edit_condition)

        self.ui.treeView.header().resizeSection(0,350)
        self.ui.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # self.ui.treeView.selectionModel().selectionChanged.connect(self.update_status)

        self.ui.treeView.doubleClicked.connect(self.open)
        self.ui.actionManage_Tags.triggered.connect(self.manage_tags)
        self.ui.actionNew_tagger_window.triggered.connect(self.new_window)

        self.ui.pathEdit.returnPressed.connect(self.change_path)
        self.ui.browseButton.clicked.connect(self.choose_path)
        self.ui.sourceComboBox.currentIndexChanged.connect(self.update_ui)
        # self.ui.selectTagsButton.clicked.connect(self.select_tags)

        self.ui.tagsFilterCombo.currentIndexChanged.connect(self.update_filter_from_combo)
        self.ui.tagsFilterLabel.setVisible(False)
        # self.ui.tagsFilterLayout.setGeometry(QRect(0,0,0,0))
        self.populate() # TBD can't it be just a part of init()?

    def new_window(self): # TBD not sure if this is safe
        tagger = TaggerWindow(self)
        tagger.show()
        tagger.move(self.x()+30,self.y()+30)

    def update_treeview(self):
        # print('updating treeview')
        #print(self.sorting_model.filter_paths)
        # filter_tags=[]
        # for t in self.filter_tag_checkboxes:
        #     if self.filter_tag_checkboxes[t].isChecked():
        #         filter_tags.append(t)
        # # self.sorting_model.filter_tags = filter_tags
        # # self.sorting_model.filter_mode = self.ui.tagsFilterCombo.currentText()
        mode = self.ui.sourceComboBox.currentText()

        # self.sorting_model.mode = mode
        # self.player.stop()
        # self.playlist.clear()
        self.rule['condition_switch'] = self.ui.filterConditionSwitchCombo.currentText()        
        if mode == 'Tagged': 
            # all_paths = []  # TBD this could be a function (used here and in sortingmodel)
            # if self.ui.tagsFilterCombo.currentText() == 'any tags':
            #     all_paths = get_all_files_from_db() # TBD rename these functions
            # elif self.ui.tagsFilterCombo.currentText() == 'any of':
            #     for t in filter_tags:
            #         all_paths = list(set(all_paths + get_files_by_tag(t)))
            # elif self.ui.tagsFilterCombo.currentText() == 'all of':
            #     all_paths = get_files_by_tags(filter_tags)                

            self.rule['folders'] = [ALL_TAGGED_TEXT]
            # print(all_paths)
            self.sorting_model = None
            self.model = FileSystemModelLite(get_files_affected_by_rule(self.rule, True), self)
            self.model.sort(0)
            # self.ui.treeView.destroy()
            # self.ui.treeView.setVisible(False)
            # self.ui.treeView = QTreeView()
            self.ui.treeView.setModel(self.model)

            # self.ui.verticalLayout_2.takeAt(1)
            # self.ui.verticalLayout_2.addWidget(self.ui.treeView)
            # self.ui.treeView.header().resizeSection(0,350)

            # self.model.data_loaded.connect(self.dir_loaded)
            # self.ui.treeView.setSortingEnabled(False)
            # self.ui.treeView.setDragEnabled(True)
            # self.ui.treeView.setDragDropMode(QAbstractItemView.DragDrop)
            self.ui.treeView.setSortingEnabled(True)            
            self.ui.treeView.expandAll()
            self.ui.treeView.selectionModel().selectionChanged.connect(self.update_status)         
            # print(self.ui.treeView.model())
            # print('model set')

        else:
            # print('not tags')        
            self.model = TagFSModel()
            # self.model = QFileSystemModel()
            self.model.setReadOnly(False)
            path = self.settings['current_folder'] if 'current_folder' in self.settings.keys() and self.settings['current_folder'] != '' else normpath(QDir.homePath())          
            self.model.setRootPath(path)
            self.model.setFilter(QDir.NoDot | QDir.AllEntries | QDir.Hidden)
            self.model.sort(0,Qt.SortOrder.AscendingOrder)          
            self.sorting_model = SortingModel(self)
            # self.sorting_model.mode = mode
            # self.sorting_model.filter_mode = self.ui.tagsFilterCombo.currentText()
            # self.sorting_model.filter_tags = filter_tags

            # self.sorting_model.rule = self.rule
            # self.sorting_model.recalc_tagged_paths()
            # print(self.rule)           
            # print(self.sorting_model.filter_tags)
            # print(self.sorting_model.tagged_paths)
            self.sorting_model.setSourceModel(self.model)   
            self.sorting_model.setSortCaseSensitivity(Qt.CaseInsensitive)
            # self.sorting_model.setSortLocaleAware(True)

            # self.rule['folders'] = [normpath(self.model.filePath(self.sorting_model.mapToSource(self.ui.treeView.rootIndex())))]            
            self.rule['folders'] = [normpath(self.ui.pathEdit.text())]            
            self.sorting_model.recalc_filtered_paths(self.rule)
            
            self.ui.treeView.setModel(self.sorting_model)
            # self.ui.treeView.setModel(self.model)
            self.ui.treeView.setRootIndex(self.sorting_model.mapFromSource(self.model.index(path)))
            # self.ui.treeView.setRootIndex(self.model.index(path))
            # self.ui.treeView.header().resizeSection(0,350)
            self.model.fileRenamed.connect(self.tag_renamed_file)
            self.model.setIconProvider(QFileIconProvider())
            self.ui.treeView.header().setSortIndicator(0, Qt.AscendingOrder)
            self.ui.treeView.setSortingEnabled(True)
            self.ui.treeView.setItemsExpandable(False)
            self.ui.treeView.setRootIsDecorated(False)
            self.ui.treeView.selectionModel().selectionChanged.connect(self.update_status)
            self.ui.treeView.setDragDropMode(QAbstractItemView.DragDrop) # TBD this is duplicated in __init__, not good
            self.ui.treeView.setAcceptDrops(True)
            self.ui.treeView.setDefaultDropAction(Qt.MoveAction)
            # print('drop action set to',self.ui.treeView.defaultDropAction())
            # print(self.ui.treeView.acceptDrops())

    def tag_renamed_file(self, path, oldName, newName):
        set_tags(os.path.join(path,newName),get_tags(os.path.join(path,oldName)))
        remove_all_tags(os.path.join(path,oldName))

##### BEGIN CONDITION SECTION
    def add_condition(self):  
        self.condition_window = ConditionDialog()
        self.condition_window.exec_()
        # if not 'conditions' in self.rule.keys():
        #     self.rule['conditions'] = []
        if self.condition_window.condition:
            self.rule['conditions'].append(self.condition_window.condition)
            self.refresh_conditions()
        # print(self.rule['conditions'])
        #print(self.condition_window.condition)

    def edit_condition(self, cond):
        self.condition_window = ConditionDialog()
        self.condition_window.loadCondition(self.rule['conditions'][self.ui.conditionListWidget.indexFromItem(cond).row()])
        self.condition_window.exec_()
        self.refresh_conditions()        

    def delete_condition(self): # same as in rule_edit_window.py
        del self.rule['conditions'][self.ui.conditionListWidget.selectedIndexes()[0].row()]
        self.refresh_conditions()

    def clear_conditions(self):
        self.rule['conditions'] = []
        self.refresh_conditions()

    def refresh_conditions(self): # same as in rule_edit_window.py
        conds = []

        for c in self.rule['conditions']:
            if c['type'] == 'tags' and c['tag_switch'] != 'tags in group':
                conds.append('Has ' + c['tag_switch'] + (' of these tags: ' + ', '.join(c['tags']) if c['tag_switch'] not in ('no tags','any tags') else ''))
            elif c['type'] == 'tags' and c['tag_switch'] == 'tags in group':
                conds.append('Has tags in group: '+c['tag_group'] )
            elif c['type'] == 'date':
                conds.append('Age is ' + c['age_switch'] + ' ' + str(c['age']) + ' ' + c['age_units'])      
            elif c['type'] == 'name':
                if not 'name_switch' in c.keys():
                    c['name_switch'] = 'matches'
                conds.append('Name ' + c['name_switch'] + ' ' + str(c['filemask']))
            elif c['type'] == 'size':
                conds.append('File size is ' + c['size_switch'] + ' ' + str(c['size']) + c['size_units'] )
            elif c['type'] == 'type':
                conds.append('File type ' + c['file_type_switch'] + ' ' + c['file_type'])

        self.ui.conditionListWidget.clear()
        self.ui.conditionListWidget.addItems(conds)
        self.update_treeview()
##### END CONDITION SECTION

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
        # return super(TaggerWindow, self).eventFilter(source, event)
        # print(source,event,event.type())
        if source == self.ui.treeView:
            # print(event,event.type())
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_F2:
                    self.player.stop()
                    self.playlist.clear()
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
                            remove_all_tags(os.path.normpath(self.model.filePath(self.sorting_model.mapToSource(index)) if self.sorting_model else self.model.filePath(index)))
                        self.ui.statusbar.showMessage(str(len(indexes))+" item(s) deleted")
                    else:
                        for index in indexes: #TBD add try/except here
                            send2trash(os.path.normpath(self.model.filePath(self.sorting_model.mapToSource(index)) if self.sorting_model else self.model.filePath(index)))
                            remove_all_tags(os.path.normpath(self.model.filePath(self.sorting_model.mapToSource(index)) if self.sorting_model else self.model.filePath(index)))
                        self.ui.statusbar.showMessage(str(len(indexes))+" item(s) sent to trash")                
                elif event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
                    indexes = self.ui.treeView.selectionModel().selectedRows()
                    urls = [QUrl(self.model.filePath(self.sorting_model.mapToSource(index)) if self.sorting_model else self.model.filePath(index)) for index in indexes]
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
        # elif source in self.tag_combos:
        #     print('combo event')
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

##### Begin Media Player section
    def media_update_play_button(self,state):
        icon1 = QIcon()
        icon1.addFile(u":/images/icons/media-pause.svg" if state == QMediaPlayer.State.PlayingState else u":/images/icons/media-play.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.ui.mediaPlayButton.setIcon(icon1)

    def play_media(self):
        file_url = QUrl.fromLocalFile(self.model.filePath(self.sorting_model.mapToSource(self.ui.treeView.currentIndex()))) if self.sorting_model else QUrl.fromLocalFile(self.model.filePath(self.ui.treeView.currentIndex()))
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
        self.settings = load_settings()
        self.checkAction = {}  # checkboxes in context menu
        self.tag_checkboxes = {} # checkboxes in tag dock widget
        self.tag_combos = {} # comboboxes in tag dock widget
        self.filter_tag_checkboxes = {} # checkboxes in tag filter dock widget
        self.rule = {'recursive':False, 'action': 'Filter', 'conditions':[]} # filter rule
        self.tag_model = QStandardItemModel()
        generate_tag_model(self.tag_model, get_tags_and_groups())

        self.ui.actionNone1 = QAction(self)
        self.ui.recent_menu.aboutToShow.connect(self.update_recent_menu)
        self.ui.recent_menu.triggered.connect(self.open_file_from_recent)
        #self.ui.menuRecent_folders.addAction(self.ui.actionNone1)
        #self.actionNone.setEnabled(False)

        path = self.settings['current_folder'] if 'current_folder' in self.settings.keys() and self.settings['current_folder'] != '' else normpath(QDir.homePath())
        
        self.model = TagFSModel()
        # self.model = QFileSystemModel()
        self.model.setRootPath(path)
        self.model.setReadOnly(False)
        self.model.setFilter(QDir.NoDot | QDir.AllEntries | QDir.Hidden)
        self.model.sort(0,Qt.SortOrder.AscendingOrder)

        self.sorting_model = SortingModel()
        self.sorting_model.mode = "Folder"
        #self.sorting_model.filter_paths = []
        self.sorting_model.setSourceModel(self.model) # TBD maybe this is not needed, model gets added later anyway

        self.ui.pathEdit.setText(path)

        self.ui.treeView.setModel(self.sorting_model)
        # self.ui.treeView.setModel(self.model)

        self.ui.treeView.setRootIndex(self.sorting_model.mapFromSource(self.model.index(path)))
        self.ui.treeView.header().resizeSection(0,350)
        # self.ui.treeView.setRootIndex(self.model.index(path))
        # self.model.setIconProvider(QFileIconProvider())
        # self.model.directoryLoaded.connect(self.dir_loaded)
              
        # self.ui.treeView.installEventFilter(self)
        # self.setStyleSheet("QDockWidget::title {position: relative; top: 100px;}")
        # self.setStyleSheet("QMainWindow::separator{ margin: 100px;}");    
        self.init_tag_checkboxes()
        # self.init_filter_checkboxes()
        self.update_ui()

    # def test(self, state):
    #     print('test')
    #     print(self.sender().checkState())
    #     print(state)

    # def test2(self):
    #     print('test2')
    #     print(self.sender().checkState())

    # TBD This opens manage tags dialog on double click on tags layout, but it's unstable, so commenting it out
    # def mouseDoubleClickEvent(self, event):
    #     widget = self.childAt(event.pos())
    #     if widget is not None and widget.objectName() == "scrollAreaWidgetContents":
    #         self.manage_tags()

##### BEGIN TAG FILTER SECTION (OBSOLETE!) TBD
    def init_filter_checkboxes(self):
        # removing all filter tag checkboxes
        while True:
            if self.ui.tagsFilterLayout.itemAt(0):
                self.ui.tagsFilterLayout.itemAt(0).widget().deleteLater()       
            if not self.ui.tagsFilterLayout.takeAt(0):
                break

        # creating filter tag checkboxes from tag model
        for i in range(self.tag_model.rowCount()):
            group = self.tag_model.item(i).data(Qt.UserRole)
            if group['name_shown']:
                group_widget = QLabel('<b>'+group['name']+'</b>')
                group_widget.setVisible(False)
                self.ui.tagsFilterLayout.addWidget(group_widget)
            for k in range(self.tag_model.item(i).rowCount()):
                tag = self.tag_model.item(i).child(k).data(Qt.UserRole)
                self.filter_tag_checkboxes[tag['name']] = QCheckBox(tag['name'])
                self.filter_tag_checkboxes[tag['name']].setVisible(False)
                self.ui.tagsFilterLayout.addWidget(self.filter_tag_checkboxes[tag['name']])
                # self.filter_tag_checkboxes[tag['name']].clicked.connect(self.set_filter_tags)
                self.filter_tag_checkboxes[tag['name']].stateChanged.connect(self.update_treeview_filters)
                if tag['color']:
                    color = QColor()
                    color.setRgba(tag['color'])
                    # color.setAlpha(100)
                    self.filter_tag_checkboxes[tag['name']].setPalette(color)
                    self.filter_tag_checkboxes[tag['name']].setAutoFillBackground(True) 
            if i<self.tag_model.rowCount()-1:
                hline = QHLine()
                hline.setVisible(False)
                self.ui.tagsFilterLayout.addWidget(hline)

    def update_treeview_filters(self):
        if self.ui.tagsFilterCombo.currentText() not in ('any tags', 'no tags','-no filter-'):
            self.update_treeview()

    def update_filter_from_combo(self):
        self.ui.tagsFilterLabel.setVisible(self.ui.tagsFilterCombo.currentText() not in ('any tags', 'no tags','-no filter-'))
        if self.ui.tagsFilterCombo.currentText() in ('any tags', 'no tags','-no filter-'):
            i=0
            while self.ui.tagsFilterLayout.itemAt(i):
                self.ui.tagsFilterLayout.itemAt(i).widget().setVisible(False)
                i+=1
        else:
            i=0
            while self.ui.tagsFilterLayout.itemAt(i):
                self.ui.tagsFilterLayout.itemAt(i).widget().setVisible(True)
                i+=1

        self.update_treeview()
##### END TAG FILTER SECTION (OBSOLETE!) TBD

    def init_tag_checkboxes(self):
        # removing all tag checkboxes
        # print('init tag checkboxes called')
        while True:
            if self.ui.tagsLayout.itemAt(0):
                self.ui.tagsLayout.itemAt(0).widget().deleteLater()       
            if not self.ui.tagsLayout.takeAt(0):
                break

        # self.test_combo = QComboBox()
        # self.test_combo.addItems(('one','two','three'))
        # self.ui.tagsLayout.addWidget(self.test_combo)
        # self.test_combo.currentIndexChanged.connect(self.set_tags)

        for i in range(self.tag_model.rowCount()):
        # i = 0
        # for group in data.keys():
            group = self.tag_model.item(i).data(Qt.UserRole)
            if group['name_shown']:
                self.ui.tagsLayout.addWidget(QLabel('<b>'+group['name']+'</b>'))
            if group['widget_type'] == 0:
                for k in range(self.tag_model.item(i).rowCount()):
                    tag = self.tag_model.item(i).child(k).data(Qt.UserRole)
                    self.tag_checkboxes[tag['name']] = QCheckBox(tag['name'])
                    self.ui.tagsLayout.addWidget(self.tag_checkboxes[tag['name']])
                    # print('added widget for', tag['name'])
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
            elif group['widget_type'] == 1:
                self.tag_combos[group['id']] = QComboBox(self)
                self.tag_combos[group['id']].addItems([""]+[self.tag_model.item(i).child(k).data(Qt.UserRole)['name'] for k in range(self.tag_model.item(i).rowCount())])
                self.ui.tagsLayout.addWidget(self.tag_combos[group['id']])
                # print('added widget (combo) for ',group['id'])
                self.tag_combos[group['id']].currentIndexChanged.connect(self.set_tags)
            # if i<self.tag_model.rowCount()-1:
            #     self.ui.tagsLayout.addWidget(QHLine())
        
        # for i in range(self.ui.tagsLayout.count()):
        #     self.ui.tagsLayout.itemAt(i).widget().setVisible(True)
        #     print(self.ui.tagsLayout.itemAt(i).widget().isVisible())
            
        # print(self.ui.tagsLayout.children())
        # print(self.ui.tagsWidget.isVisible())
        # self.ui.scrollArea.widget().update()
        # self.ui.scrollArea.widget().repaint()
        # self.ui.scrollArea.ensureVisible(1,1)
        # self.ui.scrollArea.widget().setVisible(True)
        # print(self.ui.scrollArea.widget().size())
        self.ui.tagsScrollArea.setWidgetResizable(True)

    def update_tag_checkboxes(self):
        # print('update_tag_checkboxes called')
        indexes = self.ui.treeView.selectionModel().selectedRows()
        if self.sorting_model:
            cur_selection = [normpath(self.model.filePath(self.sorting_model.mapToSource(index))) for index in indexes] 
        else:
            cur_selection = [normpath(self.model.filePath(index)) for index in indexes]             

        all_files_tags_with_group_ids = []
        for f in cur_selection:  # TBD v3 not the most efficient procedure maybe: could be get_files_tags procedure
            all_files_tags_with_group_ids.extend(get_tags_by_group_ids(f))

        # print(all_files_tags)
        if all_files_tags_with_group_ids:
            all_files_tags, n = zip(*all_files_tags_with_group_ids)
        else:
            all_files_tags = []

        tree = {}
        for t in set(all_files_tags_with_group_ids):
            if t[1] not in tree.keys():
                tree[t[1]] = []
            tree[t[1]].append(t[0])

        # print(tree)

        for i in range(self.tag_model.rowCount()):
            group = self.tag_model.item(i).data(Qt.UserRole)
            if group['widget_type'] == 0:
                for t in get_all_tags_by_group_id(group['id']):
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
            elif group['widget_type'] == 1:
                # print(group['id'], type(group['id']))
                if group['id'] not in tree.keys():
                    self.tag_combos[group['id']].setCurrentText('')
                else:
                    self.tag_combos[group['id']].setCurrentText(tree[group['id']][0]) # TBD improve this!

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

    # def dir_loaded(self):
    #     print("dir loaded")
    #     if self.ui.sourceComboBox.currentText() == "Tagged":
    #         self.ui.treeView.expandAll()

    # def apply_filter_tags(self):
          
    #     all_tags=[]
    #     for t in self.filter_tags_checkboxes:
    #         if self.filter_tags_checkboxes[t].isChecked():
    #             all_tags.append(t)
    #     self.sorting_model.filter_tags = all_tags
    #     self.update_treeview()

    # def select_tags(self):
    #     tags_dialog = QDialog()
    #     tags_dialog.setWindowTitle("Select Tags")
    #     tags_dialog.setMinimumHeight(400)
    #     treeView = QTreeView(tags_dialog)
    #     treeView.setModel(self.tag_model)

    #     treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
    #     treeView.setHeaderHidden(True)
    #     treeView.expandAll()
    #     layout = QVBoxLayout(tags_dialog)
    #     layout.addWidget(treeView)        
    #     buttonBox = QDialogButtonBox(tags_dialog)
    #     buttonBox.setObjectName(u"buttonBox")
    #     buttonBox.setOrientation(Qt.Horizontal)
    #     buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    #     buttonBox.accepted.connect(tags_dialog.accept)
    #     buttonBox.rejected.connect(tags_dialog.reject)

    #     layout.addWidget(buttonBox)

    #     tags_dialog.setLayout(layout)
    #     tags_dialog.treeView = treeView
        
    #     tags_dialog.setWindowIcon(QIcon('DeClutter.ico'))
        
    #     if tags_dialog.exec_():
    #         self.filter_tags = [t.data() for t in tags_dialog.treeView.selectedIndexes()]
    #         self.update_filter_tags()

    def update_ui(self):
        mode = self.ui.sourceComboBox.currentText()
        #self.sorting_model.mode = mode
        # print('mode',self.sorting_model.mode)
        # self.ui.selectTagsButton.setVisible(mode in ('Folder & tags', 'Tag(s)'))
        self.ui.pathEdit.setEnabled(mode == 'Folder') # TBD update this to 'Folder'
        self.ui.browseButton.setEnabled(mode == 'Folder')
        self.ui.tagsFilterCombo.clear()
        if mode == 'Tagged':
            self.ui.tagsFilterCombo.addItems(('any tags','any of', 'all of'))
        elif mode == 'Folder':
            self.ui.tagsFilterCombo.addItems(('-no filter-','any tags','any of', 'all of','none of','no tags'))

        self.update_treeview()

    def update_status(self):
        # print('update status')
        indexes = self.ui.treeView.selectionModel().selectedRows()
        # indexes = self.ui.treeView.selectedIndexes()
        indexes.sort()
        self.prev_indexes.sort()
        if indexes != self.prev_indexes:
            # print('selection changed')
            self.player.stop()
            path = self.model.filePath(self.sorting_model.mapToSource(self.ui.treeView.currentIndex())) if self.sorting_model else self.model.filePath(self.ui.treeView.currentIndex())
            ftype = get_file_type(path)
            if os.path.isfile(path) and ftype in ('Audio','Video','Image'):
                # print(self.model.filePath(self.sorting_model.mapToSource(self.ui.treeView.currentIndex())))
                file_url = QUrl.fromLocalFile(self.model.filePath(self.sorting_model.mapToSource(self.ui.treeView.currentIndex()))) if self.sorting_model else QUrl.fromLocalFile(self.model.filePath(self.ui.treeView.currentIndex()))
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
            # self.ui.pathEdit.setText(file_path)
            self.ui.pathEdit.setText(normpath(self.model.filePath(self.sorting_model.mapToSource(self.ui.treeView.rootIndex()))))
            # print(self.model.filePath(self.model.rootPath()))
            # print(self.model.rootDirectory())
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
        clear_tags_cache()
        self.init_tag_checkboxes()
        # self.init_filter_checkboxes()
        self.update_tag_checkboxes()

    def open(self):
        index = self.ui.treeView.currentIndex()
        # print(index.data(Qt.UserRole))
        # print(self.sorting_model.mapToSource(index).data())
        #file_path = normpath(self.model.filePath(index))
        if self.sorting_model:
            file_path = normpath(self.model.filePath(self.sorting_model.mapToSource(index)))
        else:
            file_path = normpath(self.model.filePath(index))
        if os.path.isdir(file_path):
            self.ui.statusbar.clearMessage()
            self.model.setRootPath(normpath(file_path)) # TBD reuse this in a function
            if self.sorting_model:
                self.ui.treeView.setRootIndex(self.sorting_model.mapFromSource(self.model.index(file_path)))
            self.ui.pathEdit.setText(file_path)
            self.settings['current_folder'] = file_path
            save_settings(SETTINGS_FILE,self.settings)
        elif os.path.isfile(file_path):
            open_file(file_path)

    def create_folder(self):
        folder, ok = QInputDialog.getText(self, "Create new folder",
                "Enter folder name:", QLineEdit.Normal)
        if ok and folder != '':
            index = self.ui.treeView.currentIndex()
            # TBD this works a bit unexpectedly in "Tagged" mode - it creates a folder inside the parent folder, not the selected folder
            if self.sorting_model:
                full_path = Path(self.model.filePath(self.sorting_model.mapToSource(index))).parent / folder
            else:
                full_path = Path(self.model.filePath(index)).parent / folder
            # full_path = Path(file_path).parent / folder
            try:
                os.mkdir(full_path)
            except Exception as e:
                QMessageBox.critical(self,"Error","Can't create this folder",QMessageBox.Ok)

    def context_menu(self, position):
        #index = self.ui.treeView.currentIndex()
        indexes = self.ui.treeView.selectionModel().selectedRows()
        if self.sorting_model:
            cur_selection = [normpath(self.model.filePath(self.sorting_model.mapToSource(index))) for index in indexes] 
        else:
            cur_selection = [normpath(self.model.filePath(index)) for index in indexes]        

        all_files_tags = []
        for f in cur_selection:  # TBD v3 not the most efficient procedure maybe
            all_files_tags.extend(get_tags(f))

        menu = QMenu()
        
        createFolderAct = QAction("&Create folder", self)
        # createFolderAct.setShortcuts(QKeySequence.Open)
        createFolderAct.setStatusTip("Create a new folder")
        createFolderAct.triggered.connect(self.create_folder)
        menu.addAction(createFolderAct)      

        self.checkAction = {}

        # # adding tag checkboxes
        # for i in range(self.tag_model.rowCount()):
        #     group = self.tag_model.item(i).data(Qt.UserRole)
        #     if group['name_shown']:
        #         menu.addAction(group['name'])
        #         # self.ui.tagsLayout.addWidget(QLabel('<b>'+group['name']+'</b>'))
        #     for k in range(self.tag_model.item(i).rowCount()):
        #         tag = self.tag_model.item(i).child(k).data(Qt.UserRole)  
        #         t = tag['name']              
        #         self.checkAction[t] = CheckBoxAction(self,t)
        #         self.checkAction[t].checkbox.clicked.connect(self.set_tags)
        #         if t not in all_files_tags:
        #             pass
        #             #window[r].update(text = CHAR_UNCHECKED + " " + r)
        #         elif all_files_tags.count(t) < len(cur_selection):
        #             self.checkAction[t].checkbox.setTristate(True)
        #             if self.checkAction[t].checkbox.checkState() is not Qt.CheckState.PartiallyChecked:
        #                 self.checkAction[t].checkbox.setCheckState(Qt.CheckState.PartiallyChecked)
        #         else:
        #             if self.checkAction[t].checkbox.checkState() is not Qt.CheckState.Checked:
        #                 self.checkAction[t].checkbox.setChecked(True)

        #         menu.addAction(self.checkAction[t])

        cursor = QCursor()
        menu.exec_(cursor.pos())

    def set_tags(self, state):
        # print('set_tags called')
        sender = self.sender()
        # print(sender)
        # if type(sender) == QCheckBox:
        #     print('checkbox')
        # print("clicked",state)
        # index = self.ui.treeView.currentIndex()
        # file_path = normpath(self.model.filePath(self.sorting_model.mapToSource(index)))      
        
        indexes = self.ui.treeView.selectionModel().selectedRows()

        # for index in indexes:
        #     print(index)

        # print(indexes)
        if self.sorting_model:
            cur_selection = [normpath(self.model.filePath(self.sorting_model.mapToSource(index))) for index in indexes]
        else:
            cur_selection = [normpath(self.model.filePath(index)) for index in indexes]
        # print(cur_selection)

        if type(sender) == QCheckBox:
            for file_path in cur_selection:
                if state: #checked - it was 2 when used with stateChanged
                    add_tag(file_path,sender.text())
                elif not state: #unchecked - it was 0 when used with stateChanged
                    remove_tag(file_path,sender.text())
        elif type(sender) == QComboBox:
            for file_path in cur_selection:
                if sender.currentText() == '':
                    remove_tags(file_path,[sender.itemText(i) for i in range(sender.count()) if sender.itemText(i) != ''])
                else:
                    remove_tags(file_path,[sender.itemText(i) for i in range(sender.count()) if sender.itemText(i) != '']) # TBD maybe optimize this
                    add_tag(file_path, sender.currentText())
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
        return Qt.MoveAction | Qt.CopyAction # | super(TagFSModel, self).supportedDropActions()         

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

        tags = get_tags(normpath(self.filePath(index))) if role in (Qt.DisplayRole, Qt.BackgroundRole) else []
        # print(tags)
        if index.column() == self.columnCount() - 1:
            if role == Qt.DisplayRole:
                #return self.fileName(index)
                return ', '.join(tags)
            # if role == Qt.TextAlignmentRole:
            #     return Qt.AlignLeft
        if role == Qt.BackgroundRole and tags and tag_get_color(tags[0]):
            #return QColor("#ccffff")
            color = QColor()
            color.setRgba(tag_get_color(tags[0]))
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
        # self.mode = ""
        # self.filter_tags = []
        # self.filter_mode = '-no filter-'
        # self.tagged_paths = []
        self.filtered_paths = []
        self.filter_enabled = False
        # self.rule = {}

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

    def recalc_filtered_paths(self, rule):
        # print(rule)
        if 'conditions' in rule.keys() and rule['conditions']:
            self.filtered_paths = get_files_affected_by_rule(rule)
            self.filter_enabled = True
        else:
            self.filter_enabled = False
        # print(self.filtered_paths)
        # print(self.filtered_paths)

    # def recalc_tagged_paths(self):
    #     # print('tagged_paths called',datetime.now())
    #     all_paths=[]
    #     # print('here')
    #     # print(self.filter_tags)
    #     # print(self.filter_mode)
    #     if self.filter_mode in ('any of', 'none of'):
    #         for t in self.filter_tags:
    #             all_paths = list(set(all_paths + get_files_by_tag(t)))
    #     elif self.filter_mode == 'all of':
    #         all_paths = get_files_by_tags(self.filter_tags)  # TBD this could be simplified by passing True as second parameter, but this could slow down filtering

        # print(all_paths)
        # if not tree:
        #     self.tagged_paths = all_paths
        #     return
        # for t in all_paths:
        #     if str(Path(t).parent).lower() not in all_paths:
        #         all_paths.append(str(Path(t).parent).lower())
        # print(all_paths)
        #return all_paths
        # self.tagged_paths = all_paths
        # print('tagged_paths done',datetime.now())

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
        if source_left.column() == 3: 
            return self.sourceModel().lastModified(source_left).__le__(self.sourceModel().lastModified(source_right))

        if (file_info1.isDir() and file_info2.isDir()) or (file_info1.isFile() and file_info2.isFile()):
            return super().lessThan(source_left, source_right)

        return file_info1.isDir() and self.sortOrder() == Qt.SortOrder.AscendingOrder

    def filterAcceptsRow(self, source_row, source_parent):
        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        path = index.data(QFileSystemModel.FilePathRole)

        # if self.mode == "Tagged": # TBD this is obsolete
        #     # print(normpath(path))
        #     if self.filter_mode in ('any of','all of'):
        #         return normpath(path) in self.tagged_paths
        #     elif self.filter_mode == 'any tags':
        #         return len(get_tags(normpath(path)))>0
        #     else:
        #         return False                
        # elif self.mode == "Folder":
        #     # print('here')
        #     if self.filter_mode in ('any of','all of') and source_parent == source_model.index(source_model.rootPath()):
        #         source_model = self.sourceModel()
        #         index = source_model.index(source_row, 0, source_parent)
        #         path = index.data(QFileSystemModel.FilePathRole)
        #         # return normpath(path).lower() in self.tagged_paths
        #         return normpath(path) in self.tagged_paths
        #     elif self.filter_mode == 'none of' and source_parent == source_model.index(source_model.rootPath()):
        #         source_model = self.sourceModel()
        #         index = source_model.index(source_row, 0, source_parent)
        #         path = index.data(QFileSystemModel.FilePathRole)
        #         return normpath(path) not in self.tagged_paths
        #     elif self.filter_mode == 'no tags' and source_parent == source_model.index(source_model.rootPath()):
        #         source_model = self.sourceModel()
        #         index = source_model.index(source_row, 0, source_parent)
        #         path = index.data(QFileSystemModel.FilePathRole)
        #         return get_tags(normpath(path)) == []
        #     elif self.filter_mode == 'any tags' and source_parent == source_model.index(source_model.rootPath()):
        #         source_model = self.sourceModel()
        #         index = source_model.index(source_row, 0, source_parent)
        #         path = index.data(QFileSystemModel.FilePathRole)
        #         return len(get_tags(normpath(path)))>0
        #     else:
        #         return True
        if source_parent == source_model.index(source_model.rootPath()) and self.filter_enabled:
            source_model = self.sourceModel()
            index = source_model.index(source_row, 0, source_parent)
            path = index.data(QFileSystemModel.FilePathRole)
            return normpath(path) in self.filtered_paths            
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

def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])

def main():
    app = QApplication(sys.argv)
    #QApplication.setQuitOnLastWindowClosed(False)
    
    # can be used with qt_material
    # apply_stylesheet(app, theme='light_purple.xml', invert_secondary=True)
    window = TaggerWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()