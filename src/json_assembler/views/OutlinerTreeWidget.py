from PySide2 import QtWidgets, QtCore, QtGui

from ..models.File import File
from PropertiesDialog import PropertiesDialog


class OutlinerTreeWidget(QtWidgets.QTreeView):

    def __init__(self, outliner, parent=None):
        super(OutlinerTreeWidget, self).__init__(parent)

        self.setModel(QtGui.QStandardItemModel())
        self.outliner = outliner

        self.create_widgets()
        self.create_connections()

        # Set behaviour and styling.
        self.setHeaderHidden(True)
        self.setStyleSheet("QTreeWidget::item { margin: 1 }")
        self.setSelectionMode(self.ExtendedSelection)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        # Create attributes.
        self.file = File()
        self.items_by_entry = {}

    def create_widgets(self):
        self.context_menu = QtWidgets.QMenu(self)
        self.edit_action = self.context_menu.addAction("Edit")
        self.remove_action = self.context_menu.addAction("Remove")
        self.context_menu.addSeparator()
        self.move_up_action = self.context_menu.addAction("Move Up")
        self.move_down_action = self.context_menu.addAction("Move Down")
        self.move_left_action = self.context_menu.addAction("Move Left")
        self.move_right_action = self.context_menu.addAction("Move Right")

    def create_connections(self):
        self.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.customContextMenuRequested.connect(self.on_context_menu_requested)

        self.edit_action.triggered.connect(self.edit_entry)
        self.remove_action.triggered.connect(lambda: self.remove_entries(set()))
        self.move_up_action.triggered.connect(self.move_up)
        self.move_down_action.triggered.connect(self.move_down)
        self.move_left_action.triggered.connect(self.move_left)
        self.move_right_action.triggered.connect(self.move_right)

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

    def get_item_groups(self, items):
        items_by_parent = {}
        for item in items:
            parent = item.index().parent()  # The parent index is used as QModelIndex is hashable, but QStandardItem is not.
            if parent not in items_by_parent:
                items_by_parent[parent] = []
            items_by_parent[parent].append(item)

        item_groups = []
        for parent_index, items in items_by_parent.items():
            parent = self.model().itemFromIndex(parent_index)
            if not parent:
                parent = self.model().invisibleRootItem()
            item_groups.append([parent, items])

        return item_groups

    def get_selected_item_groups(self):
        selected_indexes = self.selectionModel().selectedIndexes()
        selected_items = []
        for index in selected_indexes:
            selected_items.append(self.model().itemFromIndex(index))
        return self.get_item_groups(selected_items)

    def get_parent_item(self, item):
        parent = item.parent()
        if not parent:
            parent = self.model().invisibleRootItem()
        return parent

    def get_nearest_sibling_to_items(self, items):
        indexes = [x.index() for x in items]
        for index in indexes:
            nearest_sibling = index.siblingAtRow(index.row() + 1)
            if nearest_sibling.isValid() and nearest_sibling not in indexes:
                return self.model().itemFromIndex(nearest_sibling)
        return None

    def can_items_move_up(self, items):
        for item in items:
            if item.index().row() <= 0:
                return False
        return True

    def can_items_move_down(self, items, parent):
        for item in items:
            if item.index().row() >= parent.rowCount() - 1:
                return False
        return True

    def can_items_move_left(self, parent):
        if parent is self.model().invisibleRootItem():
            return False
        return True

    def can_items_move_right(self, nearest_sibling):
        if nearest_sibling:
            return True

    def new_entry(self):
        dialog = PropertiesDialog()
        result = dialog.exec_()
        if result == QtWidgets.QDialog.Accepted:
            entries = [dialog.entry]
            self.add_entries(entries)

    def edit_entry(self):
        if not self.selectionModel().hasSelection():
            return
        index = self.selectionModel().currentIndex()
        item = self.model().itemFromIndex(index)
        entry = item.data()
        dialog = PropertiesDialog(entry)
        result = dialog.exec_()
        if result == QtWidgets.QDialog.Accepted:
            item.setData(dialog.entry)
            item.setText(dialog.entry.title)
            self.outliner.updated.emit()

    def move_up(self):
        item_groups = self.get_selected_item_groups()
        for parent, item_group in item_groups:

            # Perform validation.
            if not self.can_items_move_up(item_group):
                continue

            # Move items.
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

    def move_down(self):
        item_groups = self.get_selected_item_groups()
        for parent, item_group in item_groups:

            # Perform validation.
            if not self.can_items_move_down(item_group, parent):
                continue

            # Move items.
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

    def move_left(self):
        item_groups = self.get_selected_item_groups()
        for parent, item_group in item_groups:

            # Perform validation.
            if not self.can_items_move_left(parent):
                continue

            # Move items.
            grandparent = self.get_parent_item(parent)
            sorted_items = sorted(item_group, key=lambda i: i.index().row())
            for item in sorted_items:
                index = item.index()
                row = parent.takeRow(index.row())
                grandparent.insertRow(parent.index().row(), row)

                # Select reinserted item.
                self.selectionModel().select(item.index(), QtCore.QItemSelectionModel.Select)

                # Update item entry.
                self.update_entry_parent(item, grandparent)

            # Update item group entries.
            self.update_entry_positions_by_parent(parent)
            self.update_entry_positions_by_parent(grandparent)

        self.outliner.updated.emit()

    def move_right(self):
        item_groups = self.get_selected_item_groups()
        for parent, item_group in item_groups:

            # Perform validation.
            sorted_items = sorted(item_group, key=lambda i: i.index().row(), reverse=True)
            nearest_sibling = self.get_nearest_sibling_to_items(sorted_items)
            if not self.can_items_move_right(nearest_sibling):
                continue

            # Move items.
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

    def on_selection_changed(self, selected, deselected):
        has_selection = self.selectionModel().hasSelection()
        self.outliner.set_buttons_enabled(has_selection)
        if has_selection:
            self.outliner.selection_activated.emit()

    def on_context_menu_requested(self, point):
        selected_indexes = self.selectionModel().selectedIndexes()
        if selected_indexes:
            self.context_menu.popup(self.mapToGlobal(point))
