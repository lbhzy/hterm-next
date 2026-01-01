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
    config_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__("会话列表", parent)

        self.list_widget = QListWidget(self)
        self.list_widget.setFocusPolicy(Qt.NoFocus)
        self.list_widget.setSpacing(1)
        self.list_widget.itemDoubleClicked.connect(self.request_open_session)
        self.setWidget(self.list_widget)

    def load_sessions(self, config: dict):
        """载入会话到列表"""
        self.list_widget.clear()
        sessions = config.get("session", [])
        for session in sessions:
            item = QListWidgetItem(self.get_session_name(session))
            item.session = session
            self.list_widget.addItem(item)

    def add_session(self, config: dict):
        """新添加会话到列表"""
        item = QListWidgetItem(self.get_session_name(config))
        item.session = config
        self.list_widget.addItem(item)
        self.config_changed.emit(self.get_all_sessions())

    def request_open_session(self, item):
        """请求打开会话"""
        session = item.session
        session["name"] = self.get_session_name(session)
        self.requested.emit(session)

    def get_session_name(self, config: dict) -> str:
        name = config["name"]
        if not name:
            if config["type"] == "ssh":
                name = config["server"]
            elif config["type"] == "serial":
                name = config["port"]
            elif config["type"] == "local":
                name = config["progname"]
        return name

    def get_all_sessions(self) -> dict:
        """获取所有会话配置"""
        sessions = []
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            sessions.append(item.session)
        return {"session": sessions}


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
