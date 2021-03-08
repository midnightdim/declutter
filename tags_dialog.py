import sys
from PySide6.QtUiTools import loadUiType

from PySide2.QtWidgets import QApplication, QDialog, QMessageBox, QInputDialog, QLineEdit, QColorDialog, QPushButton
from PySide2.QtCore import (Qt, QAbstractItemModel)
from PySide2.QtGui import QPalette, QColor, QStandardItemModel, QStandardItem
from ui_tags_dialog import Ui_tagsDialog
from tag_groups import TreeView, get_tree_selection_level, generate_tag_model
from declutter_lib import *
import logging


class TagsDialog(QDialog):
    def __init__(self, model):
        super(TagsDialog, self).__init__()
        self.ui = Ui_tagsDialog()
        self.ui.setupUi(self)               
        # self.model = QStandardItemModel()
        self.model = model
        # addItems(self.model, get_tags_and_groups())
        self.ui.addButton.clicked.connect(self.add_tag)
        self.ui.removeButton.clicked.connect(self.remove)
        self.ui.addGroupButton.clicked.connect(self.add_group)
        # self.ui.moveUpButton.clicked.connect(self.move_up)        
        # self.ui.moveDownButton.clicked.connect(self.move_down)
        self.ui.colorButton.clicked.connect(self.set_color)
        # self.ui.tagsList.doubleClicked.connect(self.rename_tag)
        self.ui.treeView.doubleClicked.connect(self.rename_tag)
        # create_tree_data(self.ui.treeView)
        self.model.itemChanged.connect(self.item_changed)
        # self.model.dataChanged.connect(self.data_changed)
        # self.model.rowsMoved.connect(self.rows_moved)

        self.load_tags()

    # def data_changed(self,left,right,vector):
    #     print('data changed')
    #     print(left,right,vector)
    #     print(self.model.itemFromIndex(left).text())
    #     print(self.model.itemFromIndex(right).text())
    #     # lists all top level items
    #     print(self.model.rowCount())
    #     for i in range(0,self.model.rowCount()):
    #         print(self.model.item(i).text())   


    # def rows_moved(self, parent, start, end, destination, row):
    #     print('rows moved')
    #     print(self.model.itemFromIndex(parent).text(), start, end, self.model.itemFromIndex(destination).text(), row)

    def item_changed(self, item):
        # print('changed')
        # print(item)
        print(item.text(),'index',item)

        item_data = item.data(Qt.UserRole)
        par = item.parent()
        par_data = par.data(Qt.UserRole) if par else {}
        if (item.text() != item_data['name']):
            print('renamed from',item_data['name'])
            # for i in range(0,par.rowCount()):
            #     print(i,par.child(i).text()) 
        elif item_data['type'] == 'tag' and item_data['group_id'] != par_data['id']:
            print('tag moved to group',par_data['name'])
            # for i in range(0,par.rowCount()):
            #     print(i,par.child(i).text())            
        elif item_data['type'] == 'tag' and item_data['group_id'] == par_data['id']:
            print('tag moved inside the group')
            # for i in range(0,par.rowCount()):
            #     print(i,par.child(i).text())
            #     print(i,par.child(i))
                # print(i,par.child(i).data(Qt.UserRole))
        elif item_data['type'] == 'group':
            print('group moved')
        
        self.ui.treeView
        # # lists all top level items
        # print(self.model.rowCount())
        # for i in range(0,self.model.rowCount()):
        #     print(self.model.item(i).text())        

        # print(self.model.rowCount())
        # par = item.parent()
        # # print(item.parent().text())
        # for i in range(0,par.rowCount()):
        #     print('child',i,par.child(i).text())
        # print(item.data(Qt.UserRole))


    def rename_tag(self): 
        cur_tag = self.ui.treeView.currentIndex().data()
        newtag, ok = QInputDialog.getText(self, "Rename tag",
            "Enter new name:", QLineEdit.Normal, cur_tag)            
        if ok and newtag != '' and newtag != cur_tag:
            # try:
            merge = False
            if newtag in get_all_tags():
                merge = QMessageBox.question(self, "Warning",
                    "This tag already exists, files tagged with '" + cur_tag + "' will be tagged with '" + newtag + "'.\nAre you sure you want to proceed?",
                    QMessageBox.Yes | QMessageBox.No)
            if newtag and merge in (QMessageBox.Yes,False):
                rename_tag(cur_tag,newtag)          
                self.load_tags()
            # except Exception as e:
            #     logging.exception(f'exception {e}')
        
    def set_color(self):        
        if self.ui.treeView.currentIndex().data(Qt.UserRole)['type'] == 'tag':
        # tag = self.ui.tagsList.itemFromIndex(self.ui.tagsList.selectedIndexes()[0]).text()
            tag = self.ui.treeView.currentIndex().data()
            # print(tag)
            cur_color = tag_get_color(tag)
            color = QColorDialog.getColor(QColor(cur_color) if cur_color is not None else Qt.green, self)
            if color.isValid():            
                self.ui.treeView.model().itemFromIndex(self.ui.treeView.currentIndex()).setData(color,Qt.BackgroundRole)
                # self.ui.tagsList.itemFromIndex(self.ui.tagsList.selectedIndexes()[0]).setBackground(color)

                tag_set_color(tag,color.rgb())

    def add_tag(self):
        tag, ok = QInputDialog.getText(self, "Add new tag",
        "Enter tag name:", QLineEdit.Normal)
        if ok and tag != '':
            create_tag(tag)
            #print("creating", tag)
        self.load_tags()

    def add_group(self):
        group, ok = QInputDialog.getText(self, "Add new group",
        "Enter group name:", QLineEdit.Normal)
        if ok and group != '':
            create_group(group)
            #print("creating", tag)
        self.model.appendRow(QStandardItem(group))
        # self.load_tags()

    def remove(self):
        if self.ui.treeView.currentIndex().data(Qt.UserRole)['type'] == 'tag':
            tag = self.ui.treeView.currentIndex().data()
            reply = QMessageBox.question(self, "Warning",
            "Are you sure you want to delete this tag:\n"+tag+"?",
            QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                delete_tag(tag)
                self.load_tags()
        else:
            group = self.ui.treeView.currentIndex().data(Qt.UserRole)
            if group['id'] == 1:
                QMessageBox.critical(self, "Can't do that", "You can't delete the default group, sorry.")
            else:
                msgBox = QMessageBox(QMessageBox.Question, "Question", "You're about to delete this group:\n"+group['name']+"\nWould you like to keep its tags (will be moved to Default group) or delete them all?")
                msgBox.addButton('Keep tags', QMessageBox.YesRole) #to default group
                msgBox.addButton('Delete tags', QMessageBox.NoRole)
                msgBox.addButton('Cancel', QMessageBox.RejectRole)
                
                reply = msgBox.exec_()
                # print(reply)
                if reply != 2: 
                    # print(reply)
                    delete_group(group['id'], not reply)
                # delete_tag(tag)
                self.load_tags()            

    def load_tags(self):        
        # self.ui.tagsList.clear()
        self.model.clear()
        generate_tag_model(self.model, get_tags_and_groups())
        self.ui.treeView.setModel(self.model)
        # create_tree_data(self.ui.treeView)
        self.ui.treeView.expandAll()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TagsDialog()
    window.show()

    sys.exit(app.exec_())