from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui

from views.Outliner import Outliner
from views.Explorer import Explorer
from views.Previewer import Previewer
from models import utils


def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class MainDialog(QtWidgets.QDialog):

    def __init__(self, parent=get_maya_main_window()):
        super(MainDialog, self).__init__(parent)

        self.setWindowTitle('JSON Builder')

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.menu_bar = QtWidgets.QMenuBar()

        self.file_menu = self.menu_bar.addMenu("File")
        self.save_action = QtWidgets.QAction("Save As", self)
        self.include_indentation_action = QtWidgets.QAction("Include Indentation", self)
        self.include_indentation_action.setCheckable(True)
        self.include_indentation_action.setChecked(False)

        self.display_menu = self.menu_bar.addMenu("Display")
        self.show_non_keyable_action = self.create_filter_action("Show Non-Keyable", True)
        self.show_connected_only_action = self.create_filter_action("Show Connected Only", False)
        self.show_hidden_action = self.create_filter_action("Show Hidden", False)

        self.command_menu = self.menu_bar.addMenu("Command")
        self.add_tab_action = QtWidgets.QAction("New Tab", self)
        self.rename_tab_action = QtWidgets.QAction("Rename Tab", self)
        self.close_tab_action = QtWidgets.QAction("Close Tab", self)
        self.close_all_tabs_action = QtWidgets.QAction("Close All Tabs", self)

        self.tool_bar = QtWidgets.QToolBar()
        self.tool_bar.setContentsMargins(0, 0, 0, 0)
        self.save_button = self.create_tool_bar_button(":save.png")
        self.clear_button = self.create_tool_bar_button(":hsClearView.png")
        self.add_button = self.create_tool_bar_button(":nodeGrapherAddNodes.png")
        self.remove_button = self.create_tool_bar_button(":nodeGrapherRemoveNodes.png")

        label_font = QtGui.QFont()
        label_font.setBold(True)
        label_font.setPointSize(8)
        label_font.setCapitalization(QtGui.QFont.AllUppercase)

        self.explorer_label = QtWidgets.QLabel("Explorer")
        self.explorer_label.setFont(label_font)
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.explorer = Explorer(self)
        self.explorer.setMinimumWidth(200)

        self.outliner_label = QtWidgets.QLabel("Outliner")
        self.outliner_label.setFont(label_font)
        self.outliner = Outliner(self)
        self.outliner.setMinimumHeight(350)

        self.previewer = Previewer()
        self.previewer.setMinimumWidth(800)

    def create_layouts(self):
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.include_indentation_action)

        self.display_menu.addAction(self.show_non_keyable_action)
        self.display_menu.addAction(self.show_connected_only_action)
        self.display_menu.addAction(self.show_hidden_action)

        self.command_menu.addAction(self.add_tab_action)
        self.command_menu.addAction(self.rename_tab_action)
        self.command_menu.addAction(self.close_tab_action)
        self.command_menu.addAction(self.close_all_tabs_action)

        self.tool_bar.addWidget(self.save_button)
        self.tool_bar.addWidget(self.clear_button)
        self.tool_bar.addWidget(self.add_button)
        self.tool_bar.addWidget(self.remove_button)

        tool_bar_layout = QtWidgets.QHBoxLayout()
        tool_bar_layout.addWidget(self.tool_bar)
        tool_bar_layout.setSpacing(0)

        outliner_layout = QtWidgets.QVBoxLayout()
        outliner_layout.addWidget(self.explorer_label)
        outliner_layout.addWidget(self.search_bar)
        outliner_layout.addWidget(self.explorer)
        outliner_layout.addWidget(self.outliner_label)
        outliner_layout.addWidget(self.outliner)

        previewer_layout = QtWidgets.QVBoxLayout()
        previewer_layout.addWidget(self.previewer)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addLayout(outliner_layout)
        bottom_layout.addLayout(previewer_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(11, 0, 11, 11)
        main_layout.setMenuBar(self.menu_bar)
        main_layout.addLayout(tool_bar_layout)
        main_layout.addLayout(bottom_layout)

        self.setMinimumHeight(600)

    def create_connections(self):
        self.finished.connect(self.on_finished)

        self.save_button.clicked.connect(self.save_to_file)
        self.show_non_keyable_action.triggered.connect(self.explorer.set_show_non_keyable_enabled)
        self.show_connected_only_action.triggered.connect(self.explorer.set_show_connected_only_enabled)
        self.show_hidden_action.triggered.connect(self.explorer.set_show_hidden_enabled)

        self.clear_button.clicked.connect(self.previewer.clear_active_widget)
        self.add_button.clicked.connect(self.on_add_button_clicked)
        self.remove_button.clicked.connect(self.on_remove_button_clicked)
        self.save_action.triggered.connect(self.save_to_file)
        self.add_tab_action.triggered.connect(self.previewer.add_tab)
        self.rename_tab_action.triggered.connect(self.previewer.rename_current_tab)
        self.close_tab_action.triggered.connect(self.previewer.close_current_tab)
        self.close_all_tabs_action.triggered.connect(self.previewer.close_all_tabs)

        self.search_bar.textEdited.connect(self.on_search_bar_text_edited)
        self.previewer.refreshed.connect(self.outliner.refresh)
        self.previewer.tab_changed.connect(self.outliner.stacked_widget.setCurrentIndex)
        self.previewer.tab_added.connect(self.outliner.insert_tab)
        self.previewer.tab_closed.connect(self.outliner.close_tab)
        self.explorer.selection_activated.connect(self.outliner.clear_selection)
        self.outliner.selection_activated.connect(self.explorer.clear_selection)

    def create_filter_action(self, label, default_state):
        action = QtWidgets.QAction(label, self)
        action.setCheckable(True)
        action.setChecked(default_state)
        return action

    def create_tool_bar_button(self, image_path):
        button = QtWidgets.QToolButton()
        button.setIcon(QtGui.QIcon(image_path))
        button.setStyleSheet("QToolButton{background:transparent; padding:0px; margin:0px }")
        return button

    def save_to_file(self):
        include_indentation = self.include_indentation_action.isChecked()
        self.previewer.save_to_file(include_indentation)

    def on_search_bar_text_edited(self):
        text = self.search_bar.text()
        self.explorer.search(text)

    def on_add_button_clicked(self):
        data = self.explorer.get_data_from_selected()
        self.previewer.add_to_active_widget(data)

    def on_remove_button_clicked(self):
        explorer_data = self.explorer.get_flattened_data_from_selected()
        outliner_data = self.outliner.get_flattened_data_from_selected()
        self.previewer.remove_from_active_widget(explorer_data)
        self.previewer.remove_from_active_widget(outliner_data)

    def on_finished(self, result):
        utils.deregister_callbacks(self.explorer.callback_ids)
