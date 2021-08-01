from PySide2 import QtWidgets, QtCore, QtGui

from OutlinerTreeWidget import OutlinerTreeWidget
from PropertiesDialog import PropertiesDialog


class Outliner(QtWidgets.QWidget):

    updated = QtCore.Signal()
    selection_activated = QtCore.Signal()

    def __init__(self, parent=None):
        super(Outliner, self).__init__(parent)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

        # Set behaviour and styling.
        self.setMinimumWidth(200)

    def create_widgets(self):
        self.stacked_widget = QtWidgets.QStackedWidget()
        self.insert_tab(0)

        self.left_tool_bar = QtWidgets.QToolBar()
        self.left_tool_bar.setContentsMargins(0, 0, 0, 0)
        self.new_button = self.create_tool_bar_button(":fileNew.png")
        # self.group_button = self.create_tool_bar_button(":folder-new.png")
        self.edit_button = self.create_tool_bar_button(":greasePencilPencil.png")

        self.right_tool_bar = QtWidgets.QToolBar()
        self.right_tool_bar.setContentsMargins(0, 0, 0, 0)
        self.move_up_button = self.create_tool_bar_button(":moveUVUp.png")
        self.move_down_button = self.create_tool_bar_button(":moveUVDown.png")
        self.move_left_button = self.create_tool_bar_button(":moveUVLeft.png")
        self.move_right_button = self.create_tool_bar_button(":moveUVRight.png")

    def create_layout(self):
        self.left_tool_bar.addWidget(self.new_button)
        # self.left_tool_bar.addWidget(self.group_button)
        self.left_tool_bar.addWidget(self.edit_button)

        self.right_tool_bar.addWidget(self.move_up_button)
        self.right_tool_bar.addWidget(self.move_down_button)
        self.right_tool_bar.addWidget(self.move_left_button)
        self.right_tool_bar.addWidget(self.move_right_button)

        tool_bar_layout = QtWidgets.QHBoxLayout()
        tool_bar_layout.addWidget(self.left_tool_bar)
        tool_bar_layout.addStretch()
        tool_bar_layout.addWidget(self.right_tool_bar)
        tool_bar_layout.setSpacing(0)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.stacked_widget)
        main_layout.addLayout(tool_bar_layout)

    def create_connections(self):
        self.new_button.clicked.connect(self.on_new_button_pressed)
        self.edit_button.clicked.connect(self.on_edit_button_pressed)
        self.move_up_button.clicked.connect(self.on_move_up_button_pressed)
        self.move_down_button.clicked.connect(self.on_move_down_button_pressed)
        self.move_left_button.clicked.connect(self.on_move_left_button_pressed)
        self.move_right_button.clicked.connect(self.on_move_right_button_pressed)

    def create_tool_bar_button(self, image_path):
        button = QtWidgets.QToolButton()
        button.setIcon(QtGui.QIcon(image_path))
        button.setStyleSheet("QToolButton{background:transparent; padding:0px; margin:0px }")
        return button

    def sizeHint(self):
        return QtCore.QSize(200, 350)

    def insert_tab(self, index):
        self.stacked_widget.insertWidget(index, OutlinerTreeWidget(self))
        self.stacked_widget.setCurrentIndex(index)

    def close_tab(self, index):
        stacked_widget = self.stacked_widget.widget(index)
        self.stacked_widget.removeWidget(stacked_widget)

    def refresh(self):
        current_stacked_widget = self.stacked_widget.currentWidget()
        current_stacked_widget.refresh()

    def add_entries(self, entries):
        current_stacked_widget = self.stacked_widget.currentWidget()
        current_stacked_widget.add_entries(entries)

    def remove_entries(self, entries):
        current_stacked_widget = self.stacked_widget.currentWidget()
        current_stacked_widget.remove_entries(entries)

    def clear_entries(self):
        current_stacked_widget = self.stacked_widget.currentWidget()
        current_stacked_widget.clear_entries()

    def clear_selection(self):
        current_stacked_widget = self.stacked_widget.currentWidget()
        current_stacked_widget.clearSelection()

    def on_new_button_pressed(self):
        dialog = PropertiesDialog()
        result = dialog.exec_()
        current_stacked_widget = self.stacked_widget.currentWidget()
        if result == QtWidgets.QDialog.Accepted:
            entries = [dialog.entry]
            current_stacked_widget.add_entries(entries)

    def on_edit_button_pressed(self):
        current_stacked_widget = self.stacked_widget.currentWidget()
        index = current_stacked_widget.selectionModel().currentIndex()
        item = current_stacked_widget.model().itemFromIndex(index)
        entry = item.data()
        dialog = PropertiesDialog(entry)
        result = dialog.exec_()
        if result == QtWidgets.QDialog.Accepted:
            item.setData(dialog.entry)
            self.refresh()

    def on_move_up_button_pressed(self):
        current_stacked_widget = self.stacked_widget.currentWidget()
        current_stacked_widget.on_move_up_button_pressed()

    def on_move_down_button_pressed(self):
        current_stacked_widget = self.stacked_widget.currentWidget()
        current_stacked_widget.on_move_down_button_pressed()

    def on_move_left_button_pressed(self):
        current_stacked_widget = self.stacked_widget.currentWidget()
        current_stacked_widget.on_move_left_button_pressed()

    def on_move_right_button_pressed(self):
        current_stacked_widget = self.stacked_widget.currentWidget()
        current_stacked_widget.on_move_right_button_pressed()
