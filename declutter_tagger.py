import sys
from PySide6.QtGui import QIcon, QColor, QCursor, QAction
from PySide6.QtWidgets import QWidget, QApplication, QMainWindow, QFileSystemModel, QFileIconProvider, QMenu, QAbstractItemView
from PySide6.QtWidgets import QWidgetAction, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QDialog, QFileDialog, QListWidget, QDialogButtonBox
from PySide6.QtCore import QObject, QDir, Qt, QModelIndex, QSortFilterProxyModel
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
        self.filter_tags = []
        self.filter_tags_checkboxes = {}

        self.populate()

    def populate(self):
        #path = r"D:\DIM\WinFiles\Downloads"
        settings = load_settings()
        self.checkAction = {}  # TBD what's this?

        path = settings['current_folder'] if 'current_folder' in settings.keys() and settings['current_folder'] != '' else normpath(QDir.homePath())
        #path = r"D:\Projects.other\Mikhail Beloglazov"
        #path = r"D:\DIM\WinFiles\Downloads"
        #path = r"."
        
        self.model = TagFSModel()
        #self.model = QFileSystemModel()
        self.model.setRootPath(path)
        self.model.setFilter(QDir.NoDot | QDir.AllEntries)
        self.model.sort(0,Qt.SortOrder.AscendingOrder)

        self.sorting_model = SortingModel()
        self.sorting_model.mode = "Folder"
        #self.sorting_model.filter_paths = []
        self.sorting_model.setSourceModel(self.model)

        self.ui.treeView.setModel(self.sorting_model)
        self.ui.treeView.setRootIndex(self.sorting_model.mapFromSource(self.model.index(path)))

        self.model.setIconProvider(QFileIconProvider())
              
        self.ui.treeView.header().resizeSection(0,350)
        
        #self.ui.treeView.header().setSortIndicator(0, Qt.AscendingOrder)
        
        # self.ui.treeView.setSortingEnabled(True)
        # self.ui.treeView.setRootIsDecorated(False)
        # self.ui.treeView.setItemsExpandable(False)        
                
        self.ui.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        #self.ui.treeView.resizeColumnToContents(0)  # doesn't work for some reason
        self.ui.treeView.clicked.connect(self.update_status)
        self.ui.treeView.doubleClicked.connect(self.open)
        self.ui.actionManage_Tags.triggered.connect(self.manage_tags)

        self.ui.pathEdit.setText(path)
        self.ui.pathEdit.returnPressed.connect(self.change_path)
        self.ui.browseButton.clicked.connect(self.choose_path)
        self.ui.sourceComboBox.currentIndexChanged.connect(self.update_ui)
        self.ui.selectTagsButton.clicked.connect(self.select_tags)
        self.model.directoryLoaded.connect(self.dir_loaded)
        self.update_ui()

    # def update_filter_paths(self):
    #     all_paths = []
    #     for t in self.filter_tags_checkboxes:
    #         if self.filter_tags_checkboxes[t].isChecked():
    #             all_tags = list(set(all_paths + get_files_by_tag(t)))
    #         for t in all_tags:
    #             if str(Path(t).parent).lower() not in all_tags:
    #                 all_tags.append(str(Path(t).parent).lower())
    #     print(all_paths)

    def dir_loaded(self):
        #print("dir loaded")
        if self.ui.sourceComboBox.currentText() == "Tag(s)":
            self.ui.treeView.expandAll()

    def update_filter_tags(self):
        for t in self.filter_tags_checkboxes:
            self.filter_tags_checkboxes[t].destroy()
            self.filter_tags_checkboxes[t].setVisible(False)
        self.filter_tags.reverse()
        for t in self.filter_tags:            
            self.filter_tags_checkboxes[t] = QCheckBox(t)
            self.filter_tags_checkboxes[t].setChecked(True)
            self.filter_tags_checkboxes[t].stateChanged.connect(self.apply_filter_tags)
            self.ui.horizontalLayout.insertWidget(1,self.filter_tags_checkboxes[t])
        self.apply_filter_tags()

    def apply_filter_tags(self):
        # all_paths = []
        # for t in self.filter_tags_checkboxes:
        #     if self.filter_tags_checkboxes[t].isChecked():
        #         all_paths = list(set(all_paths + get_files_by_tag(t)))
        #     for t in all_paths:
        #         if str(Path(t).parent).lower() not in all_paths:
        #             all_paths.append(str(Path(t).parent).lower())
        
        
        all_tags=[]
        for t in self.filter_tags_checkboxes:
            if self.filter_tags_checkboxes[t].isChecked():
                all_tags.append(t)
        self.sorting_model.filter_tags = all_tags
        #print(all_paths)
        self.update_treeview()

    def select_tags(self):
        tags_dialog = QDialog()
        tags_dialog.setWindowTitle("Select Tags")
        listWidget = QListWidget(tags_dialog)
        listWidget.addItems(get_all_tags())
        listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        layout = QVBoxLayout(tags_dialog)
        layout.addWidget(listWidget)        
        buttonBox = QDialogButtonBox(tags_dialog)
        buttonBox.setObjectName(u"buttonBox")
        buttonBox.setOrientation(Qt.Horizontal)
        buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(tags_dialog.accept)
        buttonBox.rejected.connect(tags_dialog.reject)

        layout.addWidget(buttonBox)

        tags_dialog.setLayout(layout)
        tags_dialog.listWidget = listWidget
        #print(tags_dialog.layout().listWidget)
        
        if tags_dialog.exec_():
            self.filter_tags = [tags_dialog.listWidget.item(row).text() for row in range(0,tags_dialog.listWidget.count()) if tags_dialog.listWidget.item(row).isSelected()]
            self.update_filter_tags()

    def update_ui(self):
        mode = self.ui.sourceComboBox.currentText()
        #self.sorting_model.mode = mode
        # print('mode',self.sorting_model.mode)
        self.ui.selectTagsButton.setVisible(mode in ('Folder & tags', 'Tag(s)'))
        self.ui.pathEdit.setEnabled(mode in ('Folder', 'Folder & tags'))
        self.ui.browseButton.setEnabled(mode in ('Folder', 'Folder & tags'))
        if mode == 'Folder':
            for t in self.filter_tags_checkboxes:
                self.filter_tags_checkboxes[t].destroy()
                self.filter_tags_checkboxes[t].setVisible(False)
            self.filter_tags = {}
        self.update_treeview()

    def update_treeview(self):
        #print('updating treeview')
        #print(self.sorting_model.filter_paths)
        all_tags=[]
        for t in self.filter_tags_checkboxes:
            if self.filter_tags_checkboxes[t].isChecked():
                all_tags.append(t)
        self.sorting_model.filter_tags = all_tags
        mode = self.ui.sourceComboBox.currentText()
        # self.sorting_model.mode = mode
        if mode == 'Tag(s)': # TBD simplify this
            #print('tags')
            self.model = TagFSModel()
            path = "."
            self.model.setRootPath(path)
            self.model.setFilter(QDir.NoDotAndDotDot | QDir.AllEntries)           
            self.model.sort(0,Qt.SortOrder.AscendingOrder)

            #path = load_settings()['current_folder']            
            #print('path',path)
            self.sorting_model = SortingModel()
            self.sorting_model.setSourceModel(self.model)            
            self.sorting_model.mode = mode
            self.sorting_model.filter_tags = all_tags
            # self.ui.treeView.setRootIndex(self.model.index(path))
            self.ui.treeView.setModel(self.sorting_model)
            self.ui.treeView.setRootIndex(self.sorting_model.mapFromSource(self.model.index(path)))           
            self.model.setIconProvider(QFileIconProvider())
            self.ui.treeView.header().setSortIndicator(0, Qt.AscendingOrder)                        
            self.ui.treeView.setItemsExpandable(True)
            self.ui.treeView.setRootIsDecorated(True)            
            self.ui.treeView.expandAll()
            self.model.directoryLoaded.connect(self.dir_loaded)
            #self.ui.treeView.expand(self.sorting_model.mapFromSource(self.model.index(path)))
        else:
            #print('not tags')
            self.model = TagFSModel()            
            path = load_settings()['current_folder']            
            self.model.setRootPath(path)
            self.model.setFilter(QDir.NoDot | QDir.AllEntries)
            self.model.sort(0,Qt.SortOrder.AscendingOrder)
            self.sorting_model = SortingModel()
            self.sorting_model.mode = mode            
            self.sorting_model.filter_tags = all_tags
            self.sorting_model.setSourceModel(self.model)
            self.ui.treeView.setModel(self.sorting_model)            
            self.ui.treeView.setRootIndex(self.sorting_model.mapFromSource(self.model.index(path)))            
            self.model.setIconProvider(QFileIconProvider())
            self.ui.treeView.header().setSortIndicator(0, Qt.AscendingOrder)
            self.ui.treeView.setItemsExpandable(False)
            self.ui.treeView.setRootIsDecorated(False)

    def update_status(self):
        num_selected = int(len(self.ui.treeView.selectedIndexes())/5)
        self.ui.statusbar.showMessage(str(num_selected)+" item(s) selected")

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
            self.ui.statusbar.clearMessage()
            self.model.setRootPath(normpath(file_path)) # TBD reuse this in a function
            self.ui.treeView.setRootIndex(self.sorting_model.mapFromSource(self.model.index(file_path)))
            self.ui.pathEdit.setText(file_path)            
            settings = load_settings()
            settings['current_folder'] = file_path
            save_settings(SETTINGS_FILE,settings)

    def manage_tags(self):
        self.tags_dialog = TagsDialog()
        self.tags_dialog.exec_()

    def open(self):
        index = self.ui.treeView.currentIndex()
        #file_path = normpath(self.model.filePath(index))
        file_path = normpath(self.model.filePath(self.sorting_model.mapToSource(index)))
        if os.path.isdir(file_path):
            self.ui.statusbar.clearMessage()
            self.model.setRootPath(normpath(file_path)) # TBD reuse this in a function
            self.ui.treeView.setRootIndex(self.sorting_model.mapFromSource(self.model.index(file_path)))
            self.ui.pathEdit.setText(file_path)
            settings = load_settings()
            settings['current_folder'] = file_path
            save_settings(SETTINGS_FILE,settings)
        elif os.path.isfile(file_path):
            os.startfile(file_path)

    def context_menu(self, position):
        index = self.ui.treeView.currentIndex()
        file_path = normpath(self.model.filePath(self.sorting_model.mapToSource(index)))
        file_tags = get_tags(file_path)
        # print(file_tags)
        menu = QMenu()
        
        self.checkAction = {}
        for t in get_all_tags():
            self.checkAction[t] = CheckBoxAction(self,t)           
            self.checkAction[t].checkbox.stateChanged.connect(self.set_tags)
            #print(t)
            if t in file_tags:
                #print('setting checked')
                #print(self.checkAction[t].checkbox.isChecked())
                self.checkAction[t].checkbox.setCheckState(Qt.CheckState.Checked)
                self.checkAction[t].checkbox.setChecked(True)
                # print('set')           
            # print('1')
            menu.addAction(self.checkAction[t])
            # print('2')

        cursor = QCursor()
        menu.exec_(cursor.pos())

    def set_tags(self, state):
        sender = self.sender()
        #print("clicked",state)
        index = self.ui.treeView.currentIndex()
        file_path = normpath(self.model.filePath(self.sorting_model.mapToSource(index)))      
        if state == 2: #checked
            #print("tagged",file_path,"with",sender.text())
            add_tag(file_path,sender.text())
        elif state == 0: #unchecked
            remove_tag(file_path,sender.text())

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

class SortingModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = ""
        self.filter_tags = []

    def tagged_paths(self, tree=False):
        all_paths=[]
        for t in self.filter_tags:
            all_paths = list(set(all_paths + get_files_by_tag(t)))
        if not tree:
            return all_paths
        for t in all_paths:
            if str(Path(t).parent).lower() not in all_paths:
                all_paths.append(str(Path(t).parent).lower())
        # print(all_paths)
        return all_paths

    def lessThan(self, source_left: QModelIndex, source_right: QModelIndex):
        file_info1 = self.sourceModel().fileInfo(source_left)
        file_info2 = self.sourceModel().fileInfo(source_right)       
        
        if file_info1.fileName() == "..":
            return self.sortOrder() == Qt.SortOrder.AscendingOrder

        if file_info2.fileName() == "..":
            return self.sortOrder() == Qt.SortOrder.DescendingOrder
                
        if (file_info1.isDir() and file_info2.isDir()) or (file_info1.isFile() and file_info2.isFile()):
            return super().lessThan(source_left, source_right)

        return file_info1.isDir() and self.sortOrder() == Qt.SortOrder.AscendingOrder

    def filterAcceptsRow(self, source_row, source_parent):
        # print(self.mode)
        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        path = index.data(QFileSystemModel.FilePathRole)

        if self.mode == "Tag(s)": # and source_parent == source_model.index(source_model.rootPath()):
            # print(normpath(path))
            return normpath(path).lower() in self.tagged_paths(True)
        elif self.mode == "Folder & tags" and source_parent == source_model.index(source_model.rootPath()):
            source_model = self.sourceModel()
            index = source_model.index(source_row, 0, source_parent)
            path = index.data(QFileSystemModel.FilePathRole)
            # print(normpath(path))
            if normpath(path).lower() in self.tagged_paths():
                # print(normpath(path))
                return True
            #print(self.tagged_paths())
            return normpath(path).lower() in self.tagged_paths()
        else:
            return True

def main():
    app = QApplication(sys.argv)
    #QApplication.setQuitOnLastWindowClosed(False)

    window = TaggerWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()