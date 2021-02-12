import sys
from PySide6.QtUiTools import loadUiType

from PySide6.QtWidgets import QApplication, QDialog, QMessageBox, QInputDialog, QLineEdit
from PySide6.QtCore import (Qt, QAbstractItemModel)
from ui_tags_dialog import Ui_tagsDialog
from declutter_lib import get_all_tags, create_tag, delete_tag, move_tag


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
        self.ui.tagsList.addItems(get_all_tags())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TagsDialog()
    window.show()

    sys.exit(app.exec_())