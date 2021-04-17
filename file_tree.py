from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from declutter_lib import get_tags, set_tags, remove_all_tags
from os import path
from pathlib import Path

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
        print('drag leave')
        self.parent().parent().player.stop()
        self.parent().parent().playlist.clear()        

    # def dragMoveEvent(self, event):      
        # print('drag')
        # print(self.parent().parent().player)

    def dropEvent(self, event):
        # tree = event.source()
        to_index = self.indexAt(event.pos())
        new_path = path.normpath(self.model().sourceModel().filePath(self.model().mapToSource(to_index)))
        new_path = Path(new_path).parent.absolute() if not path.isdir(new_path) else new_path
        if self.parent().parent().player:
            self.parent().parent().player.stop()
            self.parent().parent().playlist.clear()
        # print(new_path)
        for url in event.mimeData().urls():
            old_path = path.normpath(url.toLocalFile())
            tags = get_tags(old_path)
            # print(tags)
            new_path = path.join(new_path,path.basename(old_path))
            # new_path = path.normpath(path.join(self.model().sourceModel().rootPath(),path.basename(old_path)))
            # print('about to copy tags from',old_path,'to',new_path,':',tags)
            # print(new_path)
            if new_path != old_path and not Path(new_path).exists(): # don't copy tags if target file exists because it won't be moved
                # print('copied')
                # TBD add this to logging
                set_tags(path.normpath(new_path),tags)
                remove_all_tags(old_path)
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

    app.exec_()