from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from terminal import Terminal
from channel_local import LocalChannel


class Session:
    def __init__(self, parent=None):
        self.terminal = Terminal(parent)
        self.channel = LocalChannel('zsh')
        
        self.terminal.input_ready.connect(self.channel.send_data)
        self.terminal.resized.connect(self.channel.send_window_size)
        self.channel.received.connect(self.terminal.feed)
        self.channel.connected.connect(lambda s: self.terminal.feed(s))
        self.channel.disconnected.connect(lambda s: self.terminal.feed(s))
        
        self.channel.connect()


if __name__ == "__main__":
    app = QApplication()
    session = Session()
    session.terminal.resize(960, 540)
    session.terminal.show()
    app.exec()