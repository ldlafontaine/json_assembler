from PySide2 import QtCore, QtWidgets


class PreviewerLineNumber(QtWidgets.QWidget):
    def __init__(self, editor):
        super(PreviewerLineNumber, self).__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QtCore.QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.codeEditor.line_number_area_paint_event(event)
