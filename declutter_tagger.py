import sys
from PySide6.QtGui import QIcon, QColor, QCursor, QAction
from PySide6.QtWidgets import QWidget, QApplication, QMainWindow, QFileSystemModel, QFileIconProvider, QMenu, QAbstractItemView
from PySide6.QtWidgets import QWidgetAction, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QDialog, QFileDialog, QListWidget, QDialogButtonBox, QSpacerItem
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
        self.settings = load_settings()
        self.checkAction = {}  # checkboxes in context menu
        self.tag_checkboxes = {} # checkboxes in the dock widget

        self.ui.actionNone1 = QAction(self)
        #self.ui.actionNone1.setObjectName(u"actionNone1")
        # self.ui.actionNone1.setText(r"C:\Users\DIM\AppData\Roaming\DeClutter\Users\DIM\AppData\Roaming\DeClutter\Users\DIM\AppData\Roaming\DeClutter\Users\DIM\AppData\Roaming\DeClutter")
        # self.ui.actionNone1.triggered.connect(self.open_recent)
        self.ui.recent_menu.aboutToShow.connect(self.update_recent_menu)
        self.ui.recent_menu.triggered.connect(self.open_file_from_recent)
        #self.ui.menuRecent_folders.addAction(self.ui.actionNone1)
        #self.actionNone.setEnabled(False)

        path = self.settings['current_folder'] if 'current_folder' in self.settings.keys() and self.settings['current_folder'] != '' else normpath(QDir.homePath())
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

        # self.setStyleSheet("QDockWidget::title {position: relative; top: 100px;}")
        # self.setStyleSheet("QMainWindow::separator{ margin: 100px;}");
        
        self.init_tag_checkboxes()
        self.update_ui()

    # def open_recent(self):
    #     sender = self.sender()
    #     print('open recent', sender)

    def mouseDoubleClickEvent(self, event):  # TBD maybe remove this
        widget = self.childAt(event.pos())
        if widget is not None and widget.objectName() == "scrollAreaWidgetContents":
            self.manage_tags()

    def init_tag_checkboxes(self):
        for t in self.tag_checkboxes:
            self.ui.tagsLayout.takeAt(self.ui.tagsLayout.indexOf(self.tag_checkboxes[t]))
            self.tag_checkboxes[t].deleteLater()
            # self.tag_checkboxes[t].hide()
            # self.tag_checkboxes[t].destroy()
        
        self.tag_checkboxes = {}
        for t in get_all_tags():
            self.tag_checkboxes[t] = QCheckBox(t)
            self.ui.tagsLayout.addWidget(self.tag_checkboxes[t])
            self.tag_checkboxes[t].stateChanged.connect(self.set_tags)

            if tag_get_color(t):
                self.tag_checkboxes[t].setPalette(QColor(tag_get_color(t)))
                self.tag_checkboxes[t].setAutoFillBackground(True)  

    def update_tag_checkboxes(self):
        indexes = self.ui.treeView.selectedIndexes()
        cur_selection = [normpath(self.model.filePath(self.sorting_model.mapToSource(index))) for index in indexes]

        all_files_tags = []
        for f in cur_selection:  # TBD v3 not the most efficient procedure maybe
            all_files_tags.extend(get_tags(f))
      
        for t in get_all_tags():
            if t not in all_files_tags:
                self.tag_checkboxes[t].setTristate(False)
                self.tag_checkboxes[t].setChecked(False)
            elif all_files_tags.count(t) < len(cur_selection):
                self.tag_checkboxes[t].setTristate(True)
                self.tag_checkboxes[t].setCheckState(Qt.CheckState.PartiallyChecked)
            else:
                self.tag_checkboxes[t].setChecked(True)

    def update_recent_menu(self):
        self.ui.recent_menu.clear()
        for row, foldername in enumerate(self.settings['recent_folders'], 1):
            recent_action = self.ui.recent_menu.addAction('&{}. {}'.format(
                row, foldername))
            recent_action.setData(foldername)

    def open_file_from_recent(self, action):
        #self.open_file(action.data())
        self.ui.pathEdit.setText(normpath(action.data()))
        self.change_path()

    def dir_loaded(self):
        #print("dir loaded")
        if self.ui.sourceComboBox.currentText() == "Tag(s)":
            self.ui.treeView.expandAll()

    def update_filter_tags(self):
        # print(self.filter_tags)
        # print(self.filter_tags_checkboxes)
        for t in self.filter_tags_checkboxes:
            self.ui.horizontalLayout.takeAt(self.ui.horizontalLayout.indexOf(self.filter_tags_checkboxes[t]))    
            self.filter_tags_checkboxes[t].deleteLater()
        self.filter_tags_checkboxes = {}
        self.filter_tags.reverse()
        for t in self.filter_tags:            
            self.filter_tags_checkboxes[t] = QCheckBox(t)
            if tag_get_color(t):
                self.filter_tags_checkboxes[t].setPalette(QColor(tag_get_color(t)))
                self.filter_tags_checkboxes[t].setAutoFillBackground(True)            
            self.filter_tags_checkboxes[t].setChecked(True)
            self.filter_tags_checkboxes[t].stateChanged.connect(self.update_treeview)
            self.ui.horizontalLayout.insertWidget(1,self.filter_tags_checkboxes[t])
        self.update_treeview()

    # def apply_filter_tags(self):
          
    #     all_tags=[]
    #     for t in self.filter_tags_checkboxes:
    #         if self.filter_tags_checkboxes[t].isChecked():
    #             all_tags.append(t)
    #     self.sorting_model.filter_tags = all_tags
    #     self.update_treeview()

    def select_tags(self):
        tags_dialog = QDialog()
        tags_dialog.setWindowTitle("Select Tags")
        listWidget = QListWidget(tags_dialog)
        #listWidget.addItems(get_all_tags())
        for t in get_all_tags():
            listWidget.addItem(t)
            color = tag_get_color(t)
            if color:
                listWidget.item(listWidget.count()-1).setBackground(QColor(color))

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
        tags_dialog.setWindowIcon(QIcon('DeClutter.ico'))
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
        if mode in ('Folder', 'Folder & tags'):
            for t in self.filter_tags_checkboxes:
                self.ui.horizontalLayout.takeAt(self.ui.horizontalLayout.indexOf(self.filter_tags_checkboxes[t]))    
                self.filter_tags_checkboxes[t].deleteLater()                
                # self.filter_tags_checkboxes[t].hide()
                # self.filter_tags_checkboxes[t].destroy()
                # self.filter_tags_checkboxes[t].setVisible(False)
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
            self.sorting_model.recalc_tagged_paths(True)
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
            self.sorting_model.recalc_tagged_paths()
            # print(self.sorting_model.filter_tags)
            # print(self.sorting_model.tagged_paths)

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
        self.update_tag_checkboxes()

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
            if normpath(self.settings['current_folder']) != normpath(file_path):
                self.settings['current_folder'] = file_path
                if file_path in self.settings['recent_folders']:
                    self.settings['recent_folders'].remove(file_path)
                self.settings['recent_folders'].insert(0,file_path)
                if len(self.settings['recent_folders'])>15:
                    del self.settings['recent_folders'][-1]
            save_settings(SETTINGS_FILE,self.settings)

    def manage_tags(self):
        self.tags_dialog = TagsDialog()
        self.tags_dialog.exec_()
        self.init_tag_checkboxes()
        self.update_tag_checkboxes()

    def open(self):
        index = self.ui.treeView.currentIndex()
        #file_path = normpath(self.model.filePath(index))
        file_path = normpath(self.model.filePath(self.sorting_model.mapToSource(index)))
        if os.path.isdir(file_path):
            self.ui.statusbar.clearMessage()
            self.model.setRootPath(normpath(file_path)) # TBD reuse this in a function
            self.ui.treeView.setRootIndex(self.sorting_model.mapFromSource(self.model.index(file_path)))
            self.ui.pathEdit.setText(file_path)
            self.settings['current_folder'] = file_path
            save_settings(SETTINGS_FILE,self.settings)
        elif os.path.isfile(file_path):
            os.startfile(file_path)

    def context_menu(self, position):
        #index = self.ui.treeView.currentIndex()
        indexes = self.ui.treeView.selectedIndexes()
        cur_selection = [normpath(self.model.filePath(self.sorting_model.mapToSource(index))) for index in indexes]

        all_files_tags = []
        for f in cur_selection:  # TBD v3 not the most efficient procedure maybe
            all_files_tags.extend(get_tags(f))

        menu = QMenu()
        
        self.checkAction = {}
        for t in get_all_tags():
            self.checkAction[t] = CheckBoxAction(self,t)           
            self.checkAction[t].checkbox.stateChanged.connect(self.set_tags)
            #print(t)
            # if t in file_tags:
            #     self.checkAction[t].checkbox.setCheckState(Qt.CheckState.Checked)
            #     self.checkAction[t].checkbox.setChecked(True)
            if t not in all_files_tags:
                pass
                #window[r].update(text = CHAR_UNCHECKED + " " + r)
            elif all_files_tags.count(t) < len(cur_selection):
                self.checkAction[t].checkbox.setTristate(True)
                self.checkAction[t].checkbox.setCheckState(Qt.CheckState.PartiallyChecked)
            else:
                self.checkAction[t].checkbox.setChecked(True)


            menu.addAction(self.checkAction[t])

        cursor = QCursor()
        menu.exec_(cursor.pos())

    def set_tags(self, state):
        sender = self.sender()
        # print("clicked",state)
        # index = self.ui.treeView.currentIndex()
        # file_path = normpath(self.model.filePath(self.sorting_model.mapToSource(index)))      
        
        indexes = self.ui.treeView.selectedIndexes()
        cur_selection = [normpath(self.model.filePath(self.sorting_model.mapToSource(index))) for index in indexes]

        for file_path in cur_selection:
            if state == 2: #checked
                #print("tagged",file_path,"with",sender.text())
                add_tag(file_path,sender.text())
            elif state == 0: #unchecked
                remove_tag(file_path,sender.text())

        self.update_tag_checkboxes()

class TagFSModel(QFileSystemModel):
    def columnCount(self, parent = QModelIndex()):
        return super(TagFSModel, self).columnCount()+1
    
    def headerData(self, section, orientation, role):
        if section == 4 and role == Qt.DisplayRole:
            return "Tag(s)"
        else:
            return super(TagFSModel, self).headerData(section, orientation, role)        

    def data(self, index, role):
        # if index.column() == 0: #displays full path instead of the name
        #     if role == Qt.DisplayRole:
        #         return self.filePath(index)
        if index.column() == self.columnCount() - 1:
            if role == Qt.DisplayRole:
                #return self.fileName(index)
                return ', '.join(get_tags(normpath(self.filePath(index))))
            if role == Qt.TextAlignmentRole:
                return Qt.AlignLeft
        if role == Qt.BackgroundRole and get_tags(normpath(self.filePath(index))) and tag_get_color(get_tags(normpath(self.filePath(index)))[0]):
            #return QColor("#ccffff")
            return QColor(tag_get_color(get_tags(normpath(self.filePath(index)))[0]))

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
        if tag_get_color(text):
            self.checkbox.setPalette(QColor(tag_get_color(text)))
            self.checkbox.setAutoFillBackground(True)
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
        self.tagged_paths = []

    def recalc_tagged_paths(self, tree=False):
        # print('tagged_paths called')
        all_paths=[]
        # print('here')
        # print(self.filter_tags)
        for t in self.filter_tags:
            all_paths = list(set(all_paths + get_files_by_tag(t)))
        # print(all_paths)
        if not tree:
            self.tagged_paths = all_paths
            return
        for t in all_paths:
            if str(Path(t).parent).lower() not in all_paths:
                all_paths.append(str(Path(t).parent).lower())
        # print(all_paths)
        #return all_paths
        self.tagged_paths = all_paths

    def lessThan(self, source_left: QModelIndex, source_right: QModelIndex):
        file_info1 = self.sourceModel().fileInfo(source_left)
        file_info2 = self.sourceModel().fileInfo(source_right)

        #print(self.sourceModel() )
        
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
            return normpath(path).lower() in self.tagged_paths
        elif self.mode == "Folder & tags" and source_parent == source_model.index(source_model.rootPath()):
            source_model = self.sourceModel()
            index = source_model.index(source_row, 0, source_parent)
            path = index.data(QFileSystemModel.FilePathRole)
            # print(normpath(path).lower())
            # if normpath(path).lower() in self.tagged_paths():
            #     # print(normpath(path))
            #     return True
            # #print(self.tagged_paths())
            return normpath(path).lower() in self.tagged_paths
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