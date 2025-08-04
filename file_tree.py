from PySide6.QtCore import Qt
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QTreeView, QAbstractItemView, QMainWindow, QWidget, QHBoxLayout, QApplication
from declutter_lib import get_tags, set_tags, remove_all_tags
from os import path
from pathlib import Path
import logging


class FileTree(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
    #     self.initUI()

    # def initUI(self):
    #     self.setHeaderHidden(True)
    #     self.setColumnHidden(1, True)
    #     self.setSelectionMode(self.SingleSelection)
    #     self.setDragDropMode(QAbstractItemView.InternalMove)

    # def dragMoveEvent(self, event):
    #     tree = event.source()

    def dragLeaveEvent(self, event):
        # print('drag leave')
        self.parent().parent().player.stop()
        self.parent().parent().playlist.clear()

    # def dragMoveEvent(self, event):
        # print('drag')
        # print(self.parent().parent().player)

    def dropEvent(self, event):
        # this allows copying and moving files from/to tagger windows and Explorer windows
        # tree = event.source()
        position = self.dropIndicatorPosition()
        if not (position == QAbstractItemView.BelowItem or position == QAbstractItemView.AboveItem):
            to_index = self.indexAt(event.pos())
            target_folder = path.normpath(
                self.model().sourceModel().filePath(self.model().mapToSource(to_index)))
            if target_folder == '.':
                # print(path.normpath(self.model().sourceModel().filePath(self.model().sourceModel().rootIndex())))
                target_folder = path.normpath(
                    self.model().sourceModel().rootPath())
            # print(target_folder)
            target_folder = Path(target_folder).parent.absolute(
            ) if not path.isdir(target_folder) else target_folder
            if self.parent().parent().player:
                self.parent().parent().player.stop()
                self.parent().parent().playlist.clear()
            # print(new_path)
            for url in event.mimeData().urls():
                old_path = path.normpath(url.toLocalFile())
                tags = get_tags(old_path)
                # print(tags)
                new_path = path.join(target_folder, path.basename(old_path))
                # print(old_path,new_path)
                # new_path = path.normpath(path.join(self.model().sourceModel().rootPath(),path.basename(old_path)))
                # print('about to copy tags from',old_path,'to',new_path,':',tags)
                # print(new_path)
                # don't copy tags if target file exists because it won't be moved
                if tags and new_path != old_path and not Path(new_path).exists():
                    # print('copied')
                    # TBD add this to logging
                    set_tags(path.normpath(new_path), tags)
                    action = 'copied'
                    if event.dropAction() == Qt.MoveAction:
                        action = 'moved'
                        remove_all_tags(old_path)
                    print("File {}: {} to {}, {} tags {}".format(
                        action, old_path, new_path, action, tags))
                    logging.debug("File {}: {} to {}, {} tags {}".format(
                        action, old_path, new_path, action, tags))
        # print(self.rootIndex())
        # print(self.model().sourceModel().rootPath())
        # print(self.model().sourceModel().filePath(self.model().sourceModel().rootIndex()))

        super().dropEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        centralwidget = QWidget()
        self.setCentralWidget(centralwidget)

        hBox = QHBoxLayout(centralwidget)

        self.treeView = FileTree(centralwidget)

        hBox.addWidget(self.treeView)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    # window.treeView.expand(window.treeView.model().index(0, 0))  # expand the System-Branch
    # window.treeView.setDragDropMode(QAbstractItemView.InternalMove)
    window.treeView.expandAll()
    window.setGeometry(400, 400, 500, 400)
    window.show()

    app.exec()
