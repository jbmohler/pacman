import os
from PySide6 import QtCore, QtWidgets, QtGui

ROOTDIR = os.path.dirname(os.path.dirname(os.path.normpath(__file__)))
ARTDIR = os.path.join(ROOTDIR, "artwork")


class PacmanWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PacmanWidget, self).__init__(parent)

        self.setMinimumHeight(32 * 15)
        self.setMinimumWidth(32 * 25)

        self._pixmaps = {}

    def cached_wall_pixmap(self, bits):
        if bits not in self._pixmaps:
            pngfile = os.path.join(ARTDIR, f"wall-{bits}.png")
            self._pixmaps[bits] = QtGui.QPixmap(pngfile)

        return self._pixmaps[bits]

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)

        def paint_cell(cx, cy, pixmap):
            painter.drawPixmap(cx * 32, cy * 32, 32, 32, pixmap)

        paint_cell(2, 2, self.cached_wall_pixmap("0110"))
        paint_cell(3, 2, self.cached_wall_pixmap("0101"))
        paint_cell(4, 2, self.cached_wall_pixmap("0111"))
        paint_cell(5, 2, self.cached_wall_pixmap("0101"))
        paint_cell(6, 2, self.cached_wall_pixmap("0011"))

        paint_cell(2, 3, self.cached_wall_pixmap("1010"))
        paint_cell(4, 3, self.cached_wall_pixmap("1010"))
        paint_cell(6, 3, self.cached_wall_pixmap("1010"))

        paint_cell(2, 4, self.cached_wall_pixmap("1110"))
        paint_cell(3, 4, self.cached_wall_pixmap("0101"))
        paint_cell(4, 4, self.cached_wall_pixmap("1111"))
        paint_cell(5, 4, self.cached_wall_pixmap("0101"))
        paint_cell(6, 4, self.cached_wall_pixmap("1011"))

        paint_cell(2, 5, self.cached_wall_pixmap("1010"))
        paint_cell(4, 5, self.cached_wall_pixmap("1010"))
        paint_cell(6, 5, self.cached_wall_pixmap("1010"))

        paint_cell(2, 6, self.cached_wall_pixmap("1100"))
        paint_cell(3, 6, self.cached_wall_pixmap("0101"))
        paint_cell(4, 6, self.cached_wall_pixmap("1101"))
        paint_cell(5, 6, self.cached_wall_pixmap("0101"))
        paint_cell(6, 6, self.cached_wall_pixmap("1001"))

        paint_cell(3, 5, self.cached_wall_pixmap("0000"))
        paint_cell(5, 3, self.cached_wall_pixmap("0000"))

        paint_cell(8, 3, self.cached_wall_pixmap("0010"))
        paint_cell(7, 4, self.cached_wall_pixmap("0100"))
        paint_cell(8, 4, self.cached_wall_pixmap("1111"))
        paint_cell(9, 4, self.cached_wall_pixmap("0001"))
        paint_cell(8, 5, self.cached_wall_pixmap("1000"))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.main = QtWidgets.QWidget()
        self.setCentralWidget(self.main)

        self.mainlay = QtWidgets.QVBoxLayout(self.main)

        self.board = PacmanWidget()
        self.mainlay.addWidget(self.board)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    app.main = MainWindow()
    app.main.show()

    app.exec()
