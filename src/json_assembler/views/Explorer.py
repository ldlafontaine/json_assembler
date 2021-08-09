from PySide2 import QtWidgets, QtCore, QtGui

from ..models.Attribute import Attribute
from ..models import maya_utilities


class Explorer(QtWidgets.QWidget):

    selection_activated = QtCore.Signal()

    def __init__(self, parent=None):
        super(Explorer, self).__init__(parent)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        # Set behaviour and styling.
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        # Create attributes.
        self.show_non_keyable_enabled = True
        self.show_connected_only_enabled = False
        self.show_hidden_enabled = False
        self.expanded_items = []
        self.callback_ids = []
        self.callback_ids.append(maya_utilities.register_selection_changed_callback(self.refresh))
        self.search_term = ""

        self.populate()

    def create_widgets(self):
        label_font = QtGui.QFont()
        label_font.setBold(True)
        label_font.setPointSize(8)
        label_font.setCapitalization(QtGui.QFont.AllUppercase)

        self.title_label = QtWidgets.QLabel("Explorer")
        self.title_label.setFont(label_font)

        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Search...")

        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setSelectionMode(self.tree_widget.ExtendedSelection)
        self.tree_widget.setHeaderHidden(True)

        self.context_menu = QtWidgets.QMenu(self)
        self.add_action = self.context_menu.addAction("Add")
        self.remove_action = self.context_menu.addAction("Remove")

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.search_bar)
        main_layout.addWidget(self.tree_widget)
        self.setLayout(main_layout)

    def create_connections(self):
        self.tree_widget.itemSelectionChanged.connect(self.on_item_selection_changed)
        self.search_bar.textEdited.connect(self.on_search_bar_text_edited)
        self.customContextMenuRequested.connect(self.on_context_menu_requested)
        self.add_action.triggered.connect(self.parent().on_add_button_clicked)
        self.remove_action.triggered.connect(self.parent().on_remove_button_clicked)

    def sizeHint(*args, **kwargs):
        return QtCore.QSize(225, 225)

    def populate(self):
        for node in maya_utilities.get_active_selection():
            item = QtWidgets.QTreeWidgetItem([node.title])
            item.setData(0, QtCore.Qt.UserRole, node)
            self.tree_widget.addTopLevelItem(item)

            attributes = node.get_all_attributes()
            for attribute in attributes:
                if not self.check_filters(attribute):
                    continue
                child_item = QtWidgets.QTreeWidgetItem([attribute.title])
                child_item.setData(0, QtCore.Qt.UserRole, attribute)
                item.addChild(child_item)

            # Expand item if expanded at the time of refresh.
            if node in self.expanded_items:
                item.setExpanded(True)

        self.search(self.search_term)

    def check_filters(self, data):
        if isinstance(data, Attribute):
            if self.show_connected_only_enabled and not data.is_connected():
                return False
            elif not self.show_non_keyable_enabled and not data.is_non_keyable():
                return False
            elif not self.show_hidden_enabled and data.is_hidden():
                return False
            else:
                return True
        else:
            return True

    def refresh(self):
        # Store which top level items are expanded in order to preserve the current layout.
        self.expanded_items = []
        for item_index in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(item_index)
            if item.isExpanded():
                item_data = item.data(0, QtCore.Qt.UserRole)
                self.expanded_items.append(item_data)

        # Clear and repopulate the widget.
        self.tree_widget.clear()
        self.populate()

    def search(self, term):
        self.search_term = term
        for item_index in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(item_index)
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

    def get_data_from_selected(self, parents=False):
        data = set()
        selected_items = self.tree_widget.selectedItems()
        for item in selected_items:
            entry = item.data(0, QtCore.Qt.UserRole)
            if isinstance(entry, Attribute):
                parent_item = item.parent()
                parent_entry = parent_item.data(0, QtCore.Qt.UserRole)
                entry.parent = parent_entry
                if parents is True and parent_entry not in data:
                    data.add(parent_entry)
            data.add(entry)

        return data

    def set_show_non_keyable_enabled(self, state):
        self.show_non_keyable_enabled = state
        self.refresh()

    def set_show_connected_only_enabled(self, state):
        self.show_connected_only_enabled = state
        self.refresh()

    def set_show_hidden_enabled(self, state):
        self.show_hidden_enabled = state
        self.refresh()

    def on_item_selection_changed(self):
        selected_items = self.tree_widget.selectedItems()
        if len(selected_items) > 0:
            self.selection_activated.emit()

    def on_search_bar_text_edited(self):
        text = self.search_bar.text()
        self.search(text)

    def on_context_menu_requested(self, point):
        selected_indexes = self.tree_widget.selectedIndexes()
        if selected_indexes:
            self.context_menu.popup(self.mapToGlobal(point))
