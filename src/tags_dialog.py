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
from PySide6.QtCore import Qt, QSize
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

        self.ui.colorButton.clicked.connect(self.set_color)

        self.ui.treeView.doubleClicked.connect(self.rename)
        # self.model.itemChanged.connect(self.item_changed) # TBD this can be used for in-place editing
        self.ui.treeView.setModel(self.model)
        self.ui.treeView.expandAll()
        self.ui.treeView.setExpandsOnDoubleClick(False)
        self.ui.treeView.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def rename(self):
        cur_item = self.ui.treeView.currentIndex().data(Qt.UserRole)
        if cur_item["type"] == "tag":
            cur_tag = cur_item["name"]
            newtag, ok = QInputDialog.getText(
                self, "Rename tag", "Enter new name:", QLineEdit.Normal, cur_tag
            )
            if ok and newtag != "" and newtag != cur_tag:
                merge = False
                if newtag in get_all_tags():  # TBD use model data instead?
                    merge = QMessageBox.question(
                        self,
                        "Warning",
                        "This tag already exists, files tagged with '"
                        + cur_tag
                        + "' will be tagged with '"
                        + newtag
                        + "'.\nAre you sure you want to proceed?",
                        QMessageBox.Yes | QMessageBox.No,
                    )
                if newtag and merge in (QMessageBox.Yes, False):
                    rename_tag(cur_tag, newtag)
                    cur_item["name"] = newtag
                    self.model.itemFromIndex(self.ui.treeView.currentIndex()).setData(
                        cur_item, Qt.UserRole
                    )
                    self.model.itemFromIndex(self.ui.treeView.currentIndex()).setData(
                        newtag, Qt.DisplayRole
                    )
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
                {"name": group, "name_shown": group, "type": "group", "id": id},
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
        if self.ui.treeView.currentIndex().data(Qt.UserRole)["type"] == "tag":
            tag = self.ui.treeView.currentIndex().data()
            reply = QMessageBox.question(
                self,
                "Warning",
                "Are you sure you want to delete this tag:\n" + tag + "?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                delete_tag(tag)
                item = self.model.itemFromIndex(self.ui.treeView.currentIndex())
                self.model.removeRow(
                    item.row(), self.model.indexFromItem(item.parent())
                )
        else:
            group = self.ui.treeView.currentIndex().data(Qt.UserRole)
            if group["id"] == 1:
                QMessageBox.critical(
                    self, "Can't do that", "You can't delete the default group, sorry."
                )
            else:
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
