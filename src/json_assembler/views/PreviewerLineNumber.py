from PySide2 import QtCore, QtWidgets


class PreviewerLineNumber(QtWidgets.QWidget):
    def __init__(self, editor):
        super(PreviewerLineNumber, self).__init__(editor)
        self.text_edit = editor

    def sizeHint(self):
        return QtCore.QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.text_edit.line_number_area_paint_event(event)