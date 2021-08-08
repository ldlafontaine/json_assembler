from PySide2 import QtWidgets, QtCore, QtGui

from ..models.Entry import Entry
from ..models.Attribute import Attribute
from ..models.Node import Node


class PropertiesDialog(QtWidgets.QDialog):

    def __init__(self, entry=None, parent=None):
        super(PropertiesDialog, self).__init__(parent)

        self.entry = entry

        if self.entry:
            self.setWindowTitle("Edit Entry")
        else:
            self.setWindowTitle("Create New Entry")

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.initialize_widget_values()
        self.initialize_widget_visibility()

    def create_widgets(self):
        self.name_label = QtWidgets.QLabel("Name:")
        self.name_label.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.name_field = QtWidgets.QLineEdit()

        self.group_box = QtWidgets.QGroupBox("Value")

        self.type_label = QtWidgets.QLabel("Type:")
        self.type_label.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.type_field = QtWidgets.QComboBox()
        self.type_field.setView(QtWidgets.QListView())
        self.type_field.addItem("String")
        self.type_field.addItem("Number")
        self.type_field.addItem("Object")
        self.type_field.addItem("Array")
        self.type_field.addItem("Boolean")
        self.type_field.addItem("Null")
        self.type_field.addItem("Maya Object")
        self.type_field.model().item(6).setEnabled(False)
        self.type_field.view().setRowHidden(6, True)

        self.string_widget = QtWidgets.QWidget()
        self.string_value_label = QtWidgets.QLabel("String:")
        self.string_value_label.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.string_value_field = QtWidgets.QLineEdit()

        self.number_widget = QtWidgets.QWidget()
        self.number_value_label = QtWidgets.QLabel("Number:")
        self.number_value_label.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.number_value_field = QtWidgets.QLineEdit()
        self.number_value_field.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("\\d*\\.?\\d*"), self.number_value_field))

        self.boolean_widget = QtWidgets.QWidget()
        self.boolean_value_label = QtWidgets.QLabel("Boolean:")
        self.boolean_value_label.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.boolean_true_field = QtWidgets.QRadioButton("True")
        self.boolean_true_field.setChecked(True)
        self.boolean_true_field.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.boolean_false_field = QtWidgets.QRadioButton("False")

        self.accept_button = QtWidgets.QPushButton("Accept")
        self.cancel_button = QtWidgets.QPushButton("Cancel")

    def create_layouts(self):
        name_layout = QtWidgets.QHBoxLayout()
        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.name_field)

        type_layout = QtWidgets.QHBoxLayout()
        type_layout.addWidget(self.type_label)
        type_layout.addWidget(self.type_field)

        string_layout = QtWidgets.QHBoxLayout()
        string_layout.setContentsMargins(0, 0, 0, 0)
        string_layout.addWidget(self.string_value_label)
        string_layout.addWidget(self.string_value_field)
        self.string_widget.setLayout(string_layout)

        number_layout = QtWidgets.QHBoxLayout()
        number_layout.setContentsMargins(0, 0, 0, 0)
        number_layout.addWidget(self.number_value_label)
        number_layout.addWidget(self.number_value_field)
        self.number_widget.setLayout(number_layout)

        boolean_layout = QtWidgets.QHBoxLayout()
        boolean_layout.setContentsMargins(0, 0, 0, 0)
        boolean_layout.addWidget(self.boolean_value_label)
        boolean_layout.addSpacing(10)
        boolean_layout.addWidget(self.boolean_true_field)
        boolean_layout.addWidget(self.boolean_false_field)
        self.boolean_widget.setLayout(boolean_layout)

        self.group_box_layout = QtWidgets.QVBoxLayout()
        self.group_box_layout.addLayout(type_layout)
        self.group_box_layout.addWidget(self.string_widget)
        self.group_box_layout.addWidget(self.number_widget)
        self.group_box_layout.addWidget(self.boolean_widget)
        self.group_box.setLayout(self.group_box_layout)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(self.accept_button)
        bottom_layout.addWidget(self.cancel_button)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(name_layout)
        main_layout.addWidget(self.group_box)
        main_layout.addStretch()
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

    def create_connections(self):
        self.accept_button.clicked.connect(self.on_accept_button_clicked)
        self.cancel_button.clicked.connect(self.on_cancel_button_clicked)
        self.type_field.currentIndexChanged.connect(self.update_widget_visibility)

    def sizeHint(self):
        return QtCore.QSize(350, 175)

    def value_is_string(self, entry):
        if isinstance(entry.value, str):
            return True
        return False

    def value_is_number(self, entry):
        number_types = [int, float, complex]
        for number_type in number_types:
            if isinstance(entry.value, number_type):
                return True
        return False

    def value_is_object(self, entry):
        if isinstance(entry.value, dict):
            return True
        return False

    def value_is_array(self, entry):
        if isinstance(entry.value, list):
            return True
        return False

    def value_is_bool(self, entry):
        if isinstance(entry.value, bool):
            return True
        return False

    def initialize_widget_values(self):
        if self.entry:
            self.name_field.setText(self.entry.title)

            if isinstance(self.entry, Attribute) or isinstance(self.entry, Node):
                self.type_field.setDisabled(True)
                self.type_field.setCurrentIndex(6)
            elif self.value_is_string(self.entry):
                self.type_field.setCurrentIndex(0)
            elif self.value_is_number(self.entry):
                self.type_field.setCurrentIndex(1)
            elif self.value_is_object(self.entry):
                self.type_field.setCurrentIndex(2)
            elif self.value_is_array(self.entry):
                self.type_field.setCurrentIndex(3)
            elif self.value_is_bool(self.entry):
                self.type_field.setCurrentIndex(4)
            else:
                self.type_field.setCurrentIndex(5)

    def initialize_widget_visibility(self):
        self.update_widget_visibility(self.type_field.currentIndex())

    def update_widget_visibility(self, index):
        self.string_widget.setVisible(False)
        self.number_widget.setVisible(False)
        self.boolean_widget.setVisible(False)

        if index == 0:
            self.string_widget.setVisible(True)
        elif index == 1:
            self.number_widget.setVisible(True)
        elif index == 4:
            self.boolean_widget.setVisible(True)

    def on_accept_button_clicked(self):
        if not self.entry:
            self.entry = Entry(self.name_field.text())
        else:
            self.entry.title = self.name_field.text()

        index = self.type_field.currentIndex()
        if index == 0:
            self.entry.value = self.string_value_field.text()
        elif index == 1:
            self.entry.value = float(self.number_value_field.text())
        elif index == 2:
            self.entry.value = {}
        elif index == 3:
            self.entry.value = []
        elif index == 4:
            self.entry.value = self.boolean_true_field.isChecked()
        elif index == 5:
            self.entry.value = None

        self.accept()

    def on_cancel_button_clicked(self):
        self.reject()
