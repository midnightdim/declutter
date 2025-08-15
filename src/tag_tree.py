from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeView, QAbstractItemView, QDialog, QWidget, QHBoxLayout, QVBoxLayout
from declutter.tags import move_tag_to_group, move_tag_to_tag, move_group_to_group

def get_tree_selection_level(index):
    """Returns the level of the given QModelIndex in the tree."""
    level = 0
    while index.parent().isValid():
        index = index.parent()
        level += 1
    return level

class TagTree(QTreeView):
    """A custom QTreeView for managing tags and tag groups with drag-and-drop functionality."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        """Initializes the UI settings for the TagTree."""
        self.setHeaderHidden(True)
        self.setColumnHidden(1, True)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        # TBD: self.setEditTriggers(QAbstractItemView.NoEditTriggers) - check if this is needed

    def dragMoveEvent(self, event):
        """Handles drag move events to validate drag-and-drop operations."""
        tree = event.source()
        par_ix = tree.selectedIndexes()[0] if tree.selectedIndexes() else None
        if not par_ix or not par_ix.isValid():
            event.ignore()
            return

        to_index = self.indexAt(event.pos())
        super().dragMoveEvent(event)
        position = self.dropIndicatorPosition()

        # Prevent invalid drops: 
        # 1. Cannot drop a parent into its own child branch (level check)
        # 2. Cannot drop an item onto itself or its immediate parent (position check)
        # 3. Cannot drop a higher-level item onto a lower-level item unless it's 'OnItem' (reparenting)
        if (get_tree_selection_level(par_ix) < get_tree_selection_level(to_index)) or \
           (get_tree_selection_level(par_ix) == get_tree_selection_level(to_index) and position != QAbstractItemView.BelowItem and position != QAbstractItemView.AboveItem) or \
           (get_tree_selection_level(par_ix) > get_tree_selection_level(to_index) and position != QAbstractItemView.OnItem) or to_index == par_ix.parent():
            event.ignore()

    def dropEvent(self, event):
        """Handles drop events to perform tag and group movements."""
        to_index = self.indexAt(event.pos())
        position = self.dropIndicatorPosition()
        par_ix = self.selectedIndexes()[0] if self.selectedIndexes() else None

        if not par_ix or not par_ix.isValid():
            return

        where = to_index.data(Qt.UserRole)
        what = par_ix.data(Qt.UserRole)

        # Normalize drop indicator enum to the integer expected by move_* functions
        # Map: Above/On -> 1 (before), Below -> 2 (after), OnViewport -> 2 (safe default)
        if position in (QAbstractItemView.AboveItem, QAbstractItemView.OnItem):
            position_int = 1
        elif position == QAbstractItemView.BelowItem:
            position_int = 2
        else:
            position_int = 2

        # Logic for moving tags/groups based on source and target types
        if what['type'] == 'tag' and where['type'] == 'group':
            move_tag_to_group(what['id'], where['id'])
        elif what['type'] == 'tag' and where['type'] == 'tag':
            move_tag_to_tag(what, where, position_int)
        elif what['type'] == 'group' and where['type'] == 'group':
            move_group_to_group(what, where, position_int)

        super().dropEvent(event)
        self.setExpanded(to_index, True)


class TagsDialog(QDialog):
    """Dialog for managing tags, displaying them in a TagTree."""
    def __init__(self, tag_model, parent=None):
        super().__init__(parent)
        self.tag_model = tag_model  # Store the passed-in model
        self.initUI()

    def initUI(self):
        """Initializes the UI for the TagsDialog."""
        self.setWindowTitle("Manage Tags")  # Optional: Add a title for clarity

        layout = QVBoxLayout(self)  # Use vertical layout for dialog simplicity

        self.treeView = TagTree(self)
        self.treeView.setModel(self.tag_model)  # Set the passed-in model here
        self.treeView.expandAll()  # Expand after model is set

        layout.addWidget(self.treeView)

        self.setGeometry(400, 400, 500, 400)  # Or use self.resize(500, 400)
