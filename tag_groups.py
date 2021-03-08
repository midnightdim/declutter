from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from declutter_lib import *

ICON_LVL_CLIENT = "img/icons8-bank-16.png" #TBD add icons

# DATA = {'group1':{'type':'group','id':1,'list_order':1,'tags':[{'name':'tag1','type':'tag','id':1,'list_order':1},{'name':'tag2','type':'tag','id':2,'list_order':2},{'name':'tag3','type':'tag','id':3,'list_order':3}]}}
# print(DATA)
# DATA = get_tags_and_groups()

def create_tree_data(tree):
    model = QStandardItemModel()
    generate_tag_model(model, get_tags_and_groups())
    tree.setModel(model)

def generate_tag_model(model, data):
    for group in data.keys():
        item = QStandardItem(group)
        item.setData(data[group], Qt.UserRole)
        # print(item.data())
        model.appendRow(item)
        if 'tags' in data[group].keys():
            for tag in data[group]['tags']:
                tag_item = QStandardItem(tag['name'])
                # tag_item.setCheckable(True)
                # tag_item.setEditable(False)
                tag_item.setData(tag, Qt.UserRole)
                if tag['color']:
                    tag_item.setData(QColor(tag['color']),Qt.BackgroundRole)
                # print(tag_item.data())
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
        # self.setEditTriggers(QAbstractItemView.NoEditTriggers)
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
        # sParent: str = ""
        par_ix = tree.selectedIndexes()[0]
        # if par_ix.isValid():
        #     sParent = par_ix.data()
        #     print("par. item: ", sParent, get_tree_selection_level(par_ix))

        to_index = self.indexAt(event.pos())
        # print( self.item to_index)
        # print(to_index.data(Qt.UserRole))
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
        # if par_ix.isValid():
        #     sParent = par_ix.data()
        #     print("moved: ", sParent, get_tree_selection_level(par_ix))

        to_index = self.indexAt(event.pos())
        # if to_index.isValid():
        #     print("to:", to_index.data(), get_tree_selection_level(to_index))
        # print(position)

        where = to_index.data(Qt.UserRole)
        what = par_ix.data(Qt.UserRole)
        # print('moving',what['name'],'to',where['name'])
        
        if what['type'] == 'tag' and where['type'] == 'group':            
            move_tag_to_group(what['id'],where['id'])
            # what['group_id'] = where['id']
            # self.model().itemFromIndex(par_ix).setData(what,Qt.UserRole)
            # print(self.model().itemFromIndex(par_ix).data(Qt.UserRole))
        elif what['type'] == 'tag' and where['type'] == 'tag':
            move_tag_to_tag(what,where,int(position))
        elif what['type'] == 'group' and where['type'] == 'group':
            move_group_to_group(what,where,int(position))
            # what['group_id'] = where['group_id']
            # print('where group_id',where['group_id'])
            # self.model().itemFromIndex(par_ix).setData(what,Qt.UserRole)
            # print(self.model().itemFromIndex(par_ix).data(Qt.UserRole))
            # print("---")
            # move_tag_to_tag(what,where,int(position)) # 1 - above, 2 - below
            # new_list_order = where['list_order'] if int(position)==1 else where['list_order']+1
            # what['list_order'] = new_list_order
            # print(int(position))
            # print(new_list_order)
            # print(self.indexBelow(to_index).data(Qt.UserRole))
            # if not(int(position) == 2 and self.indexBelow(to_index).isValid() and self.indexBelow(to_index).data(Qt.UserRole)['type'] == 'tag' and \
            #     self.indexBelow(to_index).data(Qt.UserRole)['list_order']>new_list_order):
                # print('have to move')
        
        # if we have to increase the ids of all elements below
        # if not(int(position) == 2 and self.indexBelow(to_index).isValid() and self.indexBelow(to_index).data(Qt.UserRole)['type'] == 'tag' and \
        #     self.indexBelow(to_index).data(Qt.UserRole)['list_order']>new_list_order):
        #     print('have to move')

        # print(what, where)

        # for i in range(0,self.model().rowCount()):
        #     print(self.model().item(i).text()) 
        # print('------')

        super().dropEvent(event)
        self.setExpanded(to_index, True)
        
        # for i in range(0,self.model().rowCount()):
        #     print(self.model().item(i).text()) 

        # to_index = self.model().index(0,0)

        # while to_index.isValid(): # and self.indexBelow(to_index).data(Qt.UserRole)['type'] == 'tag':
        #     # print(to_index.data(Qt.UserRole)['type'],to_index.data(Qt.UserRole)['name'],to_index.data(Qt.UserRole)['id'])
        #     if to_index.data(Qt.UserRole)['type'] == 'tag':
        #         print(to_index.data(),to_index.data(Qt.UserRole)['group_id'])
        #     to_index = self.indexBelow(to_index)
        # print("---------------")

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