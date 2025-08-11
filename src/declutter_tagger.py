import os
import sys
import subprocess
from os.path import normpath, isfile, isdir
from pathlib import Path
from send2trash import send2trash
from PySide6.QtGui import QIcon, QColor, QCursor, QStandardItemModel, QAction
from PySide6.QtWidgets import (
    QWidget, QApplication, QMainWindow, QFileSystemModel, QFileIconProvider, QMenu, QAbstractItemView, QFrame, QLineEdit, QMessageBox,
    QWidgetAction, QHBoxLayout, QLabel, QCheckBox, QFileDialog, QComboBox, QInputDialog
)
from PySide6.QtCore import (
    QDir, Qt, QModelIndex, QSortFilterProxyModel, QUrl, QRect, QSize, QEvent, QMimeData, QMimeDatabase
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from src.ui.ui_tagger_window import Ui_taggerWindow
from src.tags_dialog import TagsDialog, generate_tag_model
from declutter.config import (SETTINGS_FILE, ALL_TAGGED_TEXT)
from declutter.store import load_settings, save_settings
from declutter.rules import get_files_affected_by_rule
from declutter.tags import (
    tag_get_color, set_tags, get_tags, get_tags_by_group_ids, add_tag, remove_tags, remove_all_tags, 
    clear_tags_cache, get_all_tags_by_group_id, remove_tag, get_tags_and_groups
)
from declutter.file_utils import (
    get_file_type
)

from src.file_system_model_lite import FileSystemModelLite
from src.condition_dialog import ConditionDialog


class TaggerWindow(QMainWindow):
    def __init__(self, parent=None):
        super(TaggerWindow, self).__init__(parent)
        self.ui = Ui_taggerWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(":/images/icons/DeClutter.ico"))
        self.player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self.player.setAudioOutput(self._audio_output)

        self.videoWidget = QVideoWidget()
        self.ui.playerLayout.addWidget(self.videoWidget)
        self.player.setVideoOutput(self.videoWidget)
        
        # Connect media player signals to slots
        self.ui.mediaVolumeDial.valueChanged.connect(lambda v: self._audio_output.setVolume(v / 100.0))
        self.ui.mediaPlayButton.clicked.connect(self.play_media)
        self.player.durationChanged.connect(self.change_duration)
        self.player.positionChanged.connect(self.change_position)
        self.player.playbackStateChanged.connect(self.media_update_play_button)
        self.ui.mediaPositionSlider.actionTriggered.connect(self.action_trig)

        self.ui.mediaDockWidget.installEventFilter(self)
        self.ui.treeView.installEventFilter(self)

        self.ui.treeView.setDragDropMode(QAbstractItemView.DragDrop)
        self.ui.treeView.setAcceptDrops(True)
        self.ui.treeView.setDefaultDropAction(Qt.MoveAction)
        self.ui.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.treeView.customContextMenuRequested.connect(self.context_menu)
        self.filter_tags = []
        self.prev_indexes = []

        # Add dock widget toggle actions to the View menu
        self.ui.menuView.addAction(self.ui.tagsDockWidget.toggleViewAction())
        self.ui.menuView.addAction(self.ui.mediaDockWidget.toggleViewAction())
        self.ui.menuView.addAction(self.ui.filtersDockWidget.toggleViewAction())
        self.ui.filterAddButton.clicked.connect(self.add_condition)
        self.ui.filterAddButton.sizeHint()
        self.ui.filterRemoveButton.clicked.connect(self.delete_condition)
        self.ui.filterClearButton.clicked.connect(self.clear_conditions)
        self.ui.filterConditionSwitchCombo.currentIndexChanged.connect(
            self.update_treeview)
        self.ui.conditionListWidget.itemDoubleClicked.connect(
            self.edit_condition)

        # Configure tree view header and selection
        self.ui.treeView.header().resizeSection(0, 350)
        self.ui.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # TBD: self.ui.treeView.selectionModel().selectionChanged.connect(self.update_status) - check if this is needed

        # Connect actions for opening files, managing tags, and new windows
        self.ui.treeView.doubleClicked.connect(self.open)
        self.ui.actionManage_Tags.triggered.connect(self.manage_tags)
        self.ui.actionNew_tagger_window.triggered.connect(self.new_window)

        # Connect path editing and browsing actions
        self.ui.pathEdit.returnPressed.connect(self.change_path)
        self.ui.browseButton.clicked.connect(self.choose_path)
        self.ui.sourceComboBox.currentIndexChanged.connect(self.update_ui)
        
        # Populate initial UI elements
        self.populate()  # TBD can't it be just a part of init()?

    def new_window(self):
        """Opens a new TaggerWindow instance."""
        tagger = TaggerWindow(self)
        tagger.show()
        tagger.move(self.x()+30, self.y()+30)

    def update_treeview(self):
        """Updates the file tree view based on the selected source and filter conditions."""
        mode = self.ui.sourceComboBox.currentText()
        self.player.stop()
        self.rule['condition_switch'] = self.ui.filterConditionSwitchCombo.currentText()
        if mode == 'Tagged':
            self.rule['folders'] = [ALL_TAGGED_TEXT]
            self.sorting_model = None
            self.model = FileSystemModelLite(
                get_files_affected_by_rule(self.rule, True), self)
            self.model.sort(0)
            self.ui.treeView.setModel(self.model)
            self.ui.treeView.setSortingEnabled(True)
            self.ui.treeView.expandAll()
            self.ui.treeView.selectionModel().selectionChanged.connect(self.update_status)
        else:
            self.model = TagFSModel()
            self.model.setReadOnly(False)
            path = self.settings['current_folder'] if 'current_folder' in self.settings.keys(
            ) and self.settings['current_folder'] != '' else normpath(QDir.homePath())
            self.model.setRootPath(path)
            self.model.setFilter(QDir.NoDot | QDir.AllEntries | QDir.Hidden)
            self.model.sort(0, Qt.SortOrder.AscendingOrder)
            self.sorting_model = SortingModel(self)
            self.sorting_model.setSourceModel(self.model)
            self.sorting_model.setSortCaseSensitivity(Qt.CaseInsensitive)
            self.rule['folders'] = [normpath(self.ui.pathEdit.text())]
            self.sorting_model.recalc_filtered_paths(self.rule)
            self.ui.treeView.setModel(self.sorting_model)
            self.ui.treeView.setRootIndex(self.sorting_model.mapFromSource(self.model.index(path, 0)))
            self.model.fileRenamed.connect(self.tag_renamed_file)
            self.model.setIconProvider(QFileIconProvider())
            self.ui.treeView.header().setSortIndicator(0, Qt.AscendingOrder)
            self.ui.treeView.setSortingEnabled(True)
            self.ui.treeView.setItemsExpandable(False)
            self.ui.treeView.setRootIsDecorated(False)
            self.ui.treeView.selectionModel().selectionChanged.connect(self.update_status)
            self.ui.treeView.setDragDropMode(QAbstractItemView.DragDrop)
            self.ui.treeView.setAcceptDrops(True)
            self.ui.treeView.setDefaultDropAction(Qt.MoveAction)

    def tag_renamed_file(self, path, oldName, newName):
        """Updates tags when a file is renamed."""
        set_tags(os.path.join(path, newName),
                 get_tags(os.path.join(path, oldName)))
        remove_all_tags(os.path.join(path, oldName))

    def add_condition(self):
        """Opens a dialog to add a new condition to the rule."""
        self.condition_window = ConditionDialog()
        self.condition_window.exec()
        if self.condition_window.condition:
            self.rule['conditions'].append(self.condition_window.condition)
            self.refresh_conditions()

    def edit_condition(self, cond):
        """Opens a dialog to edit an existing condition."""
        self.condition_window = ConditionDialog()
        self.condition_window.loadCondition(
            self.rule['conditions'][self.ui.conditionListWidget.indexFromItem(cond).row()])
        self.condition_window.exec_()
        self.refresh_conditions()

    def delete_condition(self):
        """Deletes the selected condition from the rule."""
        del self.rule['conditions'][self.ui.conditionListWidget.selectedIndexes()[
            0].row()]
        self.refresh_conditions()

    def clear_conditions(self):
        """Clears all conditions from the rule."""
        self.rule['conditions'] = []
        self.refresh_conditions()

    def refresh_conditions(self):
        """Refreshes the list of conditions displayed in the UI."""
        conds = []

        for c in self.rule['conditions']:
            if c['type'] == 'tags' and c['tag_switch'] != 'tags in group':
                conds.append('Has ' + c['tag_switch'] + (' of these tags: ' + ', '.join(
                    c['tags']) if c['tag_switch'] not in ('no tags', 'any tags') else ''))
            elif c['type'] == 'tags' and c['tag_switch'] == 'tags in group':
                conds.append('Has tags in group: '+c['tag_group'])
            elif c['type'] == 'date':
                conds.append(
                    'Age is ' + c['age_switch'] + ' ' + str(c['age']) + ' ' + c['age_units'])
            elif c['type'] == 'name':
                if not 'name_switch' in c.keys():
                    c['name_switch'] = 'matches'
                conds.append(
                    'Name ' + c['name_switch'] + ' ' + str(c['filemask']))
            elif c['type'] == 'size':
                conds.append(
                    'File size is ' + c['size_switch'] + ' ' + str(c['size']) + c['size_units'])
            elif c['type'] == 'type':
                conds.append('File type ' +
                             c['file_type_switch'] + ' ' + c['file_type'])

        self.ui.conditionListWidget.clear()
        self.ui.conditionListWidget.addItems(conds)
        self.update_treeview()

    def closeEvent(self, event):
        """Stops media playback when the window is closed."""
        self.player.stop()

    def eventFilter(self, source, event):
        """Filters events for specific UI elements to handle custom interactions."""
        if source == self.ui.treeView:
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_F2:
                    self.player.stop()
                if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    if self.ui.treeView.state() is not QAbstractItemView.EditingState:
                        self.open()
                if event.key() == Qt.Key_Delete:
                    indexes = self.ui.treeView.selectionModel().selectedRows()
                    self.player.stop()
                    if event.modifiers() == Qt.ShiftModifier:
                        for index in indexes:
                            self.model.remove(
                                self.sorting_model.mapToSource(index))
                            remove_all_tags(os.path.normpath(self.model.filePath(self.sorting_model.mapToSource(
                                index)) if self.sorting_model else self.model.filePath(index)))
                        self.ui.statusbar.showMessage(
                            str(len(indexes))+" item(s) deleted")
                    else:
                        for index in indexes:
                            send2trash(os.path.normpath(self.model.filePath(self.sorting_model.mapToSource(
                                index)) if self.sorting_model else self.model.filePath(index)))
                            remove_all_tags(os.path.normpath(self.model.filePath(self.sorting_model.mapToSource(
                                index)) if self.sorting_model else self.model.filePath(index)))
                        self.ui.statusbar.showMessage(
                            str(len(indexes))+" item(s) sent to trash")
                elif event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
                    indexes = self.ui.treeView.selectionModel().selectedRows()
                    urls = [QUrl(self.model.filePath(self.sorting_model.mapToSource(
                        index)) if self.sorting_model else self.model.filePath(index)) for index in indexes]
                    mime_data = QMimeData()
                    mime_data.setUrls(urls)
                    clipboard = QApplication.clipboard()
                    clipboard.setMimeData(mime_data)
                elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
                    clipboard = QApplication.clipboard()
                    for url in clipboard.mimeData().urls():
                        # TBD: Implement paste functionality
                        pass
                return False
            if event.type() == QEvent.Drop:
                for url in event.mimeData().urls():
                    # TBD: Implement drop functionality
                    pass
        else:
            if event.type() == QEvent.MouseButtonPress:
                self.play_media()
            if event.type() == QEvent.Wheel:
                if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                    delta = event.angleDelta().y() // 120
                    self.ui.mediaVolumeDial.setValue(self.ui.mediaVolumeDial.value() + delta * 5)
                    return True
        return super(TaggerWindow, self).eventFilter(source, event)
    
        # aux function, required for smooth navigation using slider
    def action_trig(self, action):
        if action == 1:
            self.seek_position(self.ui.mediaPositionSlider.value())

# Begin Media Player section
    def media_update_play_button(self, state):
        icon1 = QIcon()
        icon1.addFile(u":/images/icons/media-pause.svg" if state ==
                      QMediaPlayer.PlaybackState.PlayingState else u":/images/icons/media-play.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.ui.mediaPlayButton.setIcon(icon1)

    def play_media(self):
        file_url = QUrl.fromLocalFile(self.model.filePath(self.sorting_model.mapToSource(self.ui.treeView.currentIndex(
        )))) if self.sorting_model else QUrl.fromLocalFile(self.model.filePath(self.ui.treeView.currentIndex()))
        
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState and self.player.source() == file_url:
            self.player.pause()
        elif self.player.source() != file_url:
            self.player.setSource(file_url)
            self.player.play()
        else: # Same file, but paused or stopped, so play.
            self.player.play()

    def change_position(self, position):
        self.ui.mediaPositionSlider.setValue(position)
        self.ui.mediaDurationLabel.setText(millis_to_str(
            position)+" / "+millis_to_str(self.player.duration()))

    def seek_position(self, position):
        self.player.setPosition(position)

    def change_duration(self, duration):
        self.ui.mediaDurationLabel.setText("0:00 / "+millis_to_str(duration))
        self.ui.mediaPositionSlider.setRange(0, duration)
        self.ui.mediaPositionSlider.setPageStep(int(duration/20))
# End Media Player section

    def populate(self):
        self.settings = load_settings()
        self.checkAction = {}  # checkboxes in context menu
        self.tag_checkboxes = {}  # checkboxes in tag dock widget
        self.tag_combos = {}  # comboboxes in tag dock widget
        self.filter_tag_checkboxes = {}  # checkboxes in tag filter dock widget
        self.rule = {'recursive': False, 'action': 'Filter',
                     'conditions': []}  # filter rule
        self.tag_model = QStandardItemModel()
        generate_tag_model(self.tag_model, get_tags_and_groups())

        self.ui.actionNone1 = QAction(self)
        self.ui.recent_menu.aboutToShow.connect(self.update_recent_menu)
        self.ui.recent_menu.triggered.connect(self.open_file_from_recent)

        path = self.settings['current_folder'] if 'current_folder' in self.settings.keys(
        ) and self.settings['current_folder'] != '' else normpath(QDir.homePath())

        self.model = TagFSModel()
        self.model.setRootPath(path)
        self.model.setReadOnly(False)
        self.model.setFilter(QDir.NoDot | QDir.AllEntries | QDir.Hidden)
        self.model.sort(0, Qt.SortOrder.AscendingOrder)

        self.sorting_model = SortingModel()
        self.sorting_model.mode = "Folder"
        # TBD maybe this is not needed, model gets added later anyway
        self.sorting_model.setSourceModel(self.model)

        self.ui.pathEdit.setText(path)

        self.ui.treeView.setModel(self.sorting_model)

        self.ui.treeView.setRootIndex(
            self.sorting_model.mapFromSource(self.model.index(path, 0)))
        self.ui.treeView.header().resizeSection(0, 350)

        self.init_tag_checkboxes()
        self.update_ui()

    def init_tag_checkboxes(self):
        """Initializes and populates the tag checkboxes in the tags dock widget."""
        # removing all tag checkboxes
        while True:
            if self.ui.tagsLayout.itemAt(0):
                self.ui.tagsLayout.itemAt(0).widget().deleteLater()
            if not self.ui.tagsLayout.takeAt(0):
                break

        for i in range(self.tag_model.rowCount()):
            group = self.tag_model.item(i).data(Qt.UserRole)
            if group['name_shown']:
                self.ui.tagsLayout.addWidget(
                    QLabel('<b>'+group['name']+'</b>'))
            if group['widget_type'] == 0:
                for k in range(self.tag_model.item(i).rowCount()):
                    tag = self.tag_model.item(i).child(k).data(Qt.UserRole)
                    self.tag_checkboxes[tag['name']] = QCheckBox(tag['name'])
                    self.ui.tagsLayout.addWidget(
                        self.tag_checkboxes[tag['name']])
                    self.tag_checkboxes[tag['name']
                                        ].clicked.connect(self.set_tags)
                    if tag['color']:
                        color = QColor()
                        color.setRgba(tag['color'])
                        self.tag_checkboxes[tag['name']].setPalette(color)
                        self.tag_checkboxes[tag['name']
                                            ].setAutoFillBackground(True)
            elif group['widget_type'] == 1:
                self.tag_combos[group['id']] = QComboBox(self)
                self.tag_combos[group['id']].addItems([""]+[self.tag_model.item(i).child(k).data(
                    Qt.UserRole)['name'] for k in range(self.tag_model.item(i).rowCount())])
                self.ui.tagsLayout.addWidget(self.tag_combos[group['id']])
                self.tag_combos[group['id']].currentIndexChanged.connect(
                    self.set_tags)
        self.ui.tagsScrollArea.setWidgetResizable(True)

    def update_tag_checkboxes(self):
        """Updates the state of tag checkboxes based on the selected files."""
        indexes = self.ui.treeView.selectionModel().selectedRows()
        if self.sorting_model:
            cur_selection = [normpath(self.model.filePath(
                self.sorting_model.mapToSource(index))) for index in indexes]
        else:
            cur_selection = [normpath(self.model.filePath(index))
                             for index in indexes]

        all_files_tags_with_group_ids = []
        for f in cur_selection:
            all_files_tags_with_group_ids.extend(get_tags_by_group_ids(f))

        if all_files_tags_with_group_ids:
            all_files_tags, n = zip(*all_files_tags_with_group_ids)
        else:
            all_files_tags = []

        tree = {}
        for t in set(all_files_tags_with_group_ids):
            if t[1] not in tree.keys():
                tree[t[1]] = []
            tree[t[1]].append(t[0])

        for i in range(self.tag_model.rowCount()):
            group = self.tag_model.item(i).data(Qt.UserRole)
            if group['widget_type'] == 0:
                for t in get_all_tags_by_group_id(group['id']):
                    if t not in all_files_tags:
                        self.tag_checkboxes[t].setTristate(False)
                        if self.tag_checkboxes[t].checkState() is not Qt.CheckState.Unchecked:
                            self.tag_checkboxes[t].setChecked(False)
                    elif all_files_tags.count(t) < len(cur_selection):
                        self.tag_checkboxes[t].setTristate(True)
                        if self.tag_checkboxes[t].checkState() is not Qt.CheckState.PartiallyChecked:
                            self.tag_checkboxes[t].setCheckState(
                                Qt.CheckState.PartiallyChecked)
                    else:
                        if self.tag_checkboxes[t].checkState() is not Qt.CheckState.Checked:
                            self.tag_checkboxes[t].setChecked(True)
            elif group['widget_type'] == 1:
                if group['id'] not in tree.keys():
                    self.tag_combos[group['id']].setCurrentText('')
                else:
                    self.tag_combos[group['id']].setCurrentText(
                        tree[group['id']][0])

    def update_recent_menu(self):
        self.ui.recent_menu.clear()
        for row, foldername in enumerate(self.settings['recent_folders'], 1):
            recent_action = self.ui.recent_menu.addAction('&{}. {}'.format(
                row, foldername))
            recent_action.setData(foldername)

    def open_file_from_recent(self, action):
        """Opens a recently accessed folder when selected from the menu."""
        self.ui.sourceComboBox.setCurrentText("Folder")
        self.update_ui()
        self.ui.pathEdit.setText(normpath(action.data()))
        self.change_path()

    def update_ui(self):
        """Updates the UI elements based on the selected source mode (Folder/Tagged)."""
        mode = self.ui.sourceComboBox.currentText()
        self.ui.pathEdit.setEnabled(mode == 'Folder')
        self.ui.browseButton.setEnabled(mode == 'Folder')
        self.update_treeview()

    def update_status(self):
        indexes = self.ui.treeView.selectionModel().selectedRows()
        indexes.sort()
        self.prev_indexes.sort()
        if indexes != self.prev_indexes:
            self.player.stop()
            path = self.model.filePath(self.sorting_model.mapToSource(self.ui.treeView.currentIndex(
            ))) if self.sorting_model else self.model.filePath(self.ui.treeView.currentIndex())
            ftype = get_file_type(path)
            if isfile(path) and ftype in ('Audio', 'Video', 'Image'):
                file_url = QUrl.fromLocalFile(self.model.filePath(self.sorting_model.mapToSource(self.ui.treeView.currentIndex(
                )))) if self.sorting_model else QUrl.fromLocalFile(self.model.filePath(self.ui.treeView.currentIndex()))
                if ftype == 'Audio':  # TBD change this to audio file type
                    self.ui.playerLayout.setGeometry(QRect(0, 0, 0, 0))
                if ftype == 'Image':
                    self.ui.playerLayout.update()
                self.player.setSource(file_url)
                self.player.play()
                self.player.pause()
                self.ui.mediaPlayButton.setVisible(ftype in ('Video', 'Audio'))
                self.ui.mediaPositionSlider.setVisible(
                    ftype in ('Video', 'Audio'))
                self.ui.mediaVolumeDial.setVisible(ftype in ('Video', 'Audio'))
                self.ui.mediaDurationLabel.setVisible(
                    ftype in ('Video', 'Audio'))
            else:
                self.ui.playerLayout.setGeometry(QRect(0, 0, 0, 0))
                self.ui.mediaPlayButton.setVisible(False)
                self.ui.mediaPositionSlider.setVisible(False)
                self.ui.mediaVolumeDial.setVisible(False)
                self.ui.mediaDurationLabel.setVisible(False)
        self.prev_indexes = indexes
        # TBD Review this
        num_selected = len(self.ui.treeView.selectionModel().selectedRows())
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
        file_path = self.ui.pathEdit.text()
        if isdir(file_path):
            self.ui.statusbar.clearMessage()
            # TBD reuse this in a function
            self.model.setRootPath(normpath(file_path))
            self.ui.treeView.setRootIndex(
                self.sorting_model.mapFromSource(self.model.index(file_path, 0)))
            self.ui.pathEdit.setText(normpath(self.model.filePath(
                self.sorting_model.mapToSource(self.ui.treeView.rootIndex()))))
            if normpath(self.settings['current_folder']) != normpath(file_path):
                self.settings['current_folder'] = file_path
                if file_path in self.settings['recent_folders']:
                    self.settings['recent_folders'].remove(file_path)
                self.settings['recent_folders'].insert(0, file_path)
                if len(self.settings['recent_folders']) > 15:
                    del self.settings['recent_folders'][-1]
                save_settings(SETTINGS_FILE, self.settings)

    def manage_tags(self):
        self.tags_dialog = TagsDialog(self.tag_model)
        self.tags_dialog.exec()
        clear_tags_cache()
        self.init_tag_checkboxes()
        self.update_tag_checkboxes()

    def open(self):
        index = self.ui.treeView.currentIndex()
        if self.sorting_model:
            file_path = normpath(self.model.filePath(
                self.sorting_model.mapToSource(index)))
        else:
            file_path = normpath(self.model.filePath(index))
        if isdir(file_path):
            self.ui.statusbar.clearMessage()
            # TBD reuse this in a function
            self.model.setRootPath(normpath(file_path))
            if self.sorting_model:
                self.ui.treeView.setRootIndex(self.sorting_model.mapFromSource(self.model.index(file_path, 0)))
            self.ui.pathEdit.setText(file_path)
            self.settings['current_folder'] = file_path
            if file_path in self.settings['recent_folders']:
                self.settings['recent_folders'].remove(file_path)
            self.settings['recent_folders'].insert(0, file_path)
            if len(self.settings['recent_folders']) > 15:
                del self.settings['recent_folders'][-1]
            save_settings(SETTINGS_FILE, self.settings)
        elif isfile(file_path):
            open_file(file_path)

    def create_folder(self):
        folder, ok = QInputDialog.getText(self, "Create new folder",
                                          "Enter folder name:", QLineEdit.Normal)
        if ok and folder != '':
            index = self.ui.treeView.currentIndex()
            # TBD this works a bit unexpectedly in "Tagged" mode - it creates a folder inside the parent folder, not the selected folder
            if self.sorting_model:
                full_path = Path(self.model.filePath(
                    self.sorting_model.mapToSource(index))).parent / folder
            else:
                full_path = Path(self.model.filePath(index)).parent / folder
            try:
                os.mkdir(full_path)
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", "Can't create this folder", QMessageBox.Ok)

    def context_menu(self, position):
        indexes = self.ui.treeView.selectionModel().selectedRows()
        if self.sorting_model:
            cur_selection = [normpath(self.model.filePath(
                self.sorting_model.mapToSource(index))) for index in indexes]
        else:
            cur_selection = [normpath(self.model.filePath(index))
                             for index in indexes]

        all_files_tags = []
        for f in cur_selection:  # TBD v3 not the most efficient procedure maybe
            all_files_tags.extend(get_tags(f))

        menu = QMenu()

        createFolderAct = QAction("&Create folder", self)
        createFolderAct.setStatusTip("Create a new folder")
        createFolderAct.triggered.connect(self.create_folder)
        menu.addAction(createFolderAct)

        self.checkAction = {}

        cursor = QCursor()
        menu.exec(cursor.pos())

    def set_tags(self, state):
        sender = self.sender()
        indexes = self.ui.treeView.selectionModel().selectedRows()

        if self.sorting_model:
            cur_selection = [normpath(self.model.filePath(
                self.sorting_model.mapToSource(index))) for index in indexes]
        else:
            cur_selection = [normpath(self.model.filePath(index))
                             for index in indexes]

        if type(sender) == QCheckBox:
            for file_path in cur_selection:
                if state:  # checked - it was 2 when used with stateChanged
                    add_tag(file_path, sender.text())
                elif not state:  # unchecked - it was 0 when used with stateChanged
                    remove_tag(file_path, sender.text())
        elif type(sender) == QComboBox:
            for file_path in cur_selection:
                if sender.currentText() == '':
                    remove_tags(file_path, [sender.itemText(i) for i in range(
                        sender.count()) if sender.itemText(i) != ''])
                else:
                    remove_tags(file_path, [sender.itemText(i) for i in range(
                        sender.count()) if sender.itemText(i) != ''])  # TBD maybe optimize this
                    add_tag(file_path, sender.currentText())


class TagFSModel(QFileSystemModel):
    def columnCount(self, parent=QModelIndex()):
        return super(TagFSModel, self).columnCount()+1

    def supportedDragActions(self) -> Qt.DropActions:
        return Qt.MoveAction | Qt.CopyAction

    def headerData(self, section, orientation, role):
        if section == 4 and role == Qt.DisplayRole:
            return "Tag(s)"
        else:
            return super(TagFSModel, self).headerData(section, orientation, role)

    def data(self, index, role):
        if index.column() == 2 and role == Qt.DisplayRole:
            return QMimeDatabase().mimeTypeForFile(self.filePath(index)).comment()

        tags = get_tags(normpath(self.filePath(index))) if role in (
            Qt.DisplayRole, Qt.BackgroundRole) else []
        if index.column() == self.columnCount() - 1:
            if role == Qt.DisplayRole:
                return ', '.join(tags)
        if role == Qt.BackgroundRole and tags and tag_get_color(tags[0]):
            color = QColor()
            color.setRgba(tag_get_color(tags[0]))
            return color

        return super(TagFSModel, self).data(index, role)


class CheckBoxAction(QWidgetAction):
    def __init__(self, parent, text):
        super(CheckBoxAction, self).__init__(parent)
        layout = QHBoxLayout()
        self.widget = QWidget()
        self.checkbox = QCheckBox()
        self.checkbox.setText(text)
        if tag_get_color(text):
            self.checkbox.setPalette(QColor(tag_get_color(text)))
            self.checkbox.setAutoFillBackground(True)
        layout.addWidget(self.checkbox)
        layout.addStretch()
        layout.setContentsMargins(3, 3, 6, 3)

        self.widget.setLayout(layout)

        self.setDefaultWidget(self.widget)


class SortingModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filtered_paths = []
        self.filter_enabled = False

    def recalc_filtered_paths(self, rule):
        if 'conditions' in rule.keys() and rule['conditions']:
            self.filtered_paths = get_files_affected_by_rule(rule)
            self.filter_enabled = True
        else:
            self.filter_enabled = False

    def lessThan(self, source_left: QModelIndex, source_right: QModelIndex):
        assert source_left.column() == source_right.column()
        file_info1 = self.sourceModel().fileInfo(source_left)
        file_info2 = self.sourceModel().fileInfo(source_right)

        if file_info1.fileName() == "..":
            return self.sortOrder() == Qt.SortOrder.AscendingOrder

        if file_info2.fileName() == "..":
            return self.sortOrder() == Qt.SortOrder.DescendingOrder

        if source_left.column() == 1:
            return self.sourceModel().size(source_left) < self.sourceModel().size(source_right)

        if source_left.column() == 3:
            return self.sourceModel().lastModified(source_left).__le__(self.sourceModel().lastModified(source_right))

        if (file_info1.isDir() and file_info2.isDir()) or (file_info1.isFile() and file_info2.isFile()):
            return super().lessThan(source_left, source_right)

        return file_info1.isDir() and self.sortOrder() == Qt.SortOrder.AscendingOrder

    def filterAcceptsRow(self, source_row, source_parent):
        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        path = index.data(QFileSystemModel.FilePathRole)

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
    seconds = (millis/1000) % 60
    seconds = str(int(seconds))
    if len(seconds) == 1:
        seconds = "0"+seconds
    minutes = (millis/(1000*60)) % 60
    minutes = str(int(minutes))
    # if len(minutes) == 1:
    #     minutes = "0"+minutes
    hours = str(int((millis/(1000*60*60)) % 24))
    return (hours+":" if hours != "0" else "")+minutes+":"+seconds


def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])


def main():
    app = QApplication(sys.argv)
    window = TaggerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()