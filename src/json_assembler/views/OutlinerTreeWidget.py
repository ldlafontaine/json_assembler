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

        # Create attributes.
        self.outliner = outliner
        self.file = File()
        self.items_by_entry = {}

    def create_item(self, entry):
        item = QtGui.QStandardItem(entry.title)
        item.setData(entry)
        item_icon = entry.get_icon_path()
        item.setIcon(QtGui.QIcon(item_icon))
        item.setEditable(False)
        self.items_by_entry[entry] = item
        return item

    def append_item(self, item):
        entry = item.data()
        if entry.parent in self.items_by_entry:
            parent_widget = self.items_by_entry[entry.parent]
            entry.position = parent_widget.rowCount()
            parent_widget.setChild(entry.position, item)
        else:
            entry.position = self.model().rowCount(self.rootIndex())
            self.model().appendRow(item)

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

        # Get entries from external sources such as selected items in other widgets.
        entries = internal_entries.union(external_entries)

        # Get the children of each entry.
        map(lambda x: entries.update(self.file.get_children(x)), internal_entries)
        map(lambda x: entries.update(self.file.get_children(x)), external_entries)

        # Remove entries and associated items.
        for entry in entries:
            # Remove entry.
            self.file.remove_entry(entry)

            # Remove associated item.
            item = self.items_by_entry[entry]
            parent = item.parent()
            if not parent:
                parent = self.model().invisibleRootItem()
            parent.takeRow(item.index().row())

            # Remove the entry from dictionary.
            self.items_by_entry.pop(entry, None)

        self.outliner.updated.emit()

    def clear_entries(self):
        self.file.clear_entries()
        self.model().clear()
        self.items_by_entry.clear()
        self.outliner.updated.emit()

    def update_entry_parent(self, item, parent):
        entry = item.data()
        entry.parent = parent.data()
        self.file.entries.remove(entry)
        self.file.entries.add(entry)

    def update_entry_position(self, item, position):
        entry = item.data()
        entry.position = position
        self.file.entries.remove(entry)
        self.file.entries.add(entry)

    def update_entry_positions_by_parent(self, parent):
        for row in range(parent.rowCount()):
            child = parent.child(row)
            self.update_entry_position(child, row)

    def group_items_by_parent(self, items):
        items_by_parent = {}
        for item in items:
            parent = item.index().parent()  # The parent index is used as QModelIndex is hashable, but QStandardItem is not.
            if parent not in items_by_parent:
                items_by_parent[parent] = [item]
            else:
                items_by_parent[parent].append(item)
        return items_by_parent

    def get_selected_items_by_parent(self):
        selected_indexes = self.selectionModel().selectedIndexes()
        selected_items = []
        for index in selected_indexes:
            selected_items.append(self.model().itemFromIndex(index))
        return self.group_items_by_parent(selected_items)

    def get_parent_item(self, item):
        parent = item.parent()
        if not parent:
            parent = self.model().invisibleRootItem()
        return parent
    
    def get_parent_item_from_index(self, index):
        if index.isValid() and index != QtCore.QModelIndex():
            return self.model().itemFromIndex(index)
        else:
            return self.model().invisibleRootItem()

    def get_nearest_sibling_to_items(self, items):
        indexes = [x.index() for x in items]
        for index in indexes:
            nearest_sibling = index.siblingAtRow(index.row() + 1)
            if nearest_sibling.isValid() and nearest_sibling not in indexes:
                return self.model().itemFromIndex(nearest_sibling)
        return None

    def are_entry_keys_unique(self, parent, indexes):
        raise NotImplementedError

    def can_items_move_up(self, items):
        for item in items:
            if item.index().row() <= 0:
                return False
        return True

    def can_items_move_down(self, items):
        parent = None
        for item in items:
            if not parent:
                parent = self.get_parent_item(item)
            if item.index().row() >= parent.rowCount() - 1:
                return False
        return True

    def can_items_move_left(self, items):
        for item in items:
            if not item.parent():
                return False
        return True

    def can_items_move_right(self, item, nearest_sibling):
        if nearest_sibling:
            return True

    def on_selection_changed(self, selected, deselected):
        if self.selectionModel().hasSelection():
            self.outliner.selection_activated.emit()

    def on_move_up_button_pressed(self):
        item_groups = self.get_selected_items_by_parent()
        for parent_index, item_group in item_groups.items():

            # Perform validation.
            if not self.can_items_move_up(item_group):
                continue

            # Move items.
            parent = self.get_parent_item_from_index(parent_index)
            sorted_items = sorted(item_group, key=lambda i: i.index().row())
            for item in sorted_items:
                index = item.index()
                row = parent.takeRow(index.row())
                parent.insertRow(index.row() - 1, row)

                # Select reinserted item.
                self.selectionModel().select(item.index(), QtCore.QItemSelectionModel.Select)

            # Update item group entries.
            self.update_entry_positions_by_parent(parent)

        self.outliner.updated.emit()

    def on_move_down_button_pressed(self):
        item_groups = self.get_selected_items_by_parent()
        for parent_index, item_group in item_groups.items():

            # Perform validation.
            if not self.can_items_move_down(item_group):
                continue

            # Move items.
            parent = self.get_parent_item_from_index(parent_index)
            sorted_items = sorted(item_group, key=lambda i: i.index().row(), reverse=True)
            for item in sorted_items:
                index = item.index()
                row = parent.takeRow(index.row())
                parent.insertRow(index.row() + 1, row)

                # Select reinserted item.
                self.selectionModel().select(item.index(), QtCore.QItemSelectionModel.Select)

            # Update item group entries.
            self.update_entry_positions_by_parent(parent)

        self.outliner.updated.emit()

    def on_move_left_button_pressed(self):
        item_groups = self.get_selected_items_by_parent()
        for parent_index, item_group in item_groups.items():

            # Perform validation.
            if not self.can_items_move_left(item_group):
                continue

            # Move items.
            parent = self.get_parent_item_from_index(parent_index)
            grandparent = self.get_parent_item(parent)
            sorted_items = sorted(item_group, key=lambda i: i.index().row())
            for item in sorted_items:
                index = item.index()
                row = parent.takeRow(index.row())
                grandparent.insertRow(index.parent().row(), row)

                # Select reinserted item.
                self.selectionModel().select(item.index(), QtCore.QItemSelectionModel.Select)

                # Update item entry.
                self.update_entry_parent(item, grandparent)

            # Update item group entries.
            self.update_entry_positions_by_parent(parent)
            self.update_entry_positions_by_parent(grandparent)

        self.outliner.updated.emit()

    def on_move_right_button_pressed(self):
        item_groups = self.get_selected_items_by_parent()
        for parent_index, item_group in item_groups.items():

            # Perform validation.
            sorted_items = sorted(item_group, key=lambda i: i.index().row())
            nearest_sibling = self.get_nearest_sibling_to_items(sorted_items)
            if not self.can_items_move_right(sorted_items, nearest_sibling):
                continue

            # Move items.
            parent = self.get_parent_item_from_index(parent_index)
            for item in sorted_items:
                index = item.index()
                row = parent.takeRow(index.row())
                nearest_sibling.insertRow(0, row)

                # Select and expand reinserted item.
                self.selectionModel().select(item.index(), QtCore.QItemSelectionModel.Select)
                self.setExpanded(index, True)

                # Update item entry.
                self.update_entry_parent(item, nearest_sibling)

            # Update item group entries.
            self.update_entry_positions_by_parent(parent)
            self.update_entry_positions_by_parent(nearest_sibling)

        self.outliner.updated.emit()
