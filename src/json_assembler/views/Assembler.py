from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui

from Outliner import Outliner
from Explorer import Explorer
from Previewer import Previewer
from ..models import utils


def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class Assembler(QtWidgets.QDialog):

    def __init__(self, parent=get_maya_main_window()):
        super(Assembler, self).__init__(parent)

        self.setWindowTitle('JSON Assembler')

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.menu_bar = QtWidgets.QMenuBar()

        self.file_menu = self.menu_bar.addMenu("File")
        self.save_action = QtWidgets.QAction("Save As", self)
        self.save_with_indentation_action = QtWidgets.QAction("Save With Indentation", self)
        self.save_with_indentation_action.setCheckable(True)
        self.save_with_indentation_action.setChecked(False)

        self.display_menu = self.menu_bar.addMenu("Display")
        self.show_non_keyable_action = self.create_filter_action("Show Non-Keyable", True)
        self.show_connected_only_action = self.create_filter_action("Show Connected Only", False)
        self.show_hidden_action = self.create_filter_action("Show Hidden", False)

        self.command_menu = self.menu_bar.addMenu("Command")
        self.add_tab_action = QtWidgets.QAction("New Tab", self)
        self.rename_tab_action = QtWidgets.QAction("Rename Tab", self)
        self.close_tab_action = QtWidgets.QAction("Close Tab", self)
        self.close_all_tabs_action = QtWidgets.QAction("Close All Tabs", self)

        self.left_tool_bar = QtWidgets.QToolBar()
        self.left_tool_bar.setStyleSheet("QToolButton{background:transparent; border:0 }")
        self.save_button = QtWidgets.QToolButton()
        self.save_button.setIcon(QtGui.QIcon(":save.png"))
        self.clear_button = QtWidgets.QToolButton()
        self.clear_button.setIcon(QtGui.QIcon(":hsClearView.png"))
        self.add_button = QtWidgets.QToolButton()
        self.add_button.setIcon(QtGui.QIcon(":nodeGrapherAddNodes.png"))
        self.remove_button = QtWidgets.QToolButton()
        self.remove_button.setIcon(QtGui.QIcon(":nodeGrapherRemoveNodes.png"))

        self.right_tool_bar = QtWidgets.QToolBar()
        self.right_tool_bar.setStyleSheet("QToolButton{background:transparent; border:0}"
                                          "QToolButton:on{background:rgb(82,133,166)}")
        self.include_indentation_button = QtWidgets.QToolButton()
        self.include_indentation_button.setIcon(QtGui.QIcon(":increaseDepth.png"))
        self.include_indentation_button.setCheckable(True)
        self.include_indentation_button.setChecked(True)
        self.indentation_size_field = QtWidgets.QSpinBox()
        self.indentation_size_field.setRange(0, 10)
        self.indentation_size_field.setValue(4)
        self.indentation_size_field.setMinimumWidth(60)
        self.indentation_size_field.setMinimumHeight(24)

        label_font = QtGui.QFont()
        label_font.setBold(True)
        label_font.setPointSize(8)
        label_font.setCapitalization(QtGui.QFont.AllUppercase)

        self.explorer_label = QtWidgets.QLabel("Explorer")
        self.explorer_label.setFont(label_font)
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.explorer = Explorer(self)

        self.outliner_label = QtWidgets.QLabel("Outliner")
        self.outliner_label.setFont(label_font)
        self.outliner = Outliner(self)

        self.previewer = Previewer(self)

    def create_layouts(self):
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_with_indentation_action)

        self.display_menu.addAction(self.show_non_keyable_action)
        self.display_menu.addAction(self.show_connected_only_action)
        self.display_menu.addAction(self.show_hidden_action)

        self.command_menu.addAction(self.add_tab_action)
        self.command_menu.addAction(self.rename_tab_action)
        self.command_menu.addAction(self.close_tab_action)
        self.command_menu.addAction(self.close_all_tabs_action)

        self.left_tool_bar.addWidget(self.save_button)
        self.left_tool_bar.addWidget(self.clear_button)
        self.left_tool_bar.addWidget(self.add_button)
        self.left_tool_bar.addWidget(self.remove_button)
        # self.left_tool_bar.addWidget(self.refresh_button)

        self.right_tool_bar.addWidget(self.include_indentation_button)
        self.right_tool_bar.addWidget(self.indentation_size_field)

        tool_bar_layout = QtWidgets.QHBoxLayout()
        tool_bar_layout.addWidget(self.left_tool_bar)
        tool_bar_layout.addStretch()
        tool_bar_layout.addWidget(self.right_tool_bar)

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(self.explorer_label)
        left_layout.addWidget(self.search_bar)
        left_layout.addWidget(self.explorer, 2)
        left_layout.addWidget(self.outliner_label)
        left_layout.addWidget(self.outliner, 5)

        previewer_layout = QtWidgets.QVBoxLayout()
        previewer_layout.addWidget(self.previewer)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addLayout(left_layout, 1)
        bottom_layout.addLayout(previewer_layout, 3)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(11, 0, 11, 11)
        main_layout.setMenuBar(self.menu_bar)
        main_layout.addLayout(tool_bar_layout)
        main_layout.addLayout(bottom_layout)

    def create_connections(self):
        self.finished.connect(self.on_finished)

        self.save_button.clicked.connect(self.save_to_file)
        self.show_non_keyable_action.triggered.connect(self.explorer.set_show_non_keyable_enabled)
        self.show_connected_only_action.triggered.connect(self.explorer.set_show_connected_only_enabled)
        self.show_hidden_action.triggered.connect(self.explorer.set_show_hidden_enabled)

        self.clear_button.clicked.connect(self.outliner.clear_entries)
        self.add_button.clicked.connect(self.on_add_button_clicked)
        self.remove_button.clicked.connect(self.on_remove_button_clicked)
        self.save_action.triggered.connect(self.save_to_file)

        self.include_indentation_button.toggled.connect(self.previewer.set_include_indentation)
        self.indentation_size_field.valueChanged.connect(self.previewer.set_indentation_size)

        self.add_tab_action.triggered.connect(self.previewer.add_tab)
        self.rename_tab_action.triggered.connect(self.previewer.rename_current_tab)
        self.close_tab_action.triggered.connect(self.previewer.close_current_tab)
        self.close_all_tabs_action.triggered.connect(self.previewer.close_all_tabs)

        self.search_bar.textEdited.connect(self.on_search_bar_text_edited)
        self.previewer.tab_changed.connect(self.outliner.stacked_widget.setCurrentIndex)
        self.previewer.tab_added.connect(self.outliner.insert_tab)
        self.previewer.tab_closed.connect(self.outliner.close_tab)
        self.explorer.selection_activated.connect(self.outliner.clear_selection)
        self.outliner.selection_activated.connect(self.explorer.clearSelection)
        self.outliner.updated.connect(self.previewer.refresh)

    def create_filter_action(self, label, default_state):
        action = QtWidgets.QAction(label, self)
        action.setCheckable(True)
        action.setChecked(default_state)
        return action

    def get_active_file(self):
        current_widget = self.outliner.stacked_widget.currentWidget()
        return current_widget.file

    def save_to_file(self):
        save_with_indentation = self.save_with_indentation_action.isChecked()
        self.previewer.save_to_file(save_with_indentation)

    def on_search_bar_text_edited(self):
        text = self.search_bar.text()
        self.explorer.search(text)

    def on_add_button_clicked(self):
        data = self.explorer.get_data_from_selected(True)
        self.outliner.add_entries(data)

    def on_remove_button_clicked(self):
        explorer_entries = self.explorer.get_data_from_selected()
        self.outliner.remove_entries(explorer_entries)

    def on_finished(self, result):
        utils.deregister_callbacks(self.explorer.callback_ids)
