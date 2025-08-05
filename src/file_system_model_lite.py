import os.path as osp
from os.path import normpath
import posixpath
from typing import Any, List, Union

from PySide6.QtGui import QColor
from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt, QDateTime, QLocale, QFileInfo, QMimeDatabase, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeView, QFileIconProvider, QFileSystemModel, QAbstractItemView
from declutter.tags import get_files_by_tag, get_tags, tag_get_color, get_all_files_from_db
from declutter.file_utils import get_actual_filename

FSMItemOrNone = Union["_FileSystemModelLiteItem", None]

class _FileSystemModelLiteItem(object):
    """Represents a single node (drive, folder or file) in the tree"""

    def __init__(
        self,
        data: List[Any],
        path: str = '',
        icon=QFileIconProvider.Computer,
        parent: FSMItemOrNone = None,
    ):
        self._data: List[Any] = data
        self._icon = icon
        self._path = path
        self._parent: _FileSystemModelLiteItem = parent
        self.child_items: List[_FileSystemModelLiteItem] = []

    def append_child(self, child: "_FileSystemModelLiteItem"):
        self.child_items.append(child)

    def child(self, row: int) -> FSMItemOrNone:
        try:
            return self.child_items[row]
        except IndexError:
            return None

    def child_count(self) -> int:
        return len(self.child_items)

    def column_count(self) -> int:
        return len(self._data)

    def data(self, column: int) -> Any:
        try:
            return self._data[column]
        except IndexError:
            return None

    def path(self) -> str:
        return self._path

    def icon(self):
        return self._icon

    def row(self) -> int:
        if self._parent:
            return self._parent.child_items.index(self)
        return 0

    def parent_item(self) -> FSMItemOrNone:
        return self._parent


class FileSystemModelLite(QAbstractItemModel):
    def __init__(self, file_list: List[str], parent=None, **kwargs):
        """Initializes the FileSystemModelLite with a list of files."""
        super().__init__(parent, **kwargs)

        self._icon_provider = QFileIconProvider()

        self._root_item = _FileSystemModelLiteItem(
            ["Name", "Size", "Type", "Date Modified", "Tags"]
        )
        self._setup_model_data(file_list, self._root_item)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        item: _FileSystemModelLiteItem = index.internalPointer()
        if role == Qt.DisplayRole and index.column() < 4:
            return item.data(index.column())
        elif role == Qt.DisplayRole and index.column() == 4:
            return ', '.join(get_tags(normpath(item.path())))
        elif index.column() == 0 and role == Qt.DecorationRole:
            return self._icon_provider.icon(item.icon())
        elif role == Qt.BackgroundRole and get_tags(normpath(item.path())) and tag_get_color(get_tags(normpath(item.path()))[0]):
            color = QColor()
            color.setRgba(tag_get_color(get_tags(normpath(item.path()))[0]))
            return color
        return None

    def sort(self, column, order=Qt.AscendingOrder):
        return super().sort(column, order)

    def filePath(self, index: QModelIndex):
        if not index.isValid():
            return None

        item: _FileSystemModelLiteItem = index.internalPointer()
        return item.path()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        return super().flags(index)

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole
    ) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._root_item.data(section)
        return None

    def index(
        self, row: int, column: int, parent: QModelIndex = QModelIndex()
    ) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self._root_item
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child_item: _FileSystemModelLiteItem = index.internalPointer()
        parent_item: FSMItemOrNone = child_item.parent_item()

        if parent_item == self._root_item:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item = self._root_item
        else:
            parent_item = parent.internalPointer()

        return parent_item.child_count()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return parent.internalPointer().column_count()
        return self._root_item.column_count()

    def _setup_model_data(
        self, file_list: List[str], parent: "_FileSystemModelLiteItem"
    ):
        def _add_to_tree(_file_record, _parent: "_FileSystemModelLiteItem", root=False):
            """Recursively adds file records to the tree structure."""
            item_name = _file_record["bits"].pop(0)
            for child in _parent.child_items:
                if item_name == child.data(0):
                    item = child
                    break
            else:
                data = [item_name, "", "", "", ""]
                if root:
                    icon = QFileInfo(item_name)
                    full_path = item_name
                elif len(_file_record["bits"]) == 0:
                    full_path = _file_record['path']
                    icon = QFileInfo(_file_record['path'])
                    data = [
                        item_name,
                        _file_record["size"],
                        _file_record["type"],
                        _file_record["modified_at"],
                        _file_record["tags"]
                    ]
                else:
                    full_path = _parent._path+"\\"+item_name
                    icon = QFileInfo(full_path)

                item = _FileSystemModelLiteItem(
                    data, full_path, icon=icon, parent=_parent)
                _parent.append_child(item)

            if len(_file_record["bits"]):
                _add_to_tree(_file_record, item)

        db = QMimeDatabase()
        for file in file_list:
            # TBD: if not actual: actual = str(Path(file).resolve()) # this is dangerous in case of symlinks

            time = QDateTime().fromMSecsSinceEpoch(int(osp.getmtime(file) * 1000))
            file_record = {
                "path": file,
                "size": QLocale().formattedDataSize(osp.getsize(file)),
                "modified_at": time.toString(QLocale.system().dateTimeFormat(QLocale.ShortFormat)),
                "type": db.mimeTypeForFile(file).comment(),
                "tags": ", ".join(get_tags(normpath(file)))
            }

            drive = True
            if "\\" in file:
                file = posixpath.join(*file.split("\\"))
            bits = file.split("/")
            if len(bits) > 1 and bits[0] == "":
                bits[0] = "/"
                drive = False

            file_record["bits"] = bits
            _add_to_tree(file_record, parent, drive)


class Widget(QWidget):
    """A simple widget to demonstrate the FileSystemModelLite."""
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        file_list = get_all_files_from_db()
        self._fileSystemModel = FileSystemModelLite(file_list, self)

        layout = QVBoxLayout(self)

        self._treeView = QTreeView(self)
        self._treeView.setModel(self._fileSystemModel)
        self._treeView.setSortingEnabled(True)
        self._treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._treeView.header().resizeSection(0, 350)
        self._treeView.expandAll()
        layout.addWidget(self._treeView)


if __name__ == "__main__":
    from sys import argv, exit
    from PySide6.QtWidgets import QApplication

    a = QApplication(argv)
    w = Widget()
    w.setGeometry(200, 200, 1000, 600)
    w.show()
    exit(a.exec())
