from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from declutter_lib import get_tags_and_groups

ICON_LVL_CLIENT = "img/icons8-bank-16.png"

# DATA = {'group1':{'type':'group','id':1,'list_order':1,'tags':[{'name':'tag1','type':'tag','id':1,'list_order':1},{'name':'tag2','type':'tag','id':2,'list_order':2},{'name':'tag3','type':'tag','id':3,'list_order':3}]}}
# print(DATA)
DATA = get_tags_and_groups()

def create_tree_data(tree):
    model = QStandardItemModel()
    addItems(model, DATA)
    tree.setModel(model)

def addItems(parent, data):
    for group in data.keys():
        item = QStandardItem(group)
        item.setData(data[group], Qt.UserRole)
        print(item.data())
        parent.appendRow(item)
        if 'tags' in data[group].keys():
            for tag in data[group]['tags']:
                tag_item = QStandardItem(tag['name'])
                tag_item.setData(tag, Qt.UserRole)
                print(tag_item.data())
                tag_item.setDropEnabled(False)
                item.appendRow(tag_item)

def get_tree_selection_level(index):
    level = 0
    while index.parent().isValid():
        index = index.parent()
        level += 1

    return level

class TreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        self.setHeaderHidden(True)
        self.setColumnHidden(1, True)
        self.setSelectionMode(self.SingleSelection)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        # self.expandAll()

    # def paintEvent(self,event):
    #     position = self.dropIndicatorPosition()
    #     self.setDropIndicatorShown(position == QAbstractItemView.BelowItem or position == QAbstractItemView.AboveItem)
    #     super().paintEvent(event)

#     setDropIndicatorShown( position == QAbstractItemView::BelowItem || position == QAbstractItemView::AboveItem );
#     base_t::paintEvent( event );
#     setDropIndicatorShown( true );
# }

    def dragMoveEvent(self, event):
        tree = event.source()        

        sParent: str = ""
        par_ix = tree.selectedIndexes()[0]
        # if par_ix.isValid():
        #     sParent = par_ix.data()
        #     print("par. item: ", sParent, get_tree_selection_level(par_ix))

        to_index = self.indexAt(event.pos())
        # print( self.item to_index)
        print(to_index.data(Qt.UserRole))
        # print(to_index.parent == par_ix)
        # print('selected',par_ix)
        # print('target',to_index)
        # print('parent',par_ix.parent())
        # print(to_index == par_ix.parent())
        # if to_index.isValid():
        #     print("to:", to_index.data(), get_tree_selection_level(to_index))

        super().dragMoveEvent(event)
        position = self.dropIndicatorPosition()
        # print(position)
        #  or not ((sParent and get_tree_selection_level(par_ix) < get_tree_selection_level(to_index)) or (sParent=="" and get_tree_selection_level(to_index)==0))
        # sParent == "" - it's a group, <>"" - tag
        # print('sparent:',sParent)
        # print('par_ix',get_tree_selection_level(par_ix))
        # print('to_index',get_tree_selection_level(to_index))

        # disallow dropping groups into tags
        # disallow dropping groups into groups, tags into tags - allow only placement on one level
        # allow dropping tags only into groups
        # disallow dropping tag to its parent group
        if (get_tree_selection_level(par_ix) < get_tree_selection_level(to_index)) or \
            (get_tree_selection_level(par_ix) == get_tree_selection_level(to_index) and position != QAbstractItemView.BelowItem and position != QAbstractItemView.AboveItem) or \
            (get_tree_selection_level(par_ix) > get_tree_selection_level(to_index) and position != QAbstractItemView.OnItem) or to_index == par_ix.parent():
            event.ignore()    

        # if (position != QAbstractItemView.BelowItem and position != QAbstractItemView.AboveItem and not sParent):
        #     event.ignore()
    

    def dropEvent(self, event):
        # tree = event.source() 
        to_index = self.indexAt(event.pos())
        position = self.dropIndicatorPosition()

        par_ix = self.selectedIndexes()[0]
        if par_ix.isValid():
            sParent = par_ix.data()
            print("moved: ", sParent, get_tree_selection_level(par_ix))

        to_index = self.indexAt(event.pos())
        if to_index.isValid():
            print("to:", to_index.data(), get_tree_selection_level(to_index))
        print(position)

        super().dropEvent(event)
        self.setExpanded(to_index, True)

    # def dropEvent(self, event):
    #     tree = event.source()        

    #     if self.viewport().rect().contains(event.pos()):

    #         sParent: str = ""
    #         par_ix = tree.selectedIndexes()[0].parent()
    #         # if par_ix.isValid():
    #         #     sParent = par_ix.data()
    #         #     print("par. item: ", sParent, get_tree_selection_level(par_ix))

    #         to_index = self.indexAt(event.pos())
    #         # if to_index.isValid():
    #         #     print("to:", to_index.data(), get_tree_selection_level(to_index))

    #         # print(sParent)
    #         # print(get_tree_selection_level(to_index))
    #         # if sParent and get_tree_selection_level(to_index) == 1:
    #         if (sParent and get_tree_selection_level(par_ix) < get_tree_selection_level(to_index)) or (sParent=="" and get_tree_selection_level(to_index)==0):
    #             super().dropEvent(event)
    #             self.setExpanded(to_index, True)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()        

    def initUI(self):
        centralwidget = QWidget()
        self.setCentralWidget(centralwidget)

        hBox = QHBoxLayout(centralwidget)        

        self.treeView = TreeView(centralwidget)       

        hBox.addWidget(self.treeView)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    create_tree_data(window.treeView)
    # window.treeView.expand(window.treeView.model().index(0, 0))  # expand the System-Branch
    # window.treeView.setDragDropMode(QAbstractItemView.InternalMove)
    window.treeView.expandAll()
    window.setGeometry(400, 400, 500, 400)
    window.show()

    app.exec_()