import sys
from PySide6.QtGui import QStandardItemModel, QIcon
from PySide6.QtWidgets import QApplication, QDialog, QAbstractItemView, QMessageBox, QDialogButtonBox
from PySide6.QtCore import QItemSelectionModel

from src.ui.ui_condition_dialog import Ui_Condition

from declutter.store import load_settings
from declutter.tags import get_all_tag_groups, get_tags_and_groups
from declutter.i18n import (
    CONDITION_TYPES,
    DATE_UNITS,
    NAME_SWITCHES,
    TAG_SWITCHES,
    TYPE_SWITCHES,
    combo_value,
    localized_file_type,
    set_combo_value,
    setup_combo,
    tr,
)
from src.tags_dialog import generate_tag_model


class ConditionDialog(QDialog):
    def __init__(self, parent=None):
        super(ConditionDialog, self).__init__(parent)

        self.ui = Ui_Condition()
        self.ui.setupUi(self)
        self.condition = {}
        self.apply_localization()

        self.ui.tagsView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tag_model = QStandardItemModel()
        generate_tag_model(self.tag_model, get_tags_and_groups(), False)
        self.ui.tagsView.setModel(self.tag_model)
        self.ui.tagsView.expandAll()

        self.ui.tagsView.clicked.connect(self.tags_selection_changed)

        # Populate file types into combo
        self._populate_file_types()

        # Initial visibility
        self.update_visibility()
        self.ui.tagGroupsCombo.insertItems(0, get_all_tag_groups())

        self.ui.conditionCombo.currentIndexChanged.connect(self.update_visibility)
        self.ui.tagsCombo.currentIndexChanged.connect(self.update_tags_visibility)

    def apply_localization(self):
        self.setWindowTitle(tr("condition.dialog_title"))
        self.ui.label.setText(tr("condition.select_by"))
        self.ui.nameLabel.setText(tr("condition.file_name"))
        self.ui.expressionLabel.setText(tr("condition.expression"))
        self.ui.filenameHint.setText(tr("condition.hint_masks"))
        self.ui.ageLabel.setText(tr("condition.file_age"))
        self.ui.sizeLabel.setText(tr("condition.file_size"))
        self.ui.tagLabel.setText(tr("condition.file_has"))
        self.ui.tagLabel2.setText(tr("condition.of_selected_tags"))
        self.ui.typeLabel.setText(tr("condition.file_type"))
        self._set_selected_tags_label([])

        setup_combo(self.ui.conditionCombo, CONDITION_TYPES, "condition_type")
        setup_combo(self.ui.nameCombo, NAME_SWITCHES, "name_switch")
        setup_combo(self.ui.ageUnitsCombo, DATE_UNITS, "date_unit")
        setup_combo(self.ui.tagsCombo, TAG_SWITCHES, "tag_switch")
        setup_combo(self.ui.typeSwitchCombo, TYPE_SWITCHES, "type_switch")

        ok_button = self.ui.buttonBox.button(QDialogButtonBox.Ok)
        cancel_button = self.ui.buttonBox.button(QDialogButtonBox.Cancel)
        if ok_button:
            ok_button.setText(tr("button.ok"))
        if cancel_button:
            cancel_button.setText(tr("button.cancel"))

    def _populate_file_types(self):
        current = combo_value(self.ui.typeCombo)
        self.ui.typeCombo.blockSignals(True)
        self.ui.typeCombo.clear()
        for file_type in load_settings()['file_types'].keys():
            self.ui.typeCombo.addItem(localized_file_type(file_type), file_type)
        set_combo_value(self.ui.typeCombo, current)
        self.ui.typeCombo.blockSignals(False)

    def _set_selected_tags_label(self, tags):
        if tags:
            self.ui.selectedTagsLabel.setText(
                tr("condition.selected_tags", tags=", ".join(tags))
            )
        else:
            self.ui.selectedTagsLabel.setText(tr("condition.selected_tags_empty"))

    def tags_selection_changed(self):
        selected_tags = [
            self.ui.tagsView.model().itemFromIndex(index).text()
            for index in self.ui.tagsView.selectedIndexes()
        ]
        self._set_selected_tags_label(selected_tags)

    def update_visibility(self):
        """
        Updates the visibility of UI elements based on the selected condition type.
        """
        state = combo_value(self.ui.conditionCombo)

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
            state == "tags" and combo_value(self.ui.tagsCombo) == "tags in group"
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
        cond_type = combo_value(self.ui.conditionCombo)
        state = combo_value(self.ui.tagsCombo)

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
                set_combo_value(self.ui.conditionCombo, cond.get('type', ''))
                ctype = cond.get('type')

                if ctype == 'name':
                    set_combo_value(self.ui.nameCombo, cond.get('name_switch', ''))
                    self.ui.filemask.setText(cond.get('filemask', ''))

                elif ctype == 'date':
                    set_combo_value(self.ui.ageCombo, cond.get('age_switch', ''))
                    self.ui.age.setText(str(cond.get('age', '')))
                    set_combo_value(self.ui.ageUnitsCombo, cond.get('age_units', ''))

                elif ctype == 'size':
                    set_combo_value(self.ui.sizeCombo, cond.get('size_switch', ''))
                    self.ui.size.setText(str(cond.get('size', '')))
                    set_combo_value(self.ui.sizeUnitsCombo, cond.get('size_units', ''))

                elif ctype == 'tags':
                    set_combo_value(self.ui.tagsCombo, cond.get('tag_switch', ''))
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
                            self._set_selected_tags_label(tags_to_select)

                elif ctype == 'type':
                    set_combo_value(self.ui.typeSwitchCombo, cond.get('file_type_switch', ''))
                    set_combo_value(self.ui.typeCombo, cond.get('file_type', ''))
        finally:
            self.ui.conditionCombo.blockSignals(False)
            self.ui.tagsCombo.blockSignals(False)

        # 2) Force visibility refresh now that widgets are set
        self.update_visibility()
        self.update_tags_visibility()

    def accept(self):
        error = ""

        ctype = combo_value(self.ui.conditionCombo)
        self.condition['type'] = ctype

        if ctype == 'name':
            self.condition['name_switch'] = combo_value(self.ui.nameCombo)
            if self.ui.filemask.text() == "":
                error = tr("error.filemask_empty")
            self.condition['filemask'] = self.ui.filemask.text()

        elif ctype == 'date':
            self.condition['age_switch'] = combo_value(self.ui.ageCombo)
            try:
                self.condition['age'] = float(self.ui.age.text())
            except Exception:
                error = tr("error.incorrect_age")
            self.condition['age_units'] = combo_value(self.ui.ageUnitsCombo)

        elif ctype == 'size':
            self.condition['size_switch'] = combo_value(self.ui.sizeCombo)
            try:
                self.condition['size'] = float(self.ui.size.text())
            except Exception:
                error = tr("error.incorrect_size")
            self.condition['size_units'] = combo_value(self.ui.sizeUnitsCombo)

        elif ctype == 'tags':
            self.condition['tag_switch'] = combo_value(self.ui.tagsCombo)
            self.condition['tags'] = [index.data() for index in self.ui.tagsView.selectedIndexes()]
            if self.condition['tag_switch'] == 'tags in group':
                self.condition['tag_group'] = self.ui.tagGroupsCombo.currentText()
            if not self.condition['tags'] and self.condition['tag_switch'] not in ('no tags', 'any tags', 'tags in group'):
                error = tr("error.no_tags_selected")

        elif ctype == 'type':
            self.condition['file_type_switch'] = combo_value(self.ui.typeSwitchCombo)
            self.condition['file_type'] = combo_value(self.ui.typeCombo)

        if error:
            QMessageBox.critical(self, tr("dialog.error"), error, QMessageBox.Ok)
        else:
            super(ConditionDialog, self).accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConditionDialog()
    window.show()
    sys.exit(app.exec())
