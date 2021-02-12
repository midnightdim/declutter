import sys
from PySide6.QtGui import QIcon, QColor, QCursor, QAction
from PySide6.QtWidgets import QWidget, QApplication, QMainWindow, QFileSystemModel, QFileIconProvider, QMenu, QAbstractItemView, QWidgetAction, QHBoxLayout, QLabel, QCheckBox, QDialog, QFileDialog
from PySide6.QtCore import QObject, QDir, Qt, QModelIndex
from ui_tagger_window import Ui_taggerWindow
from tags_dialog import TagsDialog
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
        #path = r"D:\DIM\WinFiles\Downloads"
        settings = load_settings()
        path = settings['current_folder'] if 'current_folder' in settings.keys() and settings['current_folder'] != '' else normpath(QDir.homePath())
        self.model = TagFSModel()
        #self.model = QFileSystemModel()
        self.model.setRootPath(path)
        self.model.setFilter(QDir.NoDot | QDir.AllEntries)
        self.model.sort(0,Qt.SortOrder.AscendingOrder)
        #self.model.setHeaderData(4,)
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
        self.ui.actionManage_Tags.triggered.connect(self.manage_tags)
        self.checkAction = {}
        self.ui.pathEdit.setText(path)
        self.ui.pathEdit.returnPressed.connect(self.change_path)
        self.ui.browseButton.clicked.connect(self.choose_path)

    def choose_path(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
            "QFileDialog.getExistingDirectory()",
            self.ui.pathEdit.text(), options)
        if directory:
            self.ui.pathEdit.setText(normpath(directory))
            self.change_path()

    def change_path(self):
        file_path = self.ui.pathEdit.text()
        if os.path.isdir(file_path):
            self.model.setRootPath(normpath(file_path)) # TBD reuse this in a function
            self.ui.treeView.setRootIndex(self.model.index(file_path))
            self.ui.pathEdit.setText(file_path)            
            settings = load_settings()
            settings['current_folder'] = file_path
            save_settings(SETTINGS_FILE,settings)

    def manage_tags(self):
        self.tags_dialog = TagsDialog()
        self.tags_dialog.exec_()

    def open(self):
        index = self.ui.treeView.currentIndex()
        file_path = normpath(self.model.filePath(index))
        if os.path.isdir(file_path):
            self.model.setRootPath(normpath(file_path)) # TBD reuse this in a function
            self.ui.treeView.setRootIndex(self.model.index(file_path))
            self.ui.pathEdit.setText(file_path)            
            settings = load_settings()
            settings['current_folder'] = file_path
            save_settings(SETTINGS_FILE,settings)
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
    
    def headerData(self, section, orientation, role):
        if section == 4 and role == Qt.DisplayRole:
            return "Tag(s)"
        else:
            return super(TagFSModel, self).headerData(section, orientation, role)        

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