from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

import queue
import threading

from tty_channel import TtyChannel
from terminal import Terminal


class Session(Terminal):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tty = TtyChannel('shell', 'zsh')
        self.tty.open()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.reading_tty)
        self.timer.start(10)

    def reading_tty(self):
        text = self.tty.read_non_blocking(1024)
        if text:
            self.feed(text)

    def send(self, text):
        self.tty.write(text)

    def resizeEvent(self, event):
        """窗口大小改变时重新计算滚动条"""
        lines = int(self.viewport().height()/self.line_height)
        cols = int(self.viewport().width()/self.char_width)
        self.tty.resize(lines, cols)
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication()
    window = Session()
    window.resize(600, 400)
    window.resized.connect(lambda row, cols: print(f'window size: ({row}, {cols})'))
    window.show()
    app.exec()