from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeView, QAbstractItemView, QMainWindow, QWidget, QHBoxLayout, QApplication
from declutter.tags import get_tags, set_tags, remove_all_tags
from os import path
from pathlib import Path
import logging


class FileTree(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def dragLeaveEvent(self, event):
        self.parent().parent().player.stop()

    def dropEvent(self, event):
        # this allows copying and moving files from/to tagger windows and Explorer windows
        position = self.dropIndicatorPosition()
        if not (position == QAbstractItemView.BelowItem or position == QAbstractItemView.AboveItem):
            to_index = self.indexAt(event.pos())
            target_folder = path.normpath(
                self.model().sourceModel().filePath(self.model().mapToSource(to_index)))
            if target_folder == '.':
                target_folder = path.normpath(
                    self.model().sourceModel().rootPath())
            target_folder = Path(target_folder).parent.absolute(
            ) if not path.isdir(target_folder) else target_folder
            if self.parent().parent().player:
                self.parent().parent().player.stop()
                self.parent().parent().playlist.clear()
            for url in event.mimeData().urls():
                old_path = path.normpath(url.toLocalFile())
                tags = get_tags(old_path)
                new_path = path.join(target_folder, path.basename(old_path))
                # don't copy tags if target file exists because it won't be moved
                if tags and new_path != old_path and not Path(new_path).exists():
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
    window.treeView.expandAll()
    window.setGeometry(400, 400, 500, 400)
    window.show()

    app.exec()
