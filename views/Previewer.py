from PySide2 import QtWidgets, QtCore, QtGui

from views.PreviewerTextEdit import PreviewerTextEdit


class Previewer(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(Previewer, self).__init__(parent)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.new_tab()

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

    def new_tab(self):
        index = self.tab_bar.count() - 1
        label = self.get_default_tab_label()
        self.tab_bar.insertTab(index, label)
        self.stacked_widget.addWidget(PreviewerTextEdit())
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
        # Validate whether this is an appropriate tab to remove.
        count = self.tab_bar.count()
        if index == count - 1 or count <= 2:
            return
        # Remove tab and associated stacked widget element.
        current_stacked_widget = self.stacked_widget.currentWidget()
        self.stacked_widget.removeWidget(current_stacked_widget)
        self.tab_bar.removeTab(index)

    def close_current_tab(self):
        current_index = self.tab_bar.currentIndex()
        self.close_tab(current_index)

    def close_all_tabs(self):
        index = 0
        count = self.tab_bar.count() - 1
        print count
        while index < count:
            print "while iter " + str(index)
            self.tab_bar.removeTab(0)
            stacked_widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(stacked_widget)
            index += 1
        self.new_tab()

    def rename_tab(self, index):
        name, result = QtWidgets.QInputDialog.getText(self, "Rename Tab", "New tab name:")
        if result:
            self.tab_bar.setTabText(index, name)

    def rename_current_tab(self):
        current_index = self.tab_bar.currentIndex()
        self.rename_tab(current_index)

    def add_to_active_widget(self, items):
        for item in items:
            data = item.data(0, QtCore.Qt.UserRole)
            self.stacked_widget.currentWidget().add_element(data)

    def remove_from_active_widget(self, items):
        for item in items:
            data = item.data(0, QtCore.Qt.UserRole)
            self.stacked_widget.currentWidget().remove_element(data)

    def clear_active_widget(self):
        self.stacked_widget.currentWidget().clear_elements()

    def refresh(self):
        current_widget = self.stacked_widget.currentWidget()
        current_widget.refresh()

    def save_to_file(self, include_indentation):
        path = QtWidgets.QFileDialog.getSaveFileName(self, "Save As", "", "JSON (*.json)")
        if len(path[0]) > 0:
            current_widget = self.stacked_widget.currentWidget()
            current_widget.file.save_to_file(path[0], include_indentation)

    def on_tab_bar_clicked(self, tab_index):
        # Add a new tab if last tab is clicked.
        if tab_index == self.tab_bar.count() - 1:
            self.new_tab()

    def on_current_changed(self, index):
        if index == self.tab_bar.count() - 1:
            self.tab_bar.setCurrentIndex(index - 1)
            self.stacked_widget.setCurrentIndex(index - 1)
        else:
            self.stacked_widget.setCurrentIndex(index)