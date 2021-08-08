from PySide2 import QtWidgets, QtCore, QtGui

from OutlinerTreeWidget import OutlinerTreeWidget


class Outliner(QtWidgets.QWidget):

    updated = QtCore.Signal(object)
    selection_activated = QtCore.Signal()

    def __init__(self, parent=None):
        super(Outliner, self).__init__(parent)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

        # Set behaviour and styling.
        self.setMinimumWidth(225)

    def create_widgets(self):
        label_font = QtGui.QFont()
        label_font.setBold(True)
        label_font.setPointSize(8)
        label_font.setCapitalization(QtGui.QFont.AllUppercase)

        self.title_label = QtWidgets.QLabel("Outliner")
        self.title_label.setFont(label_font)

        self.stacked_widget = QtWidgets.QStackedWidget()
        self.insert_tab(0)

        self.left_tool_bar = QtWidgets.QToolBar()
        self.left_tool_bar.setStyleSheet("QToolButton{background:transparent; border:0 }")
        self.new_button = QtWidgets.QToolButton()
        self.new_button.setIcon(QtGui.QIcon(":fileNew.png"))
        self.new_button.setStatusTip("Create new entry")
        self.edit_button = QtWidgets.QToolButton()
        self.edit_button.setIcon(QtGui.QIcon(":greasePencilPencil.png"))
        self.edit_button.setStatusTip("Edit entry")

        self.right_tool_bar = QtWidgets.QToolBar()
        self.right_tool_bar.setStyleSheet("QToolButton{background:transparent; border:0 }")
        self.move_up_button = QtWidgets.QToolButton()
        self.move_up_button.setIcon(QtGui.QIcon(":moveUVUp.png"))
        self.move_up_button.setStatusTip("Move entries up")
        self.move_down_button = QtWidgets.QToolButton()
        self.move_down_button.setIcon(QtGui.QIcon(":moveUVDown.png"))
        self.move_down_button.setStatusTip("Move entries down")
        self.move_left_button = QtWidgets.QToolButton()
        self.move_left_button.setIcon(QtGui.QIcon(":moveUVLeft.png"))
        self.move_left_button.setStatusTip("Move entries left")
        self.move_right_button = QtWidgets.QToolButton()
        self.move_right_button.setIcon(QtGui.QIcon(":moveUVRight.png"))
        self.move_right_button.setStatusTip("Move entries right")

    def create_layout(self):
        top_layout = QtWidgets.QVBoxLayout()
        top_layout.setContentsMargins(0, 8, 0, 0)
        top_layout.setSpacing(8)
        top_layout.addWidget(self.title_label)
        top_layout.addWidget(self.stacked_widget)

        self.left_tool_bar.addWidget(self.new_button)
        self.left_tool_bar.addWidget(self.edit_button)

        self.right_tool_bar.addWidget(self.move_up_button)
        self.right_tool_bar.addWidget(self.move_down_button)
        self.right_tool_bar.addWidget(self.move_left_button)
        self.right_tool_bar.addWidget(self.move_right_button)

        tool_bar_layout = QtWidgets.QHBoxLayout()
        tool_bar_layout.addWidget(self.left_tool_bar)
        tool_bar_layout.addStretch()
        tool_bar_layout.addWidget(self.right_tool_bar)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(tool_bar_layout)
        self.setLayout(main_layout)

    def create_connections(self):
        self.new_button.clicked.connect(lambda: self.stacked_widget.currentWidget().new_entry())
        self.edit_button.clicked.connect(lambda: self.stacked_widget.currentWidget().edit_entry())
        self.move_up_button.clicked.connect(lambda: self.stacked_widget.currentWidget().move_up())
        self.move_down_button.clicked.connect(lambda: self.stacked_widget.currentWidget().move_down())
        self.move_left_button.clicked.connect(lambda: self.stacked_widget.currentWidget().move_left())
        self.move_right_button.clicked.connect(lambda: self.stacked_widget.currentWidget().move_right())

    def sizeHint(*args, **kwargs):
        return QtCore.QSize(225, 325)

    def insert_tab(self, index):
        self.stacked_widget.insertWidget(index, OutlinerTreeWidget(self))
        self.stacked_widget.setCurrentIndex(index)

    def close_tab(self, index):
        stacked_widget = self.stacked_widget.widget(index)
        self.stacked_widget.removeWidget(stacked_widget)

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
