from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from config import Config


class SessionListWidget(QDockWidget):
    def __init__(self, parent=None):
        super().__init__('会话列表', parent)
        self.setFocusPolicy(Qt.NoFocus)
        list_widget = QListWidget(self)
        self.setWidget(list_widget)

        self.cfg = Config('session')
        data = self.cfg.load()
        if 'session' in data:
            for session in data['session']:
                item = QListWidgetItem(session['name'])
                list_widget.addItem(item)


if __name__ == '__main__':
    app = QApplication()
    widget = SessionListWidget()

    widget.show()
    app.exec()