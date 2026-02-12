import sys
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QMessageBox,
    QInputDialog,
    QLineEdit,
    QColorDialog,
    QComboBox,
    QDialogButtonBox,
    QVBoxLayout,
    QAbstractItemView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QStandardItemModel, QStandardItem, QIcon
from src.ui.ui_tags_dialog import Ui_tagsDialog
from declutter.tags import (
    get_all_tags,
    get_tags_and_groups,
    rename_tag,
    set_group_type,
    rename_group,
    tag_get_color,
    tag_set_color,
    create_tag,
    create_group,
    delete_tag,
    delete_group,
    set_group_name_shown,
    get_files_by_tag,
)


class TagsDialog(QDialog):
    def __init__(self, model=QStandardItemModel()):
        super(TagsDialog, self).__init__()
        self.ui = Ui_tagsDialog()
        self.ui.setupUi(self)

        self.model = model

        self.ui.addButton.clicked.connect(self.add_tag)
        self.ui.removeButton.clicked.connect(self.remove)
        self.ui.addGroupButton.clicked.connect(self.add_group)

        self.ui.editButton.clicked.connect(self.edit_selected)

        self.ui.treeView.doubleClicked.connect(self.rename)
        # self.model.itemChanged.connect(self.item_changed) # TBD this can be used for in-place editing
        self.ui.treeView.setModel(self.model)
        sel_model = self.ui.treeView.selectionModel()
        if sel_model:
            sel_model.selectionChanged.connect(self._update_toolbar_buttons_state)
        # Initialize state on open
        self._update_toolbar_buttons_state()
        self.ui.treeView.expandAll()
        self.ui.treeView.setExpandsOnDoubleClick(False)
        self.ui.treeView.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def _update_toolbar_buttons_state(self, *args):
        """Enable/disable edit and delete buttons based on selection."""
        idx = self.ui.treeView.currentIndex()
        has_selection = idx.isValid() and bool(idx.data(Qt.UserRole))
        # Edit enabled only if something is selected (tag or group)
        self.ui.editButton.setEnabled(has_selection)
        # Delete enabled only if a tag is selected OR a non-default group is selected
        can_delete = False
        if has_selection:
            payload = idx.data(Qt.UserRole)
            if payload and "type" in payload:
                if payload["type"] == "tag":
                    can_delete = True
                elif payload["type"] == "group":
                    # block default group (id==1)
                    can_delete = payload.get("id") != 1
        self.ui.removeButton.setEnabled(can_delete)

    def rename(self):
        cur_item = self.ui.treeView.currentIndex().data(Qt.UserRole)
        if cur_item["type"] == "tag":
            cur_tag = cur_item["name"]
            newtag, ok = QInputDialog.getText(
                self, "Rename tag", "Enter new name:", QLineEdit.Normal, cur_tag
            )

            if ok and newtag != "" and newtag != cur_tag:
                # Check if target tag exists
                existing = set(get_all_tags())
                target_exists = newtag in existing

                # Count usage of current tag to decide whether to show merge message
                usage_count = 0
                if target_exists:
                    try:
                        usage = get_files_by_tag(cur_tag)
                        usage_count = len(usage) if usage else 0
                    except Exception:
                        usage_count = 0

                proceed = True
                if target_exists and usage_count > 0:
                    file_word = "file" if usage_count == 1 else "files"
                    merge = QMessageBox.question(
                        self,
                        "Warning",
                        f"This tag already exists. Files tagged with '{cur_tag}' ({usage_count} {file_word}) will be tagged with '{newtag}'.\nAre you sure you want to proceed?",
                        QMessageBox.Yes | QMessageBox.No,
                    )
                    proceed = merge == QMessageBox.Yes

                if not proceed:
                    return

                # Perform rename (with merge if target exists)
                rename_tag(cur_tag, newtag)

                # Update UI model payload for immediate feedback
                cur_item["name"] = newtag
                self.model.itemFromIndex(self.ui.treeView.currentIndex()).setData(
                    cur_item, Qt.UserRole
                )
                self.model.itemFromIndex(self.ui.treeView.currentIndex()).setData(
                    newtag, Qt.DisplayRole
                )

                # Fully rebuild the model to drop the old tag row immediately
                self.reload_model()
            return

        else:  # group
            group = cur_item["name"]
            other_groups = [
                self.model.item(i).data(Qt.UserRole)["name"]
                for i in range(self.model.rowCount())
            ]

            other_groups.remove(group)

            # Preselect current widget_type and name_shown
            current_widget_type = cur_item.get("widget_type", 0)
            current_name_shown = cur_item.get("name_shown", 1)
            is_default = cur_item.get("id") == 1

            group_dialog = GroupDialog(
                group, name_shown=current_name_shown, is_default=is_default
            )

            try:
                group_dialog.comboBox.setCurrentIndex(int(current_widget_type))
            except Exception:
                group_dialog.comboBox.setCurrentIndex(0)

            if group_dialog.exec():
                newgroup = group_dialog.lineEdit.text()
                widget_type = group_dialog.comboBox.currentIndex()
                name_shown = 1 if group_dialog.showNameCheck.isChecked() else 0

                # Persist group type to DB
                set_group_type(group, widget_type)
                try:
                    set_group_name_shown(group, name_shown)
                except Exception:
                    pass

                # Update current item’s metadata in the model
                cur_item["widget_type"] = widget_type
                cur_item["name_shown"] = name_shown
                self.model.itemFromIndex(self.ui.treeView.currentIndex()).setData(
                    cur_item, Qt.UserRole
                )

                # Rename group if changed and not duplicate
                if newgroup != "" and newgroup != group:
                    if newgroup in other_groups:
                        QMessageBox.information(
                            self,
                            "Can't do that",
                            "Another group with this name already exists. Please choose a different name.",
                        )
                    else:
                        rename_group(group, newgroup)
                        cur_item["name"] = newgroup
                        self.model.itemFromIndex(
                            self.ui.treeView.currentIndex()
                        ).setData(cur_item, Qt.UserRole)
                        self.model.itemFromIndex(
                            self.ui.treeView.currentIndex()
                        ).setData(newgroup, Qt.DisplayRole)

            # Prevent accidental inline edit after dialog
            self.ui.treeView.clearSelection()
            self.ui.treeView.setCurrentIndex(self.model.index(-1, -1))

    def edit_selected(self):
        """Edit selected tag or group:
        - tag: open color picker (existing behavior)
        - group: open GroupDialog
        """
        idx = self.ui.treeView.currentIndex()
        if not idx.isValid():
            return
        payload = idx.data(Qt.UserRole)
        if not payload or "type" not in payload:
            return

        if payload["type"] == "tag":
            self.set_color()
        elif payload["type"] == "group":
            # Reuse the same flow as double-click on group
            group = payload.get("name", "")
            current_widget_type = payload.get("widget_type", 0)
            current_name_shown = payload.get("name_shown", 1)
            is_default = payload.get("id") == 1

            group_dialog = GroupDialog(
                group, name_shown=current_name_shown, is_default=is_default
            )
            try:
                group_dialog.comboBox.setCurrentIndex(int(current_widget_type))
            except Exception:
                group_dialog.comboBox.setCurrentIndex(0)

            if group_dialog.exec():
                newgroup = group_dialog.lineEdit.text()
                widget_type = group_dialog.comboBox.currentIndex()
                name_shown = 1 if group_dialog.showNameCheck.isChecked() else 0

                # Persist to DB
                set_group_type(group, widget_type)
                try:
                    set_group_name_shown(group, name_shown)
                except Exception:
                    pass

                # Update model payload
                payload["widget_type"] = widget_type
                payload["name_shown"] = name_shown
                self.model.itemFromIndex(idx).setData(payload, Qt.UserRole)

                # Handle rename if changed and not duplicate
                if newgroup and newgroup != group:
                    other_groups = [
                        self.model.item(i).data(Qt.UserRole)["name"]
                        for i in range(self.model.rowCount())
                    ]
                    # remove current name to avoid self-duplicate detection
                    try:
                        other_groups.remove(group)
                    except ValueError:
                        pass
                    if newgroup in other_groups:
                        QMessageBox.information(
                            self,
                            "Can't do that",
                            "Another group with this name already exists. Please choose a different name.",
                        )
                    else:
                        rename_group(group, newgroup)
                        payload["name"] = newgroup
                        self.model.itemFromIndex(idx).setData(payload, Qt.UserRole)
                        self.model.itemFromIndex(idx).setData(newgroup, Qt.DisplayRole)

            # Prevent accidental inline edit after dialog
            self.ui.treeView.clearSelection()
            self.ui.treeView.setCurrentIndex(self.model.index(-1, -1))

    def set_color(self):
        if self.ui.treeView.currentIndex().data(Qt.UserRole)["type"] == "tag":

            tag = self.ui.treeView.currentIndex().data()

            cur_color = None
            if tag_get_color(tag):
                cur_color = QColor()
                cur_color.setRgba(tag_get_color(tag))

            color = QColorDialog.getColor(
                cur_color if cur_color is not None else Qt.gray,
                self,
                "Select color",
                QColorDialog.ShowAlphaChannel,
            )
            if color.isValid():
                self.ui.treeView.model().itemFromIndex(
                    self.ui.treeView.currentIndex()
                ).setData(color, Qt.BackgroundRole)

                tag_set_color(tag, color.rgba())
                tag_data = self.ui.treeView.currentIndex().data(Qt.UserRole)

                tag_data["color"] = color.rgba()
                self.model.itemFromIndex(self.ui.treeView.currentIndex()).setData(
                    tag_data, Qt.UserRole
                )

    def add_tag(self):
        group_id = 1
        if (
            self.ui.treeView.currentIndex().data()
            and self.ui.treeView.currentIndex().data(Qt.UserRole)["type"] == "group"
        ):
            group_id = self.ui.treeView.currentIndex().data(Qt.UserRole)["id"]

        tag, ok = QInputDialog.getText(
            self, "Add new tag", "Enter tag name:", QLineEdit.Normal
        )
        if not ok or tag == "":
            return

        # Prevent duplicates: check against existing tags first
        from declutter.tags import get_all_tags

        existing = set(get_all_tags())
        if tag in existing:
            QMessageBox.information(
                self, "Duplicate tag", f"A tag named '{tag}' already exists."
            )
            return

        # Create and handle any DB uniqueness errors defensively
        try:
            create_tag(tag, group_id)
        except Exception as e:
            # Most likely sqlite3.IntegrityError: UNIQUE constraint failed: tags.name
            QMessageBox.critical(self, "Error", f"Failed to create tag '{tag}': {e}")
            return

        self.reload_model()  # keep behavior: refresh view

    def add_group(self):
        group, ok = QInputDialog.getText(
            self, "Add new group", "Enter group name:", QLineEdit.Normal
        )
        if ok and group != "":
            id = create_group(group)
            gr_item = QStandardItem(group)
            gr_item.setData(
                {"name": group, "name_shown": 1, "type": "group", "id": id},
                Qt.UserRole,
            )

            # Set folder icon immediately (prefer theme; fallback to bundled)
            iconThemeName = "folder"
            if QIcon.hasThemeIcon(iconThemeName):
                gr_item.setIcon(QIcon.fromTheme(iconThemeName))
            else:
                gr_item.setIcon(QIcon(":/images/icons/folder.svg"))

            self.model.appendRow(gr_item)

    def remove(self):
        idx = self.ui.treeView.currentIndex()
        data = idx.data(Qt.UserRole)
        if not data or "type" not in data:
            return

        if data["type"] == "tag":
            tag = idx.data()  # display role holds tag name
            # New: compute usage count
            try:
                from declutter.tags import get_files_by_tag

                usage = get_files_by_tag(tag)
                count = len(usage) if usage else 0
            except Exception:
                count = 0

            msg = f'Are you sure you want to delete this tag: "{tag}"?'
            if count > 0:
                msg += f"\nThis tag is used by {count} file{'s' if count != 1 else ''}.\nDeleting it will remove the tag from {'those files' if count != 1 else 'that file'}."

            reply = QMessageBox.question(
                self,
                "Warning",
                msg,
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                delete_tag(tag)
                item = self.model.itemFromIndex(idx)
                self.model.removeRow(
                    item.row(), self.model.indexFromItem(item.parent())
                )
            return

        else:
            group = data
            if group["id"] == 1:
                QMessageBox.critical(
                    self, "Can't do that", "You can't delete the default group, sorry."
                )
                return

            msgBox = QMessageBox(
                QMessageBox.Question,
                "Question",
                "You're about to delete this group:\n"
                + group["name"]
                + "\nWould you like to keep its tags (will be moved to Default group) or delete them all?",
            )
            # to default group
            msgBox.addButton("Keep tags", QMessageBox.YesRole)
            msgBox.addButton("Delete tags", QMessageBox.NoRole)
            msgBox.addButton("Cancel", QMessageBox.RejectRole)
            reply = msgBox.exec()
            if reply != 2:
                delete_group(group["id"], not reply)
                self.reload_model()

    def reload_model(self):

        self.model.clear()
        generate_tag_model(self.model, get_tags_and_groups())
        self._update_toolbar_buttons_state()

        self.ui.treeView.expandAll()


# generates the model used in tagger dock widget, tags selection for filtering and tags manager


def generate_tag_model(model, data, groups_selectable=True):
    for group in data.keys():
        item = QStandardItem(group)
        item.setData(group, Qt.DisplayRole)
        item.setData(data[group], Qt.UserRole)
        try:
            if data[group].get("id") == 1:
                # avoid importing QFont globally; set a bold font object via FontRole
                from PySide6.QtGui import QFont

                bold_font = QFont()
                bold_font.setBold(True)
                item.setData(bold_font, Qt.FontRole)
        except Exception:
            pass
        item.setEditable(False)
        item.setSelectable(groups_selectable)
        item.setIcon(QIcon(":/images/icons/folder.svg"))
        model.appendRow(item)
        if "tags" in data[group].keys():
            for tag in data[group]["tags"]:
                tag_item = QStandardItem(tag["name"])
                tag_item.setData(tag["name"], Qt.DisplayRole)
                tag_item.setData(tag, Qt.UserRole)
                if tag["color"]:
                    color = QColor()
                    color.setRgba(tag["color"])
                    tag_item.setData(color, Qt.BackgroundRole)
                tag_item.setDropEnabled(False)
                tag_item.setEditable(False)
                item.appendRow(tag_item)


class GroupDialog(QDialog):
    def __init__(self, group, name_shown=True, is_default=False, parent=None):
        super(GroupDialog, self).__init__(parent)
        vbox = QVBoxLayout()

        self.comboBox = QComboBox()
        self.comboBox.addItems(["Multi-value (checkboxes)", "Single value (combobox)"])

        self.lineEdit = QLineEdit(group)

        # New: checkbox to control name_shown
        from PySide6.QtWidgets import QCheckBox, QLabel

        self.showNameCheck = QCheckBox("Show group name")
        self.showNameCheck.setChecked(bool(name_shown))

        # Optional info for Default group
        if is_default:
            note = QLabel("This is the default group")
            note.setStyleSheet("color: palette(mid);")  # subtle
            vbox.addWidget(note)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.accepted.connect(self.accept)

        vbox.addWidget(self.lineEdit)
        vbox.addWidget(self.comboBox)
        vbox.addWidget(self.showNameCheck)
        vbox.addWidget(self.buttonBox)

        self.setWindowTitle("Edit Group")
        self.setWindowIcon(QIcon(":/images/icons/DeClutter.ico"))
        self.setLayout(vbox)

    def accept(self):
        return super().accept()

    def reject(self):
        return super().reject()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = TagsDialog()
    window.show()
    sys.exit(app.exec())
