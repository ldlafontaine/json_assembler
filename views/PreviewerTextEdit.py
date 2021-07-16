from PySide2 import QtCore, QtWidgets, QtGui

from PreviewerLineNumber import PreviewerLineNumber
from models.File import File


class PreviewerTextEdit(QtWidgets.QPlainTextEdit):
    def __init__(self, parent=None):
        super(PreviewerTextEdit, self).__init__(parent)

        self.create_widgets()
        self.create_connections()

        self.update_line_number_area_width(0)
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)
        #self.setReadOnly(True)
        self.document().setDocumentMargin(8)

        self.file = File()

    def create_widgets(self):
        self.line_number_area = PreviewerLineNumber(self)

    def create_connections(self):
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        # self.cursorPositionChanged.connect(self.highlight_current_line)

    def line_number_area_width(self):
        digits = 1
        max_value = max(1, self.blockCount())
        while max_value >= 10:
            max_value /= 10
            digits += 1
        space = 22 + self.fontMetrics().width('9') * digits
        return max(space, 40)

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super(PreviewerTextEdit, self).resizeEvent(event)
        contents_rect = self.contentsRect()
        self.line_number_area.setGeometry(QtCore.QRect(contents_rect.left(), contents_rect.top(),
                                                       self.line_number_area_width(), contents_rect.height()))

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QtWidgets.QTextEdit.ExtraSelection()
            line_color = QtGui.QColor(255, 255, 150)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def line_number_area_paint_event(self, event):
        painter = QtGui.QPainter(self.line_number_area)

        painter.fillRect(event.rect(), QtGui.QColor(40, 40, 40))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # Just to make sure I use the right font
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(block_number + 1)
                painter.setPen(QtGui.QColor(90, 90, 90))
                painter.drawText(-8, top, self.line_number_area.width(), height, QtCore.Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def refresh(self):
        self.setPlainText(self.file.get_formatted_text())

    def add_element(self, data):
        self.file.add_element(data)
        self.refresh()

    def remove_element(self, data):
        self.file.remove_element(data)
        self.refresh()

    def clear_elements(self):
        self.file.clear_elements()
        self.refresh()