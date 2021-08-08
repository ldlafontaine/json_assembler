from PySide2 import QtWidgets, QtCore

from PreviewerTextEdit import PreviewerTextEdit


class Previewer(QtWidgets.QWidget):

    tab_changed = QtCore.Signal(int)
    tab_added = QtCore.Signal(int)
    tab_closed = QtCore.Signal(int)

    def __init__(self, parent=None):
        super(Previewer, self).__init__(parent)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.include_indentation = True
        self.indentation_size = 4

        self.add_tab()

    def create_widgets(self):
        self.tab_bar = QtWidgets.QTabBar()
        self.tab_bar.setObjectName("previewerTabBar")
        self.tab_bar.setStyleSheet("#previewerTabBar {background-color: #383838}")
        self.tab_bar.setExpanding(False)
        self.tab_bar.setUsesScrollButtons(True)
        self.tab_bar.addTab("+")

        self.stacked_widget = QtWidgets.QStackedWidget()
        self.stacked_widget.setObjectName("previewerStackedWidget")
        self.stacked_widget.setStyleSheet("#previewerStackedWidget {border: 1px solid #2e2e2e}")

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.tab_bar)
        main_layout.addWidget(self.stacked_widget)

    def create_connections(self):
        self.tab_bar.tabBarClicked.connect(self.on_tab_bar_clicked)
        self.tab_bar.currentChanged.connect(self.on_current_changed)

    def sizeHint(self):
        return QtCore.QSize(800, 550)

    def add_tab(self):
        count = self.tab_bar.count()
        index = count - 1 if count > 0 else 0
        label = self.get_default_tab_label()
        self.tab_bar.insertTab(index, label)
        self.stacked_widget.insertWidget(index, PreviewerTextEdit())
        self.tab_added.emit(index)
        self.tab_bar.setCurrentIndex(index)
        return index

    def get_default_tab_label(self):
        labels = []
        for tab_index in range(self.tab_bar.count()):
            labels.append(self.tab_bar.tabText(tab_index))
        index = 1
        while True:
            label = "Untitled - " + str(index)
            index += 1
            if label not in labels:
                break
        return label

    def close_tab(self, index):
        # Prevent new tab button from being deleted.
        count = self.tab_bar.count()
        if index == count - 1:
            return
        # Remove tab and associated stacked widget element.
        stacked_widget = self.stacked_widget.widget(index)
        self.stacked_widget.removeWidget(stacked_widget)
        self.tab_bar.removeTab(index)
        self.tab_closed.emit(index)
        # If deleted tab was the only remaining tab, replace it.
        if count <= 2:
            self.add_tab()

    def close_current_tab(self):
        current_index = self.tab_bar.currentIndex()
        self.close_tab(current_index)

    def close_all_tabs(self):
        index = 0
        count = self.tab_bar.count() - 1
        while index < count:
            self.close_tab(0)
            index += 1

    def rename_tab(self, index):
        name, result = QtWidgets.QInputDialog.getText(self, "Rename Tab", "New tab name:")
        if result:
            self.tab_bar.setTabText(index, name)

    def rename_current_tab(self):
        current_index = self.tab_bar.currentIndex()
        self.rename_tab(current_index)

    def set_include_indentation(self, include_indentation):
        self.include_indentation = include_indentation
        self.refresh()

    def set_indentation_size(self, indentation_size):
        self.indentation_size = indentation_size
        self.refresh()

    def refresh(self):
        active_file = self.parent().get_active_file()
        text = active_file.encode(self.include_indentation, self.indentation_size)
        current_widget = self.stacked_widget.currentWidget()
        current_widget.refresh(text)

    def on_tab_bar_clicked(self, tab_index):
        # Add a new tab if last tab is clicked.
        if tab_index == self.tab_bar.count() - 1:
            self.add_tab()

    def on_current_changed(self, index):
        if index == self.tab_bar.count() - 1:
            index -= 1
        self.tab_changed.emit(index)
        self.tab_bar.setCurrentIndex(index)
        self.stacked_widget.setCurrentIndex(index)
        self.refresh()
