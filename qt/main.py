import os
from PySide6 import QtCore, QtWidgets, QtGui

ROOTDIR = os.path.dirname(os.path.dirname(os.path.normpath(__file__)))
ARTDIR = os.path.join(ROOTDIR, "artwork")


class PacmanWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PacmanWidget, self).__init__(parent)

        self.setMinimumHeight(32 * 15)
        self.setMinimumWidth(32 * 25)

    def paintEvent(self, e):
        painter = QtWidgets.QPainter(self)

        painter.begin(self)

        pix0101 = QtGui.QPixmap(os.path.join(ARTDIR, "wall-0101.png"))
        pix0110 = QtGui.QPixmap(os.path.join(ARTDIR, "wall-0110.png"))
        pix0011 = QtGui.QPixmap(os.path.join(ARTDIR, "wall-0011.png"))

        def paint_cell(cx, cy, pixmap):
            painter.drawPixmap(cx * 32, cy * 32, (cx + 1) * 32, (cy + 1) * 32, pix0110)

        paint_cell(1, 2, pix0110)
        paint_cell(1, 3, pix0101)
        paint_cell(1, 4, pix0011)

        painter.end()


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

    app.exec_()
