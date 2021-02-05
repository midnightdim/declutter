import sys
from PySide6.QtGui import QIcon, QColor, QCursor
from PySide6.QtWidgets import QWidget, QApplication, QMainWindow, QFileSystemModel, QFileIconProvider, QMenu, QAbstractItemView, QWidgetAction
from PySide6.QtCore import QObject, QDir, Qt, QModelIndex
from ui_tagger_window import Ui_taggerWindow
from declutter_lib import *
from os.path import normpath

class TaggerWindow(QMainWindow):
    def __init__(self):
        super(TaggerWindow, self).__init__()
        self.ui = Ui_taggerWindow()
        self.ui.setupUi(self)
        self.ui.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.treeView.customContextMenuRequested.connect(self.context_menu)

        self.populate()

    def populate(self):
        path = r"D:\DIM\WinFiles\Downloads"
        self.model = TagFSModel()
        #self.model = QFileSystemModel()
        self.model.setRootPath((QDir.rootPath()))
        self.model.sort(0,Qt.SortOrder.DescendingOrder)
        #self.model.setFilter(QDir.AllDirs | QDir.NoDot)
        #self.model.sort(QDir.DirsFirst)
        self.ui.treeView.setModel(self.model)
        self.ui.treeView.setRootIndex(self.model.index(path))
        self.model.setIconProvider(QFileIconProvider())
        self.ui.treeView.setItemsExpandable(False)
        self.ui.treeView.header().resizeSection(0,350)
        #self.ui.treeView.header().setSortIndicator(1, Qt.DescendingOrder)
        self.ui.treeView.setSortingEnabled(True)
        self.ui.treeView.setRootIsDecorated(False)
        self.ui.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        #self.ui.treeView.resizeColumnToContents(0)  # doesn't work for some reason

    def context_menu(self, position):
        index = self.ui.treeView.currentIndex()
        file_path = normpath(self.model.filePath(index))
        file_tags = get_tags(file_path)
        #print(file_tags)
        menu = QMenu()
        open = menu.addAction(file_path)
        for t in get_all_tags():
            open = menu.addAction(t)
            open.setCheckable(True)
            if t in file_tags:
                open.setChecked(True)
            #open.triggered.connect(self.tag_files)
        cursor = QCursor()
        menu.exec_(cursor.pos())

    def tag_files(self):
        print("tagging")

class TagFSModel(QFileSystemModel):
    def columnCount(self, parent = QModelIndex()):
        return super(TagFSModel, self).columnCount()+1

    def data(self, index, role):
        if index.column() == self.columnCount() - 1:
            if role == Qt.DisplayRole:
                #return self.fileName(index)
                return ','.join(get_tags(normpath(self.filePath(index))))
            if role == Qt.TextAlignmentRole:
                return Qt.AlignLeft
        if role == Qt.BackgroundRole and get_tags(normpath(self.filePath(index))):
            return QColor("#ccffff")                

        return super(TagFSModel, self).data(index, role)

#class CheckBoxAction(QWidgetAction):



def main():
    app = QApplication(sys.argv)
    #QApplication.setQuitOnLastWindowClosed(False)

    window = TaggerWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()