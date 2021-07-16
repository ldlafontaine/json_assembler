from PySide2 import QtWidgets, QtCore

from models import utils


class Outliner(QtWidgets.QTreeWidget):

    def __init__(self, parent=None):
        super(Outliner, self).__init__(parent)

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
            node_name = utils.get_node_name(node)
            item = QtWidgets.QTreeWidgetItem([node_name])
            item.setData(0, QtCore.Qt.UserRole, node)

            attributes = utils.get_attributes(node)
            for attribute in attributes:
                attribute_name = utils.get_attribute_name(attribute)
                child_item = QtWidgets.QTreeWidgetItem([attribute_name])
                child_item.setData(0, QtCore.Qt.UserRole, attribute)
                item.addChild(child_item)

            self.addTopLevelItem(item)

    def refresh(self):
        self.clear()
        self.populate()

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

    def propagate_selection_to_children(self, item):
        self.selection_is_being_propagated = True
        selection_state = item.isSelected()
        for child_index in range(item.childCount()):
            child_item = item.child(child_index)
            child_item.setSelected(selection_state)
            if child_item.childCount() > 0:
                self.propagate_selection_to_children(child_item)
        self.selection_is_being_propagated = False

    def on_item_selection_changed(self):
        if self.selection_is_being_propagated:
            return
        selected_items = self.selectedItems()
        # Propagate selection to children.
        for item in selected_items:
            self.propagate_selection_to_children(item)
