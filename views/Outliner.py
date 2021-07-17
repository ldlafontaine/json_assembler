from PySide2 import QtWidgets, QtCore

from OutlinerTreeWidget import OutlinerTreeWidget


class Outliner(QtWidgets.QWidget):

    selection_activated = QtCore.Signal()

    def __init__(self, parent=None):
        super(Outliner, self).__init__(parent)

        self.create_widgets()
        self.create_layout()

    def create_widgets(self):
        self.stacked_widget = QtWidgets.QStackedWidget()
        self.insert_tab(0)

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.stacked_widget)

    def insert_tab(self, index):
        self.stacked_widget.insertWidget(index, OutlinerTreeWidget(self))
        self.stacked_widget.setCurrentIndex(index)

    def close_tab(self, index):
        stacked_widget = self.stacked_widget.widget(index)
        self.stacked_widget.removeWidget(stacked_widget)

    def refresh(self, data):
        current_stacked_widget = self.stacked_widget.currentWidget()
        current_stacked_widget.refresh(data)

    def clear_selection(self):
        self.blockSignals(True)
        current_stacked_widget = self.stacked_widget.currentWidget()
        selected_items = current_stacked_widget.selectedItems()
        for item in selected_items:
            item.setSelected(False)
        self.blockSignals(False)

    def get_flattened_data_from_selected(self):
        data = set()
        current_stacked_widget = self.stacked_widget.currentWidget()
        selected_items = current_stacked_widget.selectedItems()
        for item in selected_items:
            item_data = item.data(0, QtCore.Qt.UserRole)
            data.add(item_data)
        return data
