import os
import sys
import subprocess
from os.path import normpath, isfile, isdir
from pathlib import Path
from send2trash import send2trash
import logging
from PySide6.QtGui import QIcon, QColor, QCursor, QStandardItemModel, QAction
from PySide6.QtWidgets import (
    QWidget,
    QApplication,
    QMainWindow,
    QFileSystemModel,
    QFileIconProvider,
    QMenu,
    QAbstractItemView,
    QFrame,
    QLineEdit,
    QMessageBox,
    QWidgetAction,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QFileDialog,
    QComboBox,
    QInputDialog,
)
from PySide6.QtCore import (
    QDir,
    Qt,
    QModelIndex,
    QSortFilterProxyModel,
    QUrl,
    QRect,
    QSize,
    QEvent,
    QMimeData,
    QMimeDatabase,
    QByteArray,
    QDataStream,
    QIODevice,
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from src.ui.ui_tagger_window import Ui_taggerWindow
from src.tags_dialog import TagsDialog, generate_tag_model
from declutter.config import ALL_TAGGED_TEXT
from declutter.store import load_settings, save_settings
from declutter.rules import get_files_affected_by_rule
from declutter.tags import (
    tag_get_color,
    set_tags,
    get_tags,
    get_tags_by_group_ids,
    add_tag,
    remove_tags,
    remove_all_tags,
    clear_tags_cache,
    get_all_tags_by_group_id,
    remove_tag,
    get_tags_and_groups,
)
from declutter.file_utils import get_file_type, open_file

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
        self.ui.mediaVolumeDial.valueChanged.connect(
            lambda v: self._audio_output.setVolume(v / 100.0)
        )
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
            self.update_treeview
        )
        self.ui.conditionListWidget.itemDoubleClicked.connect(self.edit_condition)

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

        self._clipboard_mime = None

        # Populate initial UI elements
        self.populate()  # TBD can't it be just a part of init()?

    def in_tagged_mode(self):
        return self.ui.sourceComboBox.currentText() == "Tagged"

    def _current_target_dir(self):
        # Only allow pasting into Folder mode, since Tagged view isn't a real FS destination
        if self.in_tagged_mode():
            return None

        view_model = self.ui.treeView.model()
        cur_index = self.ui.treeView.currentIndex()

        # If no valid selection, fallback to model rootPath (Folder mode)
        if not cur_index.isValid():
            if isinstance(self.model, QFileSystemModel):
                return os.path.normpath(self.model.rootPath())
            return None

        # Map to source if the view uses a proxy, regardless of self.sorting_model identity
        try:
            if isinstance(view_model, QSortFilterProxyModel):
                src_index = view_model.mapToSource(cur_index)
                if src_index.isValid() and isinstance(self.model, QFileSystemModel):
                    path = self.model.filePath(src_index)
                else:
                    path = None
            elif isinstance(view_model, QFileSystemModel):
                path = view_model.filePath(cur_index)
            else:
                path = None
        except Exception:
            path = None

        if not path:
            # Fallback to this window's model root
            if isinstance(self.model, QFileSystemModel):
                return os.path.normpath(self.model.rootPath())
            return None

        # If a file is selected, paste into its parent directory
        return os.path.normpath(path if os.path.isdir(path) else os.path.dirname(path))

    def new_window(self):
        """Opens a new TaggerWindow instance."""
        tagger = TaggerWindow(self)
        tagger.show()
        tagger.move(self.x() + 30, self.y() + 30)

    def update_treeview(self):
        """Updates the file tree view based on the selected source and filter conditions."""
        mode = self.ui.sourceComboBox.currentText()
        self.player.stop()
        self.rule["condition_switch"] = self.ui.filterConditionSwitchCombo.currentText()
        self.ui.treeView.setEditTriggers(
            QAbstractItemView.EditKeyPressed | QAbstractItemView.SelectedClicked
        )
        if mode == "Tagged":
            self.rule["folders"] = [ALL_TAGGED_TEXT]
            paths = get_files_affected_by_rule(self.rule, True)
            self.model = FileSystemModelLite(paths, self)
            self.sorting_model = QSortFilterProxyModel(self)
            self.sorting_model.setSourceModel(self.model)
            self.sorting_model.setSortCaseSensitivity(Qt.CaseInsensitive)
            self.ui.treeView.setItemsExpandable(True)
            self.ui.treeView.setModel(self.sorting_model)
            self.ui.treeView.setSortingEnabled(True)
            self.ui.treeView.expandAll()
            self.ui.treeView.selectionModel().selectionChanged.connect(
                self.update_status
            )
        else:
            self.model = TagFSModel()
            self.model.setReadOnly(False)
            path = (
                self.settings["current_folder"]
                if "current_folder" in self.settings.keys()
                and self.settings["current_folder"] != ""
                else normpath(QDir.homePath())
            )
            self.model.setRootPath(path)
            self.model.setFilter(QDir.NoDot | QDir.AllEntries | QDir.Hidden)
            self.model.sort(0, Qt.SortOrder.AscendingOrder)
            self.sorting_model = SortingModel(self)
            self.sorting_model.setSourceModel(self.model)
            self.sorting_model.setSortCaseSensitivity(Qt.CaseInsensitive)
            self.rule["folders"] = [normpath(self.ui.pathEdit.text())]
            self.sorting_model.recalc_filtered_paths(self.rule)
            self.ui.treeView.setModel(self.sorting_model)
            self.ui.treeView.setRootIndex(
                self.sorting_model.mapFromSource(self.model.index(path, 0))
            )
            self.model.fileRenamed.connect(self.tag_renamed_file)
            self.model.setIconProvider(QFileIconProvider())
            self.ui.treeView.header().setSortIndicator(0, Qt.AscendingOrder)
            self.ui.treeView.setSortingEnabled(True)
            self.ui.treeView.setItemsExpandable(False)
            self.ui.treeView.setRootIsDecorated(False)
            self.ui.treeView.selectionModel().selectionChanged.connect(
                self.update_status
            )
            self.ui.treeView.setDragDropMode(QAbstractItemView.DragDrop)
            self.ui.treeView.setAcceptDrops(True)
            self.ui.treeView.setDefaultDropAction(Qt.MoveAction)

    def tag_renamed_file(self, path, oldName, newName):
        """Updates tags when a file is renamed or moved within the same watched directory."""
        try:
            old_path = os.path.normpath(os.path.join(path, oldName))
            new_path = os.path.normpath(os.path.join(path, newName))
            set_tags(new_path, get_tags(old_path))
            remove_all_tags(old_path)
        except Exception:
            pass

    def add_condition(self):
        """Opens a dialog to add a new condition to the rule."""
        self.condition_window = ConditionDialog()
        self.condition_window.exec()
        if self.condition_window.condition:
            self.rule["conditions"].append(self.condition_window.condition)
            self.refresh_conditions()

    def edit_condition(self, cond):
        """Opens a dialog to edit an existing condition."""
        self.condition_window = ConditionDialog()
        self.condition_window.loadCondition(
            self.rule["conditions"][
                self.ui.conditionListWidget.indexFromItem(cond).row()
            ]
        )
        self.condition_window.exec_()
        self.refresh_conditions()

    def delete_condition(self):
        """Deletes the selected condition from the rule."""
        del self.rule["conditions"][
            self.ui.conditionListWidget.selectedIndexes()[0].row()
        ]
        self.refresh_conditions()

    def clear_conditions(self):
        """Clears all conditions from the rule."""
        self.rule["conditions"] = []
        self.refresh_conditions()

    def refresh_conditions(self):
        """Refreshes the list of conditions displayed in the UI."""
        conds = []

        for c in self.rule["conditions"]:
            if c["type"] == "tags" and c["tag_switch"] != "tags in group":
                conds.append(
                    "Has "
                    + c["tag_switch"]
                    + (
                        " of these tags: " + ", ".join(c["tags"])
                        if c["tag_switch"] not in ("no tags", "any tags")
                        else ""
                    )
                )
            elif c["type"] == "tags" and c["tag_switch"] == "tags in group":
                conds.append("Has tags in group: " + c["tag_group"])
            elif c["type"] == "date":
                conds.append(
                    "Age is "
                    + c["age_switch"]
                    + " "
                    + str(c["age"])
                    + " "
                    + c["age_units"]
                )
            elif c["type"] == "name":
                if not "name_switch" in c.keys():
                    c["name_switch"] = "matches"
                conds.append("Name " + c["name_switch"] + " " + str(c["filemask"]))
            elif c["type"] == "size":
                conds.append(
                    "File size is "
                    + c["size_switch"]
                    + " "
                    + str(c["size"])
                    + c["size_units"]
                )
            elif c["type"] == "type":
                conds.append(
                    "File type " + c["file_type_switch"] + " " + c["file_type"]
                )

        self.ui.conditionListWidget.clear()
        self.ui.conditionListWidget.addItems(conds)
        self.update_treeview()

    def closeEvent(self, event):
        """Stops media playback when the window is closed."""
        self.player.stop()

    def eventFilter(self, source, event):
        """Filters events for specific UI elements to handle custom interactions."""
        if source == self.ui.treeView:
            if event.type() == QEvent.Drop:
                mime = event.mimeData()
                index_at_pos = (
                    self.ui.treeView.indexAt(event.position().toPoint())
                    if hasattr(event, "position")
                    else self.ui.treeView.indexAt(event.pos())
                )
                target_index = (
                    index_at_pos
                    if index_at_pos.isValid()
                    else self.ui.treeView.rootIndex()
                )
                src_target_index = (
                    self.sorting_model.mapToSource(target_index)
                    if self.sorting_model
                    else target_index
                )

                # Resolve action from keyboard modifiers per Qt conventions:
                mods = event.keyboardModifiers()
                if mods & Qt.ControlModifier:
                    action = Qt.CopyAction  # Ctrl forces copy
                elif mods & Qt.ShiftModifier:
                    action = Qt.MoveAction  # Shift forces move
                else:
                    # Fall back to the view's defaultDropAction (commonly MoveAction as you set)
                    action = self.ui.treeView.defaultDropAction()

                if hasattr(self.model, "dropMimeData"):
                    acted = self.model.dropMimeData(
                        mime, action, -1, -1, src_target_index
                    )
                    if acted:
                        event.acceptProposedAction()
                        self.update_treeview()
                        self.update_tag_checkboxes()
                        return True
                return False
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_F2:
                    self.player.stop()
                if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    if self.ui.treeView.state() is not QAbstractItemView.EditingState:
                        self.open()
                    return True
                if event.key() == Qt.Key_Delete:
                    indexes = self.ui.treeView.selectionModel().selectedRows()
                    self.player.stop()

                    if event.modifiers() == Qt.ShiftModifier:
                        # Confirm permanent deletion
                        count = len(indexes)
                        reply = QMessageBox.question(
                            self,
                            "Delete files",
                            f"Permanently delete {count} item(s)? This cannot be undone.",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No,
                        )
                        if reply != QMessageBox.Yes:
                            return True

                        for index in indexes:
                            src_index = (
                                self.sorting_model.mapToSource(index)
                                if self.sorting_model
                                else index
                            )
                            # capture path for tag cleanup before removing the row
                            try:
                                path = os.path.normpath(self.model.filePath(src_index))
                            except Exception:
                                path = ""
                            self.model.remove(src_index)
                            if path:
                                remove_all_tags(path)
                        self.ui.statusbar.showMessage(
                            str(len(indexes)) + " item(s) deleted"
                        )
                    else:
                        for index in indexes:
                            src_index = (
                                self.sorting_model.mapToSource(index)
                                if self.sorting_model
                                else index
                            )
                            try:
                                path = os.path.normpath(self.model.filePath(src_index))
                            except Exception:
                                path = ""
                            if path:
                                try:
                                    send2trash(path)
                                except Exception:
                                    pass
                                remove_all_tags(path)
                        self.ui.statusbar.showMessage(
                            str(len(indexes)) + " item(s) sent to trash"
                        )
                    return True

                elif (
                    event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier
                ):
                    # Collect selected rows and store as file:// URLs in clipboard
                    indexes = self.ui.treeView.selectionModel().selectedRows()
                    urls = [
                        QUrl.fromLocalFile(
                            self.model.filePath(self.sorting_model.mapToSource(index))
                            if self.sorting_model
                            else self.model.filePath(index)
                        )
                        for index in indexes
                    ]

                    mime_data = QMimeData()
                    mime_data.setUrls(urls)

                    # Keep a strong reference to avoid premature GC of the QMimeData
                    self._clipboard_mime = mime_data
                    QApplication.clipboard().setMimeData(self._clipboard_mime)
                    return True

                elif (
                    event.key() == Qt.Key_X and event.modifiers() == Qt.ControlModifier
                ):
                    # Collect selected rows and store as file:// URLs in clipboard, mark as cut
                    indexes = self.ui.treeView.selectionModel().selectedRows()
                    urls = [
                        QUrl.fromLocalFile(
                            self.model.filePath(self.sorting_model.mapToSource(index))
                            if self.sorting_model
                            else self.model.filePath(index)
                        )
                        for index in indexes
                    ]

                    mime_data = QMimeData()
                    mime_data.setUrls(urls)

                    # Windows Explorer hint: 2 = Cut (Move)
                    drop_effect = 2
                    ba = QByteArray()
                    ds = QDataStream(ba, QIODevice.WriteOnly)
                    ds.setByteOrder(QDataStream.LittleEndian)
                    ds << drop_effect
                    mime_data.setData("Preferred DropEffect", ba)

                    self._clipboard_mime = mime_data
                    QApplication.clipboard().setMimeData(self._clipboard_mime)
                    return True

                elif (
                    event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier
                ):
                    if not self.ui.treeView.hasFocus():
                        return True
                    # Ensure this is the active window
                    if QApplication.activeWindow() is not self:
                        return True
                    if self.in_tagged_mode():
                        return True

                    clipboard = QApplication.clipboard()
                    clip_mime = clipboard.mimeData()

                    paste_urls = []
                    if clip_mime:
                        if clip_mime.hasUrls():
                            paste_urls = clip_mime.urls()
                        if not paste_urls and clip_mime.hasText():
                            raw = clip_mime.text().strip()
                            if raw:
                                for part in raw.splitlines():
                                    part = part.strip()
                                    if not part:
                                        continue
                                    u = QUrl(part)
                                    if u.isLocalFile() or u.scheme() == "file":
                                        paste_urls.append(u)
                                    elif os.path.isabs(part):
                                        paste_urls.append(QUrl.fromLocalFile(part))

                    if not paste_urls:
                        return True

                    target_dir = self._current_target_dir()
                    if not target_dir or not os.path.isdir(target_dir):
                        return True

                    # Check for overwrite conflicts
                    for url in paste_urls:
                        dst_path = os.path.join(
                            target_dir, os.path.basename(url.toLocalFile())
                        )
                        if os.path.exists(dst_path):
                            reply = QMessageBox.question(
                                self,
                                "File exists",
                                f"File '{os.path.basename(dst_path)}' already exists in the target folder.\nOverwrite?",
                                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                QMessageBox.No,
                            )
                            if reply == QMessageBox.Cancel:
                                return True
                            elif reply == QMessageBox.No:
                                paste_urls = [u for u in paste_urls if u != url]
                            # if Yes → keep in list to overwrite

                    if not paste_urls:
                        return True

                    mime_for_drop = QMimeData()
                    mime_for_drop.setUrls(paste_urls)
                    if clip_mime and "Preferred DropEffect" in clip_mime.formats():
                        mime_for_drop.setData(
                            "Preferred DropEffect",
                            clip_mime.data("Preferred DropEffect"),
                        )

                    drop_effect_val = None
                    if clip_mime and "Preferred DropEffect" in clip_mime.formats():
                        try:
                            ds = QDataStream(clip_mime.data("Preferred DropEffect"))
                            ds.setByteOrder(QDataStream.LittleEndian)
                            drop_effect_val = ds.readInt32()
                        except Exception as e:
                            logging.warning(
                                "[PASTE] Error reading Preferred DropEffect: %s", e
                            )

                    # Decide action
                    if drop_effect_val == 2:
                        action = Qt.MoveAction
                    else:
                        # Default copy; Shift forces move
                        mods = QApplication.keyboardModifiers()
                        action = (
                            Qt.CopyAction
                            if not (mods & Qt.ShiftModifier)
                            else Qt.MoveAction
                        )

                    src_target_index = (
                        self.model.index(target_dir, 0)
                        if isinstance(self.model, QFileSystemModel)
                        else QModelIndex()
                    )

                    if hasattr(self.model, "dropMimeData"):
                        if self.model.dropMimeData(
                            mime_for_drop, action, -1, -1, src_target_index
                        ):
                            self.update_treeview()
                            self.update_tag_checkboxes()
                    return True

        else:
            if event.type() == QEvent.MouseButtonPress:
                self.play_media()
            if event.type() == QEvent.Wheel:
                if (
                    self.player.playbackState()
                    == QMediaPlayer.PlaybackState.PlayingState
                ):
                    delta = event.angleDelta().y() // 120
                    self.ui.mediaVolumeDial.setValue(
                        self.ui.mediaVolumeDial.value() + delta * 5
                    )
                    return True
        return super(TaggerWindow, self).eventFilter(source, event)

        # aux function, required for smooth navigation using slider

    def action_trig(self, action):
        if action == 1:
            self.seek_position(self.ui.mediaPositionSlider.value())

    # Begin Media Player section
    def media_update_play_button(self, state):
        icon1 = QIcon()
        icon1.addFile(
            (
                ":/images/icons/media-pause.svg"
                if state == QMediaPlayer.PlaybackState.PlayingState
                else ":/images/icons/media-play.svg"
            ),
            QSize(),
            QIcon.Normal,
            QIcon.Off,
        )
        self.ui.mediaPlayButton.setIcon(icon1)

    def play_media(self):
        file_url = (
            QUrl.fromLocalFile(
                self.model.filePath(
                    self.sorting_model.mapToSource(self.ui.treeView.currentIndex())
                )
            )
            if self.sorting_model
            else QUrl.fromLocalFile(
                self.model.filePath(self.ui.treeView.currentIndex())
            )
        )

        if (
            self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
            and self.player.source() == file_url
        ):
            self.player.pause()
        elif self.player.source() != file_url:
            self.player.setSource(file_url)
            self.player.play()
        else:  # Same file, but paused or stopped, so play.
            self.player.play()

    def change_position(self, position):
        self.ui.mediaPositionSlider.setValue(position)
        self.ui.mediaDurationLabel.setText(
            millis_to_str(position) + " / " + millis_to_str(self.player.duration())
        )

    def seek_position(self, position):
        self.player.setPosition(position)

    def change_duration(self, duration):
        self.ui.mediaDurationLabel.setText("0:00 / " + millis_to_str(duration))
        self.ui.mediaPositionSlider.setRange(0, duration)
        self.ui.mediaPositionSlider.setPageStep(int(duration / 20))

    # End Media Player section

    def populate(self):
        self.settings = load_settings()
        self.checkAction = {}  # checkboxes in context menu
        self.tag_checkboxes = {}  # checkboxes in tag dock widget
        self.tag_combos = {}  # comboboxes in tag dock widget
        self.filter_tag_checkboxes = {}  # checkboxes in tag filter dock widget
        self.rule = {
            "recursive": False,
            "action": "Filter",
            "conditions": [],
        }  # filter rule
        self.tag_model = QStandardItemModel()
        generate_tag_model(self.tag_model, get_tags_and_groups())

        self.ui.actionNone1 = QAction(self)
        self.ui.recent_menu.aboutToShow.connect(self.update_recent_menu)
        self.ui.recent_menu.triggered.connect(self.open_file_from_recent)

        path = (
            self.settings["current_folder"]
            if "current_folder" in self.settings.keys()
            and self.settings["current_folder"] != ""
            else normpath(QDir.homePath())
        )

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
            self.sorting_model.mapFromSource(self.model.index(path, 0))
        )
        self.ui.treeView.header().resizeSection(0, 350)

        self.init_tag_checkboxes()
        self.update_ui()

    def init_tag_checkboxes(self):
        """Initializes and populates the tag checkboxes in the tags dock widget."""
        # reset mappings to avoid stale QObject references
        self.tag_checkboxes = {}
        self.tag_combos = {}

        # removing all tag checkboxes
        while True:
            if self.ui.tagsLayout.itemAt(0):
                self.ui.tagsLayout.itemAt(0).widget().deleteLater()
            if not self.ui.tagsLayout.takeAt(0):
                break

        for i in range(self.tag_model.rowCount()):
            group = self.tag_model.item(i).data(Qt.UserRole) or {}
            # default fallbacks if keys are missing
            widget_type = group.get("widget_type", 0)
            name_shown = group.get("name_shown", 1)
            group_id = group.get("id")

            if name_shown:
                self.ui.tagsLayout.addWidget(QLabel("" + group.get("name", "") + ""))

            if widget_type == 0:
                for k in range(self.tag_model.item(i).rowCount()):
                    tag = self.tag_model.item(i).child(k).data(Qt.UserRole)
                    self.tag_checkboxes[tag["name"]] = QCheckBox(tag["name"])
                    self.ui.tagsLayout.addWidget(self.tag_checkboxes[tag["name"]])
                    self.tag_checkboxes[tag["name"]].clicked.connect(self.set_tags)
                    self.tag_checkboxes[tag["name"]].setEnabled(False)
                    if tag["color"]:
                        color = QColor()
                        color.setRgba(tag["color"])
                        self.tag_checkboxes[tag["name"]].setPalette(color)
                        self.tag_checkboxes[tag["name"]].setAutoFillBackground(True)
            elif widget_type == 1:
                self.tag_combos[group_id] = QComboBox(self)
                self.tag_combos[group_id].addItems(
                    [""]
                    + [
                        self.tag_model.item(i).child(k).data(Qt.UserRole)["name"]
                        for k in range(self.tag_model.item(i).rowCount())
                    ]
                )
                self.ui.tagsLayout.addWidget(self.tag_combos[group_id])
                self.tag_combos[group_id].setCurrentText("")
                self.tag_combos[group_id].currentIndexChanged.connect(self.set_tags)
                self.tag_combos[group_id].setEnabled(False)

        self.ui.tagsScrollArea.setWidgetResizable(True)

    def update_tag_checkboxes(self):
        """Updates the state of tag checkboxes based on the selected files."""
        indexes = self.ui.treeView.selectionModel().selectedRows()

        if not indexes:
            for cb in self.tag_checkboxes.values():
                cb.setEnabled(False)
                cb.setChecked(False)
            for combo in self.tag_combos.values():
                combo.setEnabled(False)
                combo.setCurrentText("")
            return
        else:
            for cb in self.tag_checkboxes.values():
                cb.setEnabled(True)
            for combo in self.tag_combos.values():
                combo.setEnabled(True)

        if self.sorting_model:
            cur_selection = [
                normpath(self.model.filePath(self.sorting_model.mapToSource(index)))
                for index in indexes
            ]
        else:
            cur_selection = [normpath(self.model.filePath(index)) for index in indexes]

        all_files_tags_with_group_ids = []
        for f in cur_selection:
            all_files_tags_with_group_ids.extend(get_tags_by_group_ids(f))
        # all_files_tags_with_group_ids should be a list of (tag_name, group_id)

        if all_files_tags_with_group_ids:
            all_files_tags, _ = zip(*all_files_tags_with_group_ids)
        else:
            all_files_tags = []

        # Build group_id -> list[str tag_name]
        tree = {}
        for tag_name, group_id in set(all_files_tags_with_group_ids):
            tree.setdefault(group_id, []).append(tag_name)

        for i in range(self.tag_model.rowCount()):
            group = self.tag_model.item(i).data(Qt.UserRole)
            if group["widget_type"] == 0:
                for t in get_all_tags_by_group_id(group["id"]):
                    if t not in all_files_tags:
                        self.tag_checkboxes[t].setTristate(False)
                        if (
                            self.tag_checkboxes[t].checkState()
                            is not Qt.CheckState.Unchecked
                        ):
                            self.tag_checkboxes[t].setChecked(False)
                    elif all_files_tags.count(t) < len(cur_selection):
                        self.tag_checkboxes[t].setTristate(True)
                        if (
                            self.tag_checkboxes[t].checkState()
                            is not Qt.CheckState.PartiallyChecked
                        ):
                            self.tag_checkboxes[t].setCheckState(
                                Qt.CheckState.PartiallyChecked
                            )
                    else:
                        if (
                            self.tag_checkboxes[t].checkState()
                            is not Qt.CheckState.Checked
                        ):
                            self.tag_checkboxes[t].setChecked(True)
            elif group["widget_type"] == 1:
                # Set combo to the first tag name (string) for this group
                vals = tree.get(group["id"], [])
                if not vals:
                    self.tag_combos[group["id"]].setCurrentText("")
                else:
                    # Defensive: ensure we pass a string even if vals contain tuples by mistake
                    first = vals[0]
                    self.tag_combos[group["id"]].setCurrentText(
                        first if isinstance(first, tuple) else first
                    )

    def update_recent_menu(self):
        self.ui.recent_menu.clear()
        for row, foldername in enumerate(self.settings["recent_folders"], 1):
            recent_action = self.ui.recent_menu.addAction(
                "&{}. {}".format(row, foldername)
            )
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
        self.ui.pathEdit.setEnabled(mode == "Folder")
        self.ui.browseButton.setEnabled(mode == "Folder")
        self.update_treeview()

    def update_status(self):
        indexes = self.ui.treeView.selectionModel().selectedRows()
        indexes.sort()
        self.prev_indexes.sort()
        if indexes != self.prev_indexes:
            self.player.stop()
            path = (
                self.model.filePath(
                    self.sorting_model.mapToSource(self.ui.treeView.currentIndex())
                )
                if self.sorting_model
                else self.model.filePath(self.ui.treeView.currentIndex())
            )
            ftype = get_file_type(path)
            if isfile(path) and ftype in ("Audio", "Video", "Image"):
                file_url = (
                    QUrl.fromLocalFile(
                        self.model.filePath(
                            self.sorting_model.mapToSource(
                                self.ui.treeView.currentIndex()
                            )
                        )
                    )
                    if self.sorting_model
                    else QUrl.fromLocalFile(
                        self.model.filePath(self.ui.treeView.currentIndex())
                    )
                )
                if ftype == "Audio":  # TBD change this to audio file type
                    self.ui.playerLayout.setGeometry(QRect(0, 0, 0, 0))
                if ftype == "Image":
                    self.ui.playerLayout.update()
                self.player.setSource(file_url)
                self.player.play()
                self.player.pause()
                self.ui.mediaPlayButton.setVisible(ftype in ("Video", "Audio"))
                self.ui.mediaPositionSlider.setVisible(ftype in ("Video", "Audio"))
                self.ui.mediaVolumeDial.setVisible(ftype in ("Video", "Audio"))
                self.ui.mediaDurationLabel.setVisible(ftype in ("Video", "Audio"))
            else:
                self.ui.playerLayout.setGeometry(QRect(0, 0, 0, 0))
                self.ui.mediaPlayButton.setVisible(False)
                self.ui.mediaPositionSlider.setVisible(False)
                self.ui.mediaVolumeDial.setVisible(False)
                self.ui.mediaDurationLabel.setVisible(False)
        self.prev_indexes = indexes
        # TBD Review this
        num_selected = len(self.ui.treeView.selectionModel().selectedRows())
        self.ui.statusbar.showMessage(str(num_selected) + " item(s) selected")
        self.update_tag_checkboxes()

    def choose_path(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(
            self, "QFileDialog.getExistingDirectory()", self.ui.pathEdit.text(), options
        )
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
                self.sorting_model.mapFromSource(self.model.index(file_path, 0))
            )
            self.ui.pathEdit.setText(
                normpath(
                    self.model.filePath(
                        self.sorting_model.mapToSource(self.ui.treeView.rootIndex())
                    )
                )
            )
            if normpath(self.settings["current_folder"]) != normpath(file_path):
                self.settings["current_folder"] = file_path
                if file_path in self.settings["recent_folders"]:
                    self.settings["recent_folders"].remove(file_path)
                self.settings["recent_folders"].insert(0, file_path)
                if len(self.settings["recent_folders"]) > 15:
                    del self.settings["recent_folders"][-1]
                save_settings(self.settings)

    def manage_tags(self):
        self.tags_dialog = TagsDialog(self.tag_model)
        self.tags_dialog.exec()
        clear_tags_cache()
        self.init_tag_checkboxes()
        self.update_tag_checkboxes()

    def open(self):
        index = self.ui.treeView.currentIndex()
        if self.sorting_model:
            file_path = normpath(
                self.model.filePath(self.sorting_model.mapToSource(index))
            )
        else:
            file_path = normpath(self.model.filePath(index))
        if isdir(file_path):
            self.ui.statusbar.clearMessage()
            if not self.in_tagged_mode():
                self.model.setRootPath(normpath(file_path))
                if self.sorting_model:
                    self.ui.treeView.setRootIndex(
                        self.sorting_model.mapFromSource(self.model.index(file_path, 0))
                    )
                self.ui.pathEdit.setText(file_path)
                self.settings["current_folder"] = file_path
                if file_path in self.settings["recent_folders"]:
                    self.settings["recent_folders"].remove(file_path)
                self.settings["recent_folders"].insert(0, file_path)
                if len(self.settings["recent_folders"]) > 15:
                    del self.settings["recent_folders"][-1]
                save_settings(self.settings)
            else:
                # No-op in Tagged mode for folders
                pass
        else:
            # Open files in the system default application
            open_file(file_path)

    def create_folder(self):
        folder, ok = QInputDialog.getText(
            self, "Create new folder", "Enter folder name:", QLineEdit.Normal
        )
        if ok and folder != "":
            index = self.ui.treeView.currentIndex()
            # TBD this works a bit unexpectedly in "Tagged" mode - it creates a folder inside the parent folder, not the selected folder
            if self.sorting_model:
                full_path = (
                    Path(
                        self.model.filePath(self.sorting_model.mapToSource(index))
                    ).parent
                    / folder
                )
            else:
                full_path = Path(self.model.filePath(index)).parent / folder
            try:
                os.mkdir(full_path)
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", "Can't create this folder", QMessageBox.Ok
                )

    def context_menu(self, position):
        indexes = self.ui.treeView.selectionModel().selectedRows()
        if self.sorting_model:
            cur_selection = [
                normpath(self.model.filePath(self.sorting_model.mapToSource(index)))
                for index in indexes
            ]
        else:
            cur_selection = [normpath(self.model.filePath(index)) for index in indexes]

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
            cur_selection = [
                normpath(self.model.filePath(self.sorting_model.mapToSource(index)))
                for index in indexes
            ]
            source_indexes = [self.sorting_model.mapToSource(i) for i in indexes]
        else:
            cur_selection = [normpath(self.model.filePath(index)) for index in indexes]
            source_indexes = indexes

        if type(sender) == QCheckBox:
            for file_path in cur_selection:
                if state:  # checked
                    add_tag(file_path, sender.text())
                else:  # unchecked
                    remove_tag(file_path, sender.text())

        elif type(sender) == QComboBox:
            for file_path in cur_selection:
                if sender.currentText() == "":
                    remove_tags(
                        file_path,
                        [
                            sender.itemText(i)
                            for i in range(sender.count())
                            if sender.itemText(i) != ""
                        ],
                    )
                else:
                    remove_tags(
                        file_path,
                        [
                            sender.itemText(i)
                            for i in range(sender.count())
                            if sender.itemText(i) != ""
                        ],
                    )
                    add_tag(file_path, sender.currentText())

        # Refresh dock state immediately
        self.update_tag_checkboxes()

        # Refresh view/model cells for tag column immediately (multi-select too)
        try:
            if isinstance(self.model, TagFSModel):
                tag_col = self.model.columnCount() - 1
                for sidx in source_indexes:
                    if sidx.isValid():
                        left = self.model.index(sidx.row(), tag_col, sidx.parent())
                        self.model.dataChanged.emit(
                            left, left, [Qt.DisplayRole, Qt.BackgroundRole]
                        )
        except Exception:
            pass

        # Ensure repaint
        self.ui.treeView.viewport().update()


class TagFSModel(QFileSystemModel):
    def columnCount(self, parent=QModelIndex()):
        return super(TagFSModel, self).columnCount() + 1

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

        tags = (
            get_tags(normpath(self.filePath(index)))
            if role in (Qt.DisplayRole, Qt.BackgroundRole)
            else []
        )
        if index.column() == self.columnCount() - 1:
            if role == Qt.DisplayRole:
                return ", ".join(tags)
        if role == Qt.BackgroundRole and tags and tag_get_color(tags[0]):
            color = QColor()
            color.setRgba(tag_get_color(tags[0]))
            return color

        return super(TagFSModel, self).data(index, role)

    def flags(self, index):
        # Ensure items are draggable and droppable
        default = super(TagFSModel, self).flags(index)
        return default | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

    def dropMimeData(self, data, action, row, column, parent):
        if action not in (Qt.MoveAction, Qt.CopyAction):
            return False
        if not data.hasUrls():
            return False

        target_dir = self.filePath(parent) if parent.isValid() else self.rootPath()
        if not target_dir or not os.path.isdir(target_dir):
            return False

        success = True
        for url in data.urls():
            src_path = url.toLocalFile()
            if not src_path:
                continue
            base_name = os.path.basename(src_path)
            dst_path = os.path.normpath(os.path.join(target_dir, base_name))

            if os.path.normpath(src_path) == os.path.normpath(dst_path):
                continue

            from declutter.tags import get_tags, set_tags, remove_all_tags

            try:
                src_tags = []
                try:
                    src_tags = get_tags(os.path.normpath(src_path))
                except Exception:
                    src_tags = []

                import shutil

                if action == Qt.CopyAction:
                    # Copy
                    if os.path.isdir(src_path):
                        shutil.copytree(src_path, dst_path)
                    else:
                        shutil.copy2(src_path, dst_path)
                    # Tags: apply to copy; do NOT remove from source
                    try:
                        if src_tags:
                            set_tags(os.path.normpath(dst_path), src_tags)
                    except Exception:
                        pass
                else:
                    # Move
                    try:
                        os.rename(src_path, dst_path)
                    except OSError:
                        if os.path.isdir(src_path):
                            shutil.copytree(src_path, dst_path)
                            shutil.rmtree(src_path)
                        else:
                            shutil.copy2(src_path, dst_path)
                            os.remove(src_path)
                    # Tags: migrate
                    try:
                        if src_tags:
                            set_tags(os.path.normpath(dst_path), src_tags)
                        remove_all_tags(os.path.normpath(src_path))
                    except Exception:
                        pass

                # Refresh directories so view updates even on cross-dir operations
                src_parent = os.path.dirname(src_path)
                dst_parent = os.path.dirname(dst_path)
                if os.path.normpath(src_parent) == os.path.normpath(dst_parent):
                    self.directoryLoaded.emit(dst_parent)
                else:
                    self.directoryLoaded.emit(src_parent)
                    self.directoryLoaded.emit(dst_parent)

            except Exception:
                success = False

        return success


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
        if "conditions" in rule.keys() and rule["conditions"]:
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
            return self.sourceModel().size(source_left) < self.sourceModel().size(
                source_right
            )

        if source_left.column() == 3:
            return (
                self.sourceModel()
                .lastModified(source_left)
                .__le__(self.sourceModel().lastModified(source_right))
            )

        if (file_info1.isDir() and file_info2.isDir()) or (
            file_info1.isFile() and file_info2.isFile()
        ):
            return super().lessThan(source_left, source_right)

        return file_info1.isDir() and self.sortOrder() == Qt.SortOrder.AscendingOrder

    def filterAcceptsRow(self, source_row, source_parent):
        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        path = index.data(QFileSystemModel.FilePathRole)

        if (
            source_parent == source_model.index(source_model.rootPath())
            and self.filter_enabled
        ):
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
    seconds = (millis / 1000) % 60
    seconds = str(int(seconds))
    if len(seconds) == 1:
        seconds = "0" + seconds
    minutes = (millis / (1000 * 60)) % 60
    minutes = str(int(minutes))
    # if len(minutes) == 1:
    #     minutes = "0"+minutes
    hours = str(int((millis / (1000 * 60 * 60)) % 24))
    return (hours + ":" if hours != "0" else "") + minutes + ":" + seconds


def main():
    app = QApplication(sys.argv)
    window = TaggerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
