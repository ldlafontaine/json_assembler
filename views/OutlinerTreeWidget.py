from PySide2 import QtWidgets, QtCore, QtGui

from models.Attribute import Attribute
from models.Node import Node
from models import utils


class OutlinerTreeWidget(QtWidgets.QTreeWidget):

    def __init__(self, outliner, parent=None):
        super(OutlinerTreeWidget, self).__init__(parent)

        # Set styling.
        self.setHeaderHidden(True)
        self.setStyleSheet("QTreeWidget::item { margin: 1 }")

        # Set behaviour.
        self.setSelectionMode(self.ExtendedSelection)

        # Create connections.
        self.itemSelectionChanged.connect(self.on_item_selection_changed)

        # Create properties.
        self.outliner = outliner
        self.expanded_items = []

    def populate(self, data):
        for data_element in sorted(data.keys()):
            # Create top level items.
            if not isinstance(data_element, Node):
                continue
            item = QtWidgets.QTreeWidgetItem([data_element.name])
            item.setData(0, QtCore.Qt.UserRole, data_element)
            item_icon = data_element.get_icon_path()
            item.setIcon(0, QtGui.QIcon(item_icon))
            self.addTopLevelItem(item)

            # Create child items.
            for child_data in sorted(data[data_element]):
                if not isinstance(child_data, Attribute):
                    continue
                child_item = QtWidgets.QTreeWidgetItem([child_data.name])
                child_item.setData(0, QtCore.Qt.UserRole, child_data)
                item.addChild(child_item)

            # Expand item if expanded at the time of refresh
            if data_element in self.expanded_items:
                item.setExpanded(True)

    def refresh(self, data):
        # Store which top level items are expanded in order to preserve the current layout.
        self.expanded_items = []
        for item_index in range(self.topLevelItemCount()):
            item = self.topLevelItem(item_index)
            if item.isExpanded():
                item_data = item.data(0, QtCore.Qt.UserRole)
                self.expanded_items.append(item_data)

        # Clear and repopulate the widget.
        self.clear()
        self.populate(data)

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
            self.outliner.selection_activated.emit()
