from PySide2 import QtWidgets, QtCore

from models.Attribute import Attribute
from models.Node import Node
from models import utils


class Explorer(QtWidgets.QTreeWidget):

    selection_activated = QtCore.Signal()

    def __init__(self, parent=None):
        super(Explorer, self).__init__(parent)

        # Set styling.
        self.setHeaderHidden(True)

        # Set behaviour.
        self.setSelectionMode(self.ExtendedSelection)

        # Create connections.
        self.itemSelectionChanged.connect(self.on_item_selection_changed)

        # Create properties.
        self.selection_is_being_propagated = False
        self.callback_ids = []
        self.callback_ids.append(utils.register_selection_changed_callback(self.refresh))

        self.populate()

    def populate(self):
        for node in utils.get_active_selection():
            item = QtWidgets.QTreeWidgetItem([node.name])
            item.setData(0, QtCore.Qt.UserRole, node)

            attributes = node.get_all_attributes()
            for attribute in attributes:
                child_item = QtWidgets.QTreeWidgetItem([attribute.name])
                child_item.setData(0, QtCore.Qt.UserRole, attribute)
                item.addChild(child_item)

            self.addTopLevelItem(item)

    def refresh(self):
        self.clear()
        self.populate()

    def clear_selection(self):
        self.blockSignals(True)
        selected_items = self.selectedItems()
        for item in selected_items:
            item.setSelected(False)
        self.blockSignals(False)

    def search(self, term):
        for item_index in range(self.topLevelItemCount()):
            item = self.topLevelItem(item_index)
            item_text = item.text(0)
            hidden_count = 0
            for child_index in range(item.childCount()):
                child_item = item.child(child_index)
                child_text = child_item.text(0)
                if term.lower() not in (item_text + "." + child_text).lower():
                    child_item.setHidden(True)
                    hidden_count += 1
                else:
                    child_item.setHidden(False)
            if hidden_count == item.childCount():
                item.setHidden(True)
            else:
                item.setHidden(False)

    def get_data_from_selected(self):
        data = {}
        selected_items = self.selectedItems()
        for item in selected_items:
            item_data = item.data(0, QtCore.Qt.UserRole)
            if isinstance(item_data, Node) and item_data not in data:
                data[item_data] = {}
            elif isinstance(item_data, Attribute):
                try:
                    item_data_value = item_data.get_value()
                except NotImplementedError:
                    continue
                except:
                    continue
                parent_data = item.parent().data(0, QtCore.Qt.UserRole)
                if isinstance(parent_data, Node) and parent_data not in data:
                    data[parent_data] = {}
                data[parent_data][item_data] = item_data_value
        return data

    def get_flattened_data_from_selected(self):
        data = set()
        selected_items = self.selectedItems()
        for item in selected_items:
            item_data = item.data(0, QtCore.Qt.UserRole)
            data.add(item_data)
        return data

    def propagate_selection_to_children(self, item):
        selection_state = item.isSelected()
        child_count = item.childCount()
        child_index = 0
        while child_index < child_count:
            child_item = item.child(child_index)
            child_item.setSelected(selection_state)
            self.propagate_selection_to_children(child_item)
            child_index += 1

    def on_item_selection_changed(self):
        self.blockSignals(True)
        selected_items = self.selectedItems()
        # Propagate selection to children.
        for item in selected_items:
            self.propagate_selection_to_children(item)
        self.blockSignals(False)
        if len(selected_items) > 0:
            self.selection_activated.emit()
