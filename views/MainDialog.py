from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui

from views.Outliner import Outliner
from views.PreviewerTabBar import PreviewerTabBar
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
        self.save_action = QtWidgets.QAction("Save as .JSON", self)

        self.display_menu = self.menu_bar.addMenu("Display")
        self.show_hidden_action = QtWidgets.QAction("Show Hidden", self)
        self.show_hidden_action.setCheckable(True)
        self.show_hidden_action.setChecked(False)

        self.command_menu = self.menu_bar.addMenu("Command")
        self.new_tab_action = QtWidgets.QAction("New Tab", self)
        self.rename_tab_action = QtWidgets.QAction("Rename Tab", self)
        self.close_tab_action = QtWidgets.QAction("Close Tab", self)

        self.tool_bar = QtWidgets.QToolBar()
        self.tool_bar.setContentsMargins(0, 0, 0, 0)
        tool_bar_button_style = "QToolButton{background:transparent; padding:0px; margin:0px }"
        self.clear_button = QtWidgets.QToolButton()
        self.clear_button.setIcon(QtGui.QIcon(":hsClearView.png"))
        self.clear_button.setStyleSheet(tool_bar_button_style)
        self.add_button = QtWidgets.QToolButton()
        self.add_button.setIcon(QtGui.QIcon(":nodeGrapherAddNodes.png"))
        self.add_button.setStyleSheet(tool_bar_button_style)
        self.remove_button = QtWidgets.QToolButton()
        self.remove_button.setIcon(QtGui.QIcon(":nodeGrapherRemoveNodes.png"))
        self.remove_button.setStyleSheet(tool_bar_button_style)

        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Search...")

        self.outliner = Outliner(self)
        self.outliner.setMinimumWidth(200)

        self.previewer_tab_bar = PreviewerTabBar()
        self.previewer_tab_bar.setMinimumWidth(600)

    def create_layouts(self):
        self.file_menu.addAction(self.save_action)
        self.display_menu.addAction(self.show_hidden_action)
        self.command_menu.addAction(self.new_tab_action)
        self.command_menu.addAction(self.rename_tab_action)
        self.command_menu.addAction(self.close_tab_action)

        self.tool_bar.addWidget(self.clear_button)
        self.tool_bar.addWidget(self.add_button)
        self.tool_bar.addWidget(self.remove_button)

        tool_bar_layout = QtWidgets.QHBoxLayout()
        tool_bar_layout.addWidget(self.tool_bar)
        tool_bar_layout.setSpacing(0)

        outliner_layout = QtWidgets.QVBoxLayout()
        outliner_layout.addWidget(self.search_bar)
        outliner_layout.addWidget(self.outliner)

        previewer_layout = QtWidgets.QVBoxLayout()
        previewer_layout.addWidget(self.previewer_tab_bar)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addLayout(outliner_layout)
        bottom_layout.addLayout(previewer_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(11, 0, 11, 11)
        main_layout.setMenuBar(self.menu_bar)
        main_layout.addLayout(tool_bar_layout)
        main_layout.addLayout(bottom_layout)

        self.setMinimumHeight(550)

    def create_connections(self):
        self.finished.connect(self.on_finished)
        self.search_bar.textEdited.connect(self.on_search_bar_text_edited)
        self.clear_button.clicked.connect(self.previewer_tab_bar.clear_active_widget)
        self.add_button.clicked.connect(self.on_add_button_clicked)
        self.remove_button.clicked.connect(self.on_remove_button_clicked)
        self.save_action.triggered.connect(self.on_save_action_triggered)
        self.new_tab_action.triggered.connect(self.previewer_tab_bar.new_tab)
        self.rename_tab_action.triggered.connect(self.previewer_tab_bar.rename_current_tab)
        self.close_tab_action.triggered.connect(self.previewer_tab_bar.close_current_tab)

    def on_search_bar_text_edited(self):
        text = self.search_bar.text()
        self.outliner.search(text)

    def on_save_action_triggered(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self, "Save As", "", "json")
        if path:
            self.previewer_tab_bar.save_to_file(path[0])

    def on_add_button_clicked(self):
        items = self.outliner.selectedItems()
        self.previewer_tab_bar.add_to_active_widget(items)

    def on_remove_button_clicked(self):
        items = self.outliner.selectedItems()
        self.previewer_tab_bar.remove_from_active_widget(items)

    def on_finished(self, result):
        utils.deregister_callbacks(self.outliner.callback_ids)
