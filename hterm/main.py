from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from hterm.ui import MainWindow


class Hterm(MainWindow):
    def __init__(self):
        super().__init__()



if __name__ == '__main__':
    app = QApplication()
    # app.setStyle('Fusion')
    app.setApplicationName("hterm")
    hterm = Hterm()
    hterm.show()
    app.exec()