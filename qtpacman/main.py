import os
import pmlib
from PySide6 import QtCore, QtWidgets, QtGui

ROOTDIR = os.path.dirname(os.path.dirname(os.path.normpath(__file__)))
ARTDIR = os.path.join(ROOTDIR, "artwork")


class PacmanWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PacmanWidget, self).__init__(parent)

        self.setMinimumHeight(32 * 15)
        self.setMinimumWidth(32 * 25)

        self._pixmaps = {}

    @property
    def logic(self):
        return self._logic

    @logic.setter
    def logic(self, v):
        self._logic = v
        self.update()

    def cached_wall_pixmap(self, bits):
        if bits not in self._pixmaps:
            pngfile = os.path.join(ARTDIR, f"wall-{bits}.png")
            self._pixmaps[bits] = QtGui.QPixmap(pngfile)

        return self._pixmaps[bits]

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)

        def paint_cell(cx, cy, pixmap):
            painter.drawPixmap(cx * 32, cy * 32, 32, 32, pixmap)

        def mask_to_suffix(cell):
            ordered = [1, 2, 4, 8]
            return "".join([str((cell & bit) // bit) for bit in ordered])

        pmmap = self.logic.map

        for ii in range(pmmap.width):
            for jj in range(pmmap.height):
                cell = pmmap[ii, jj]

                if cell & pmmap.WALL != 0:
                    suffix = mask_to_suffix(cell)
                    paint_cell(ii, jj, self.cached_wall_pixmap(suffix))

    def _unused_example(self, paint_cell):
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

        self.setWindowTitle("Pacman")

        self.make_menu_bar()

        self.main = QtWidgets.QWidget()
        self.setCentralWidget(self.main)

        self.mainlay = QtWidgets.QVBoxLayout(self.main)

        self.board = PacmanWidget()
        self.mainlay.addWidget(self.board)

        self.new()

    def make_menu_bar(self):
        mb = self.menuBar()

        game = mb.addMenu("&Game")
        game.addAction("New").triggered.connect(self.new)
        game.addAction("Exit").triggered.connect(self.close)

    def new(self):
        self.logic = pmlib.PacmanBoard()

        self.logic.load_from_string(pmlib.level1)

        self.board.logic = self.logic


def main():
    app = QtWidgets.QApplication([])

    app.main = MainWindow()
    app.main.show()

    app.exec()
