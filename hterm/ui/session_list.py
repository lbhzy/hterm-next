from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QListWidget,
    QListWidgetItem,
)


class SessionList(QDockWidget):
    """会话列表栏"""

    # 请求打开会话信号，携带会话配置
    requested = Signal(dict)

    def __init__(self, parent=None):
        super().__init__("会话列表", parent)

        self.list_widget = QListWidget(self)
        self.list_widget.setFocusPolicy(Qt.NoFocus)
        self.list_widget.setSpacing(1)
        self.list_widget.itemDoubleClicked.connect(
            lambda item: self.requested.emit(item.session)
        )
        self.setWidget(self.list_widget)

    def load_sessions(self, config: dict):
        """载入会话到列表"""
        self.list_widget.clear()
        if not config:
            return

        for session in config["session"]:
            item = QListWidgetItem(session["name"])
            item.session = session
            self.list_widget.addItem(item)


if __name__ == "__main__":
    app = QApplication()
    w = SessionList()
    config = {
        "session": [
            {"name": "session1", "type": "local", "progname": "zsh"},
            {
                "name": "session2",
                "type": "serial",
                "port": "/dev/cu.debug-console",
                "baudrate": 115200,
            },
            {
                "name": "session3",
                "type": "ssh",
                "server": "10.10.10.1",
                "port": 22,
                "username": "root",
                "password": "password",
            },
        ]
    }
    w.load_sessions(config)
    w.requested.connect(lambda session: print(session))
    w.show()
    app.exec()
