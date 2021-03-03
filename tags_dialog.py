import sys
from PySide2.QtUiTools import loadUiType

from PySide2.QtWidgets import QApplication, QDialog, QMessageBox, QInputDialog, QLineEdit, QColorDialog
from PySide2.QtCore import (Qt, QAbstractItemModel)
from PySide2.QtGui import QPalette, QColor
from ui_tags_dialog import Ui_tagsDialog
from declutter_lib import *
import logging


class TagsDialog(QDialog):
    def __init__(self):
        super(TagsDialog, self).__init__()
        self.ui = Ui_tagsDialog()
        self.ui.setupUi(self)        
        self.load_tags()

        self.ui.addButton.clicked.connect(self.add_tag)
        self.ui.removeButton.clicked.connect(self.remove_tag)
        self.ui.moveUpButton.clicked.connect(self.move_up)        
        self.ui.moveDownButton.clicked.connect(self.move_down)
        self.ui.colorButton.clicked.connect(self.set_color)
        self.ui.tagsList.doubleClicked.connect(self.rename_tag)

    def rename_tag(self):
        cur_tag = self.ui.tagsList.itemFromIndex(self.ui.tagsList.currentIndex()).text()
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
        tag = self.ui.tagsList.itemFromIndex(self.ui.tagsList.selectedIndexes()[0]).text()
        cur_color = tag_get_color(tag)
        color = QColorDialog.getColor(QColor(cur_color) if cur_color is not None else Qt.green, self)
        if color.isValid():            
            self.ui.tagsList.itemFromIndex(self.ui.tagsList.selectedIndexes()[0]).setBackground(color)
            tag_set_color(tag,color.rgb())

    def add_tag(self):
        tag, ok = QInputDialog.getText(self, "Add new tag",
        "Enter tag name:", QLineEdit.Normal)
        if ok and tag != '':
            create_tag(tag)
            #print("creating", tag)
        self.load_tags()

    def remove_tag(self):
        tag = self.ui.tagsList.itemFromIndex(self.ui.tagsList.selectedIndexes()[0]).text()
        reply = QMessageBox.question(self, "Warning",
        "Are you sure you want to delete this tag:\n"+tag+"?",
        QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            delete_tag(tag)
            self.load_tags()

    def move_up(self):
        tag = self.ui.tagsList.itemFromIndex(self.ui.tagsList.selectedIndexes()[0]).text()
        move_tag(tag, 'up')
        self.load_tags()

    def move_down(self):
        tag = self.ui.tagsList.itemFromIndex(self.ui.tagsList.selectedIndexes()[0]).text()
        move_tag(tag, 'down')
        self.load_tags()

    def load_tags(self):
        self.ui.tagsList.clear()
        #self.ui.tagsList.addItems(get_all_tags())
        #self.setStyleSheet("QListWidget::item:selected {color:black; image: url(icons/checkmark.svg); image-position: right;}")
        for t in get_all_tags():
            self.ui.tagsList.addItem(t)
            color = tag_get_color(t)
            if color:
                self.ui.tagsList.item(self.ui.tagsList.count()-1).setBackground(QColor(color))

        #self.setStyleSheet("QListWidget::item:selected {image: url(icons/checkmark.svg); image-position: right; color: red; border: 2px solid black; font: bold;}")
        
        #self.ui.tagsList.setStyleSheet("QListWidget::item:selected {font-weight: bold; color: red; border: 3px solid black;} QListWidget {show-decoration-selected: 1;}")
        #print(self.ui.tagsList.styleSheet())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TagsDialog()
    window.show()

    sys.exit(app.exec_())