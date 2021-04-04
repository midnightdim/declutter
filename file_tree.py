from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from declutter_lib import get_tags, set_tags
from os import path

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

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            old_path = path.normpath(url.toLocalFile())
            tags = get_tags(old_path)
            # print(tags)
            new_path = path.join(self.model().sourceModel().rootPath(),path.basename(old_path))
            # print(new_path)
            set_tags(path.normpath(new_path),tags)
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