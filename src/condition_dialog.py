import sys
from PySide6.QtGui import QStandardItemModel, QIcon
from PySide6.QtWidgets import QApplication, QDialog, QAbstractItemView, QMessageBox
from PySide6.QtCore import QItemSelectionModel

from src.ui.ui_condition_dialog import Ui_Condition

from declutter.store import load_settings
from declutter.tags import get_all_tag_groups, get_tags_and_groups
from src.tags_dialog import generate_tag_model


class ConditionDialog(QDialog):
    def __init__(self, parent=None):
        super(ConditionDialog, self).__init__(parent)

        self.ui = Ui_Condition()
        self.ui.setupUi(self)
        self.condition = {}

        self.ui.tagsView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tag_model = QStandardItemModel()
        generate_tag_model(self.tag_model, get_tags_and_groups(), False)
        self.ui.tagsView.setModel(self.tag_model)
        self.ui.tagsView.expandAll()

        self.ui.tagsView.clicked.connect(self.tags_selection_changed)

        # Populate file types into combo
        self.ui.typeCombo.insertItems(0, list(load_settings()['file_types'].keys()))

        # Initial visibility
        self.update_visibility()
        self.ui.tagGroupsCombo.insertItems(0, get_all_tag_groups())

        self.ui.conditionCombo.currentIndexChanged.connect(self.update_visibility)
        self.ui.tagsCombo.currentIndexChanged.connect(self.update_tags_visibility)

    def tags_selection_changed(self):
        selected_tags = [
            self.ui.tagsView.model().itemFromIndex(index).text()
            for index in self.ui.tagsView.selectedIndexes()
        ]
        self.ui.selectedTagsLabel.setText('Selected tags: ' + ', '.join(selected_tags))

    def update_visibility(self):
        """
        Updates the visibility of UI elements based on the selected condition type.
        """
        state = self.ui.conditionCombo.currentText()

        self.ui.nameLabel.setVisible(state == "name")
        self.ui.nameCombo.setVisible(state == "name")
        self.ui.expressionLabel.setVisible(state == "name")
        self.ui.filemask.setVisible(state == "name")
        self.ui.filenameHint.setVisible(state == "name")

        self.ui.ageLabel.setVisible(state == "date")
        self.ui.ageCombo.setVisible(state == "date")
        self.ui.age.setVisible(state == "date")
        self.ui.ageUnitsCombo.setVisible(state == "date")

        self.ui.sizeLabel.setVisible(state == "size")
        self.ui.sizeCombo.setVisible(state == "size")
        self.ui.size.setVisible(state == "size")
        self.ui.sizeUnitsCombo.setVisible(state == "size")

        self.ui.tagLabel.setVisible(state == "tags")
        self.ui.tagsCombo.setVisible(state == "tags")
        # tagLabel2, tagsView, selectedTagsLabel are further refined in update_tags_visibility
        self.ui.tagLabel2.setVisible(state == "tags")
        self.ui.tagsView.setVisible(state == "tags")
        self.ui.selectedTagsLabel.setVisible(state == "tags")
        self.ui.tagGroupsCombo.setVisible(
            state == "tags" and self.ui.tagsCombo.currentText() == "tags in group"
        )

        self.ui.typeCombo.setVisible(state == "type")
        self.ui.typeLabel.setVisible(state == "type")
        self.ui.typeSwitchCombo.setVisible(state == "type")

        # Ensure tags sub-controls are in the right state
        self.update_tags_visibility()

    def update_tags_visibility(self):
        """
        Updates the visibility of tag-related UI elements based on the selected tag condition.
        Only relevant when condition type is 'tags'.
        """
        cond_type = self.ui.conditionCombo.currentText()
        state = self.ui.tagsCombo.currentText()

        # If not in 'tags' condition, hide tag-specific widgets
        if cond_type != 'tags':
            self.ui.tagLabel2.setVisible(False)
            self.ui.tagsView.setVisible(False)
            self.ui.tagsView.setEnabled(False)
            self.ui.selectedTagsLabel.setVisible(False)
            self.ui.tagGroupsCombo.setVisible(False)
            return

        # In 'tags' condition, refine visibility based on tag switch
        self.ui.tagLabel2.setVisible(state not in ('no tags', 'any tags', 'tags in group'))
        self.ui.tagsView.setVisible(state not in ('no tags', 'any tags', 'tags in group'))
        self.ui.tagsView.setEnabled(state not in ('no tags', 'any tags', 'tags in group'))
        self.ui.selectedTagsLabel.setVisible(state not in ('no tags', 'any tags', 'tags in group'))
        self.ui.tagGroupsCombo.setVisible(state == 'tags in group')

    def load_condition(self, cond: dict = None):
        """
        Loads a condition into the dialog, populating the UI elements with the condition's data.
        """
        if cond is None:
            cond = {}
        self.condition = dict(cond)  # copy to avoid mutating external reference

        # Block signals to avoid intermediate visibility flicker while we set widgets
        self.ui.conditionCombo.blockSignals(True)
        self.ui.tagsCombo.blockSignals(True)
        try:
            if not cond:
                # Nothing to preload
                pass
            else:
                # Select condition type first
                self.ui.conditionCombo.setCurrentIndex(self.ui.conditionCombo.findText(cond.get('type', '')))
                ctype = cond.get('type')

                if ctype == 'name':
                    self.ui.nameCombo.setCurrentIndex(self.ui.nameCombo.findText(cond.get('name_switch', '')))
                    self.ui.filemask.setText(cond.get('filemask', ''))

                elif ctype == 'date':
                    self.ui.ageCombo.setCurrentIndex(self.ui.ageCombo.findText(cond.get('age_switch', '')))
                    self.ui.age.setText(str(cond.get('age', '')))
                    self.ui.ageUnitsCombo.setCurrentIndex(self.ui.ageUnitsCombo.findText(cond.get('age_units', '')))

                elif ctype == 'size':
                    self.ui.sizeCombo.setCurrentIndex(self.ui.sizeCombo.findText(cond.get('size_switch', '')))
                    self.ui.size.setText(str(cond.get('size', '')))
                    self.ui.sizeUnitsCombo.setCurrentIndex(self.ui.sizeUnitsCombo.findText(cond.get('size_units', '')))

                elif ctype == 'tags':
                    self.ui.tagsCombo.setCurrentIndex(self.ui.tagsCombo.findText(cond.get('tag_switch', '')))
                    # Set tag group if applicable
                    if 'tag_group' in cond:
                        self.ui.tagGroupsCombo.setCurrentText(cond['tag_group'])
                    # Pre-select tags
                    tag_switch = cond.get('tag_switch')
                    if tag_switch not in ('no tags', 'any tags', 'tags in group'):
                        tags_to_select = set(cond.get('tags', []))
                        if tags_to_select:
                            sel_model = self.ui.tagsView.selectionModel()
                            sel_model.clearSelection()
                            model = self.ui.tagsView.model()
                            for i in range(model.rowCount()):
                                parent_item = model.item(i)
                                for k in range(parent_item.rowCount()):
                                    child = parent_item.child(k)
                                    if child.text() in tags_to_select:
                                        idx = model.indexFromItem(child)
                                        sel_model.select(idx, QItemSelectionModel.Select)
                            self.ui.selectedTagsLabel.setText('Selected tags: ' + ', '.join(tags_to_select))

                elif ctype == 'type':
                    self.ui.typeSwitchCombo.setCurrentIndex(self.ui.typeSwitchCombo.findText(cond.get('file_type_switch', '')))
                    self.ui.typeCombo.setCurrentIndex(self.ui.typeCombo.findText(cond.get('file_type', '')))
        finally:
            self.ui.conditionCombo.blockSignals(False)
            self.ui.tagsCombo.blockSignals(False)

        # 2) Force visibility refresh now that widgets are set
        self.update_visibility()
        self.update_tags_visibility()

    def accept(self):
        error = ""

        ctype = self.ui.conditionCombo.currentText()
        self.condition['type'] = ctype

        if ctype == 'name':
            self.condition['name_switch'] = self.ui.nameCombo.currentText()
            if self.ui.filemask.text() == "":
                error = "Filemask can't be empty"
            self.condition['filemask'] = self.ui.filemask.text()

        elif ctype == 'date':
            self.condition['age_switch'] = self.ui.ageCombo.currentText()
            try:
                self.condition['age'] = float(self.ui.age.text())
            except Exception:
                error = "Incorrect Age value"
            self.condition['age_units'] = self.ui.ageUnitsCombo.currentText()

        elif ctype == 'size':
            self.condition['size_switch'] = self.ui.sizeCombo.currentText()
            try:
                self.condition['size'] = float(self.ui.size.text())
            except Exception:
                error = "Incorrect Size value"
            self.condition['size_units'] = self.ui.sizeUnitsCombo.currentText()

        elif ctype == 'tags':
            self.condition['tag_switch'] = self.ui.tagsCombo.currentText()
            self.condition['tags'] = [index.data() for index in self.ui.tagsView.selectedIndexes()]
            if self.condition['tag_switch'] == 'tags in group':
                self.condition['tag_group'] = self.ui.tagGroupsCombo.currentText()
            if not self.condition['tags'] and self.condition['tag_switch'] not in ('no tags', 'any tags', 'tags in group'):
                error = "You haven't selected any tags"

        elif ctype == 'type':
            self.condition['file_type_switch'] = self.ui.typeSwitchCombo.currentText()
            self.condition['file_type'] = self.ui.typeCombo.currentText()

        if error:
            QMessageBox.critical(self, "Error", error, QMessageBox.Ok)
        else:
            super(ConditionDialog, self).accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConditionDialog()
    window.show()
    sys.exit(app.exec())
