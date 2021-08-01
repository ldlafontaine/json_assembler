from PySide2 import QtWidgets, QtCore, QtGui

from ..models.Entry import Entry
from ..models.Attribute import Attribute
from ..models.Node import Node
from ..models.File import File


class OutlinerTreeWidget(QtWidgets.QTreeView):

    def __init__(self, outliner, parent=None):
        super(OutlinerTreeWidget, self).__init__(parent)

        self.setModel(QtGui.QStandardItemModel())

        # Set styling.
        self.setHeaderHidden(True)
        self.setStyleSheet("QTreeWidget::item { margin: 1 }")

        # Set behaviour.
        self.setSelectionMode(self.ExtendedSelection)

        # Create connections.
        self.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.expanded.connect(self.on_expanded)
        self.collapsed.connect(self.on_collapsed)

        # Create properties.
        self.outliner = outliner
        self.file = File()
        self.expanded_entries = set()
        self.selected_entries = set()

        self.items_by_entry = {}

    def create_item(self, entry):
        item = QtGui.QStandardItem(entry.title)
        item.setData(entry)
        item_icon = entry.get_icon_path()
        item.setIcon(QtGui.QIcon(item_icon))
        item.setEditable(False)
        self.items_by_entry[entry] = item
        return item

    def insert_item(self, item):
        entry = self.item.data()
        if entry.parent in self.items_by_entry:
            parent_widget = self.items_by_entry[entry.parent]
            parent_widget.setChild(entry.position, item)
        else:
            self.model().insertRow(entry.position, item)

        index = self.model().indexFromItem(item)
        if entry in self.selected_entries:
            self.selectionModel().select(index, QtCore.QItemSelectionModel.Select)
        if entry in self.expanded_entries:
            index = self.model().indexFromItem(item)
            self.setExpanded(index, True)

    def append_item(self, item):
        entry = item.data()
        if entry.parent in self.items_by_entry:
            parent_widget = self.items_by_entry[entry.parent]
            entry.position = parent_widget.rowCount()
            parent_widget.setChild(entry.position, item)
        else:
            entry.position = self.model().rowCount(self.rootIndex())
            self.model().appendRow(item)

    def refresh(self):
        # Clear the tree view.
        self.model().clear()

        # Repopulate the tree view.
        items = []
        for entry in self.file.entries:
            items.append(self.create_item(entry))
        for item in items:
            self.insert_item(item)

        # Emit signal to update connected widgets.
        self.outliner.updated.emit()

    def add_entries(self, entries):
        # Validate data and create item widgets from entries.
        validated_items = {}
        for entry in entries:
            if entry not in self.file.entries:
                item = self.create_item(entry)
                validated_items[entry] = item

        # Append items to the tree view and push to the file.
        for entry, item in validated_items.items():
            self.append_item(item)
            self.file.add_entry(entry)

        self.outliner.updated.emit()

    def remove_entries(self, external_entries):
        # Get entries from selected items.
        internal_entries = set()
        selected_indexes = self.selectionModel().selectedIndexes()
        for index in selected_indexes:
            item = self.model().itemFromIndex(index)
            entry = item.data()
            internal_entries.add(entry)

        entries = internal_entries.union(external_entries)
        for entry in entries:
            if entry in self.items_by_entry:
                # Remove entry from tree.
                item = self.items_by_entry[entry]
                index = self.model().indexFromItem(item)
                self.model().removeRow(index.row(), index.parent())
                del self.items_by_entry[entry]

                # Remove entry from file.
                self.file.remove_entry(entry)

        self.outliner.updated.emit()

    def clear_entries(self):
        self.file.clear_entries()
        self.refresh()

    def update_entry_parent(self, item, parent):
        entry = item.data()
        entry.parent = parent.data()
        self.file.entries.remove(entry)
        self.file.entries.add(entry)

    def update_entry_position(self, item, position):
        entry = item.data()
        if isinstance(entry, Entry):
            entry.position = position
            self.file.entries.remove(entry)
            self.file.entries.add(entry)

    def update_entry_positions_by_parent(self, parent):
        for row in range(parent.rowCount()):
            child = parent.child(row)
            self.update_entry_position(child, row)

    def on_expanded(self, index):
        item = self.model().itemFromIndex(index)
        data = item.data()
        self.expanded_entries.add(data)

    def on_collapsed(self, index):
        item = self.model().itemFromIndex(index)
        data = item.data()
        self.expanded_entries.remove(data)

    def on_selection_changed(self, selected, deselected):
        if self.selectionModel().hasSelection():
            self.outliner.selection_activated.emit()

        for index in selected.indexes():
            item = self.model().itemFromIndex(index)
            data = item.data()
            self.selected_entries.add(data)
        for index in deselected.indexes():
            item = self.model().itemFromIndex(index)
            data = item.data()
            self.selected_entries.remove(data)

    def on_move_up_button_pressed(self):
        selected_indexes = self.selectionModel().selectedIndexes()
        for index in selected_indexes:
            if index.row() <= 0:
                continue
            item = self.model().itemFromIndex(index)
            parent = item.parent()
            if not parent:
                parent = self.model().invisibleRootItem()
            row = parent.takeRow(index.row())
            parent.insertRow(index.row() - 1, row)

            # Select reinserted item.
            destination_index = self.model().indexFromItem(item)
            self.selectionModel().select(destination_index, QtCore.QItemSelectionModel.Select)

            # Update model.
            self.update_entry_positions_by_parent(parent)
        self.outliner.updated.emit()

    def on_move_down_button_pressed(self):
        selected_indexes = self.selectionModel().selectedIndexes()
        for index in selected_indexes:
            item = self.model().itemFromIndex(index)
            parent = item.parent()
            if not parent:
                parent = self.model().invisibleRootItem()
            if index.row() >= parent.rowCount() - 1:
                continue
            row = parent.takeRow(index.row())
            parent.insertRow(index.row() + 1, row)

            # Select reinserted item.
            destination_index = self.model().indexFromItem(item)
            self.selectionModel().select(destination_index, QtCore.QItemSelectionModel.Select)

            # Update model.
            self.update_entry_positions_by_parent(parent)
        self.outliner.updated.emit()

    def on_move_left_button_pressed(self):
        selected_indexes = self.selectionModel().selectedIndexes()
        for index in selected_indexes:
            item = self.model().itemFromIndex(index)
            parent = item.parent()
            if not parent:
                return
            grandparent = parent.parent()
            if not grandparent:
                grandparent = self.model().invisibleRootItem()
            row = parent.takeRow(index.row())
            grandparent.insertRow(index.parent().row(), row)
            destination_index = self.model().indexFromItem(item)
            self.selectionModel().select(destination_index, QtCore.QItemSelectionModel.Select)

            # Update model.
            self.update_entry_parent(item, grandparent)
            self.update_entry_positions_by_parent(parent)
            self.update_entry_positions_by_parent(grandparent)
        self.outliner.updated.emit()

    def on_move_right_button_pressed(self):
        selected_indexes = self.selectionModel().selectedIndexes()
        for index in selected_indexes:
            item = self.model().itemFromIndex(index)
            parent = item.parent()
            if not parent:
                parent = self.model().invisibleRootItem()
            nearest_sibling = index.siblingAtRow(index.row() + 1)
            nearest_sibling_item = self.model().itemFromIndex(nearest_sibling)
            if not nearest_sibling_item:
                return
            row = parent.takeRow(index.row())
            nearest_sibling_item.insertRow(0, row)
            destination_index = self.model().indexFromItem(item)
            self.selectionModel().select(destination_index, QtCore.QItemSelectionModel.Select)
            self.setExpanded(index, True)

            # Update model.
            self.update_entry_parent(item, nearest_sibling_item)
            self.update_entry_positions_by_parent(parent)
            self.update_entry_positions_by_parent(nearest_sibling_item)
        self.outliner.updated.emit()
