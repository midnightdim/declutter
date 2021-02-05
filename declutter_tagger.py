import sys
from PySide6.QtGui import QIcon, QColor, QCursor, QAction
from PySide6.QtWidgets import QWidget, QApplication, QMainWindow, QFileSystemModel, QFileIconProvider, QMenu, QAbstractItemView, QWidgetAction, QHBoxLayout, QLabel, QCheckBox
from PySide6.QtCore import QObject, QDir, Qt, QModelIndex
from ui_tagger_window import Ui_taggerWindow
from declutter_lib import *
from os.path import normpath
from pathlib import Path

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
        #path = str(Path.home() / "Downloads")
        #path = r"G:\QUIK_VTB"
        #path = ""
        #path = r"D:\DIM\WinFiles\Downloads"
        #path = normpath(r"D:\Projects.other\Programming\DeClutter archive\test")
        #path = Path(path)
        #print(path)
        self.model = TagFSModel()
        #self.model = QFileSystemModel()
        self.model.setRootPath(path)
        self.model.setFilter(QDir.AllEntries | QDir.NoDot)
        self.model.sort(0,Qt.SortOrder.AscendingOrder)
        #self.model.setFilter(QDir.AllDirs | QDir.NoDot)
        #self.model.sort(QDir.DirsFirst)
        self.ui.treeView.setModel(self.model)
        self.ui.treeView.setRootIndex(self.model.index(path))
        self.model.setIconProvider(QFileIconProvider())
        self.ui.treeView.setItemsExpandable(False)
        self.ui.treeView.header().resizeSection(0,350)
        self.ui.treeView.header().setSortIndicator(0, Qt.AscendingOrder)
        self.ui.treeView.setSortingEnabled(True)
        self.ui.treeView.setRootIsDecorated(False)
        self.ui.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        #self.ui.treeView.resizeColumnToContents(0)  # doesn't work for some reason
        self.ui.treeView.doubleClicked.connect(self.open)
        self.checkAction = {}

    def open(self):
        index = self.ui.treeView.currentIndex()
        file_path = normpath(self.model.filePath(index))
        if os.path.isdir(file_path):
            self.model.setRootPath(file_path)
            self.ui.treeView.setRootIndex(self.model.index(file_path))
        elif os.path.isfile(file_path):
            os.startfile(file_path)

    def context_menu(self, position):
        index = self.ui.treeView.currentIndex()
        file_path = normpath(self.model.filePath(index))
        file_tags = get_tags(file_path)
        #print(file_tags)
        menu = QMenu()
        #open = menu.addAction(file_path)
        #checkAction = CheckBoxAction(self,"test")
        #checkAction.checkbox.setTristate()
        #open = menu.addAction(checkAction)
        
        self.checkAction = {}
        for t in get_all_tags():
            self.checkAction[t] = CheckBoxAction(self,t)           
            #self.checkAction[t].checkbox.checked.connect(self.test)
            #self.checkAction[t].checkbox.unchecked.connect(self.test)
            self.checkAction[t].checkbox.stateChanged.connect(self.test)
            #open = menu.addAction(t)
            #open.setCheckable(True)
            if t in file_tags:
                #open.setChecked(True)
                self.checkAction[t].checkbox.setChecked(True)                
            menu.addAction(self.checkAction[t])
            #open.triggered.connect(self.tag_files)
        cursor = QCursor()
        menu.exec_(cursor.pos())

    def test(self, state):
        sender = self.sender()
        #print("clicked",state)
        index = self.ui.treeView.currentIndex()
        file_path = normpath(self.model.filePath(index))        
        if state == 2: #checked
            print("tagged",file_path,"with",sender.text())
            add_tag(file_path,sender.text())
        elif state == 0: #unchecked
            remove_tag(file_path,sender.text())
    def tag_files(self):
        print("tagging")

class TagFSModel(QFileSystemModel):
    def columnCount(self, parent = QModelIndex()):
        return super(TagFSModel, self).columnCount()+1

    def data(self, index, role):
        if index.column() == self.columnCount() - 1:
            if role == Qt.DisplayRole:
                #return self.fileName(index)
                return ', '.join(get_tags(normpath(self.filePath(index))))
            if role == Qt.TextAlignmentRole:
                return Qt.AlignLeft
        if role == Qt.BackgroundRole and get_tags(normpath(self.filePath(index))):
            return QColor("#ccffff")                

        return super(TagFSModel, self).data(index, role)

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

def main():
    app = QApplication(sys.argv)
    #QApplication.setQuitOnLastWindowClosed(False)

    window = TaggerWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()