import sys
from PySide6.QtUiTools import loadUiType

from PySide2.QtWidgets import QApplication, QDialog, QMessageBox, QInputDialog, QLineEdit, QColorDialog, QPushButton
from PySide2.QtCore import (Qt, QAbstractItemModel)
from PySide2.QtGui import QPalette, QColor, QStandardItemModel, QStandardItem, QIcon
from ui_tags_dialog import Ui_tagsDialog
from tag_tree import TagTree, get_tree_selection_level
from declutter_lib import *
import logging


class TagsDialog(QDialog):
    def __init__(self, model = QStandardItemModel()):
        super(TagsDialog, self).__init__()
        self.ui = Ui_tagsDialog()
        self.ui.setupUi(self)               
        # self.model = QStandardItemModel()
        self.model = model
        # self.print_model()
        # addItems(self.model, get_tags_and_groups())
        self.ui.addButton.clicked.connect(self.add_tag)
        self.ui.removeButton.clicked.connect(self.remove)
        self.ui.addGroupButton.clicked.connect(self.add_group)
        # self.ui.moveUpButton.clicked.connect(self.move_up)        
        # self.ui.moveDownButton.clicked.connect(self.move_down)
        self.ui.colorButton.clicked.connect(self.set_color)
        # self.ui.tagsList.doubleClicked.connect(self.rename_tag)
        self.ui.treeView.doubleClicked.connect(self.rename)     
        # self.model.dataChanged.connect(self.data_changed)
        # self.model.rowsMoved.connect(self.rows_moved)

        # self.model.itemChanged.connect(self.item_changed) # TBD this can be used for in-place editing
        self.ui.treeView.setModel(self.model)
        self.ui.treeView.expandAll()
        self.ui.treeView.setExpandsOnDoubleClick(False)

        # self.load_tags()

    # def print_model(self):
    #     for i in range(0,self.model.rowCount()):
    #     # i = 0
    #     # for group in data.keys():
    #         group = self.model.item(i).data(Qt.UserRole)
    #         print('group:',group['name'])
    #         for k in range(0,self.model.item(i).rowCount()):
    #             tag = self.model.item(i).child(k).data(Qt.UserRole)
    #             print('tag:',tag['name'])

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

    # def item_changed(self, item):  # TBD this can be used for in-place editing
    #     item_data = item.data(Qt.UserRole)
    #     par = item.parent()
    #     par_data = par.data(Qt.UserRole) if par else {}
    #     if (item.text() != item_data['name']):
    #         print('renamed from',item_data['name'])
    #         # for i in range(0,par.rowCount()):
    #         #     print(i,par.child(i).text()) 
    #     elif item_data['type'] == 'tag' and item_data['group_id'] != par_data['id']:
    #         print('tag moved to group',par_data['name'])
    #         # for i in range(0,par.rowCount()):
    #         #     print(i,par.child(i).text())            
    #     elif item_data['type'] == 'tag' and item_data['group_id'] == par_data['id']:
    #         print('tag moved inside the group')
    #         # for i in range(0,par.rowCount()):
    #         #     print(i,par.child(i).text())
    #         #     print(i,par.child(i))
    #             # print(i,par.child(i).data(Qt.UserRole))
    #     elif item_data['type'] == 'group':
    #         print('group moved')
        
    #     self.ui.treeView
    #     # # lists all top level items
    #     # print(self.model.rowCount())
    #     # for i in range(0,self.model.rowCount()):
    #     #     print(self.model.item(i).text())

    def rename(self):
        cur_item = self.ui.treeView.currentIndex().data(Qt.UserRole)
        if cur_item['type'] == 'tag':
            cur_tag = cur_item['name']
            newtag, ok = QInputDialog.getText(self, "Rename tag",
                "Enter new name:", QLineEdit.Normal, cur_tag)            
            if ok and newtag != '' and newtag != cur_tag:
                # try:
                merge = False
                if newtag in get_all_tags(): # TBD use model data instead?
                    merge = QMessageBox.question(self, "Warning",
                        "This tag already exists, files tagged with '" + cur_tag + "' will be tagged with '" + newtag + "'.\nAre you sure you want to proceed?",
                        QMessageBox.Yes | QMessageBox.No)
                if newtag and merge in (QMessageBox.Yes,False):
                    rename_tag(cur_tag,newtag)          
                    cur_item['name'] = newtag
                    self.model.itemFromIndex(self.ui.treeView.currentIndex()).setData(cur_item,Qt.UserRole)                    
                    self.model.itemFromIndex(self.ui.treeView.currentIndex()).setData(newtag,Qt.DisplayRole)
                    # self.load_tags()
                # except Exception as e:
                #     logging.exception(f'exception {e}')
        else: # group
            group = cur_item['name']
            other_groups = [self.model.item(i).data(Qt.UserRole)['name'] for i in range(0,self.model.rowCount())]
            # print(other_groups)
            other_groups.remove(group)
            newgroup, ok = QInputDialog.getText(self, "Rename group",
                "Enter new name:", QLineEdit.Normal, group)
            if ok and newgroup != '' and newgroup != group:
                if newgroup in other_groups:
                    QMessageBox.information(self, "Can't do that", "Another group with this name already exists. Please choose a different name.")
                else:
                    rename_group(group,newgroup)
                    # print('renaming')
                    cur_item['name'] = newgroup
                    self.model.itemFromIndex(self.ui.treeView.currentIndex()).setData(cur_item,Qt.UserRole)
                    self.model.itemFromIndex(self.ui.treeView.currentIndex()).setData(newgroup,Qt.DisplayRole)
                    # self.ui.treeView.setModel(self.model)
                # try:
                    # if newgroup in get_all_tags():
                    #     merge = QMessageBox.question(self, "Warning",
                    #         "This tag already exists, files tagged with '" + group + "' will be tagged with '" + newgroup + "'.\nAre you sure you want to proceed?",
                    #         QMessageBox.Yes | QMessageBox.No)
                    # if newgroup == QMessageBox.Yes:
                        # rename_tag(cur_tag,newtag)          
                    # self.load_tags()
        
    def set_color(self):        
        if self.ui.treeView.currentIndex().data(Qt.UserRole)['type'] == 'tag':
        # tag = self.ui.tagsList.itemFromIndex(self.ui.tagsList.selectedIndexes()[0]).text()
            tag = self.ui.treeView.currentIndex().data()
            # print(tag)
            cur_color = None
            if tag_get_color(tag):
                cur_color = QColor()
                cur_color.setRgba(tag_get_color(tag))

            color = QColorDialog.getColor(cur_color if cur_color is not None else Qt.gray, self, "Select color", QColorDialog.ShowAlphaChannel)
            if color.isValid():            
                self.ui.treeView.model().itemFromIndex(self.ui.treeView.currentIndex()).setData(color,Qt.BackgroundRole)
                # self.ui.tagsList.itemFromIndex(self.ui.tagsList.selectedIndexes()[0]).setBackground(color)
                tag_set_color(tag,color.rgba())
                tag_data = self.ui.treeView.currentIndex().data(Qt.UserRole)
                print(tag_data)
                tag_data['color'] = color.rgba()
                self.model.itemFromIndex(self.ui.treeView.currentIndex()).setData(tag_data,Qt.UserRole)

    def add_tag(self):
        group_id = 1
        if self.ui.treeView.currentIndex().data() and self.ui.treeView.currentIndex().data(Qt.UserRole)['type'] == 'group':
            group_id = self.ui.treeView.currentIndex().data(Qt.UserRole)['id']
        tag, ok = QInputDialog.getText(self, "Add new tag",
        "Enter tag name:", QLineEdit.Normal)
        if ok and tag != '':
            create_tag(tag,group_id)
            #print("creating", tag)
        self.reload_model() # TBD can do this without reloading model

    def add_group(self):
        group, ok = QInputDialog.getText(self, "Add new group",
        "Enter group name:", QLineEdit.Normal)
        if ok and group != '':
            id = create_group(group)
            #print("creating", tag)
            gr_item = QStandardItem(group)
            gr_item.setData({'name':group,'name_shown':group,'type':'group','id':id}, Qt.UserRole)
            self.model.appendRow(gr_item)
        # self.reload_model()

    def remove(self):
        if self.ui.treeView.currentIndex().data(Qt.UserRole)['type'] == 'tag':
            tag = self.ui.treeView.currentIndex().data()
            reply = QMessageBox.question(self, "Warning",
            "Are you sure you want to delete this tag:\n"+tag+"?",
            QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                delete_tag(tag)
                item = self.model.itemFromIndex(self.ui.treeView.currentIndex())
                self.model.removeRow(item.row(), self.model.indexFromItem(item.parent()))
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
                self.reload_model()            

    def reload_model(self):        
        # self.ui.tagsList.clear()
        self.model.clear()
        generate_tag_model(self.model, get_tags_and_groups())
        # self.ui.treeView.setModel(self.model)
        self.ui.treeView.expandAll()

# generates the model used in tagger dock widget, tags selection for filtering and tags manager
def generate_tag_model(model, data, groups_selectable = True):
    for group in data.keys():
        item = QStandardItem(group)
        item.setData(group,Qt.DisplayRole)
        item.setData(data[group], Qt.UserRole)
        item.setEditable(False)  # TBD can change this in the future to make in-place editing
        item.setSelectable(groups_selectable)
        item.setIcon(QIcon(u":/images/icons/folder.svg"))
        model.appendRow(item)
        if 'tags' in data[group].keys():
            for tag in data[group]['tags']:
                tag_item = QStandardItem(tag['name'])
                tag_item.setData(tag['name'], Qt.DisplayRole)
                tag_item.setData(tag, Qt.UserRole)
                if tag['color']:
                    color = QColor()
                    color.setRgba(tag['color'])
                    tag_item.setData(color,Qt.BackgroundRole)
                tag_item.setDropEnabled(False)
                tag_item.setEditable(False)  # TBD can change this in the future to make in-place editing
                item.appendRow(tag_item)
                # for f in get_files_by_tag(tag['name']):
                #     tag_item.appendRow(QStandardItem(f))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TagsDialog()
    window.show()

    sys.exit(app.exec_())