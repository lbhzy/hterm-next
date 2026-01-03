import qtawesome as qta
from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDockWidget,
    QListWidget,
    QListWidgetItem,
    QMenu,
)

from hterm.ui.session_dialog import SessionDialog


class SessionItem(QListWidgetItem):
    def __init__(self, config: dict):
        super().__init__()
        self.session = config
        self.load_config(config)

    def load_config(self, config: dict):
        if config["type"] == "ssh":
            name = config["server"]
            icon = qta.icon("mdi.ssh")
        elif config["type"] == "serial":
            name = config["port"]
            icon = qta.icon("mdi.serial-port")
        elif config["type"] == "local":
            name = config["progname"]
            icon = qta.icon("ri.mini-program-line")

        # 别名不为空，使用别名
        if config["name"]:
            name = config["name"]

        self.setText(name)
        self.setIcon(icon)


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
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        self.list_widget.model().rowsMoved.connect(
            lambda: self.config_changed.emit(self.get_all_sessions())
        )
        self.list_widget.itemDoubleClicked.connect(self.request_open_session)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.setWidget(self.list_widget)

    def load_sessions(self, config: dict):
        """载入会话到列表"""
        self.list_widget.clear()
        sessions = config.get("session", [])
        for session in sessions:
            item = SessionItem(session)
            self.list_widget.addItem(item)

    def add_session(self, config: dict):
        """新添加会话到列表"""
        item = SessionItem(config)
        self.list_widget.addItem(item)
        self.config_changed.emit(self.get_all_sessions())

    def request_open_session(self, item: SessionItem):
        """请求打开会话"""
        session = item.session
        session["name"] = item.text()
        self.requested.emit(session)

    def get_all_sessions(self) -> dict:
        """获取所有会话配置"""
        sessions = []
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            sessions.append(item.session)
        return {"session": sessions}

    def show_context_menu(self, pos: QPoint):
        # 获取点击位置对应的 Item
        item = self.list_widget.itemAt(pos)

        # 创建菜单对象
        menu = QMenu(self.list_widget)

        if item:
            # --- 如果点击在具体条目上的菜单项 ---
            edit_action = QAction("编辑会话", self.list_widget)
            edit_action.triggered.connect(lambda: self.edit_session(item))

            delete_action = QAction("删除会话", self)
            delete_action.triggered.connect(lambda: self.delete_session(item))

            connect_action = QAction("立即连接", self)
            connect_action.triggered.connect(lambda: self.request_open_session(item))
            # 设置为粗体，表示默认动作
            font = connect_action.font()
            font.setBold(True)
            connect_action.setFont(font)

            menu.addAction(connect_action)
            menu.addSeparator()  # 分割线
            menu.addAction(edit_action)
            menu.addAction(delete_action)
        else:
            # --- 如果点击在空白处的菜单项 ---
            add_action = QAction("新建会话", self)
            add_action.triggered.connect(self.new_session)
            menu.addAction(add_action)

        # 3. 在鼠标光标位置显示菜单
        # 注意要将相对坐标转换为屏幕全局坐标
        menu.exec(self.mapToGlobal(pos))

    def new_session(self):
        """新建会话"""
        dialog = SessionDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            config = dialog.get_session_config()
            item = SessionItem(config)
            self.list_widget.addItem(item)
            self.config_changed.emit(self.get_all_sessions())

    def edit_session(self, item: SessionItem):
        dialog = SessionDialog(item.session, parent=self)
        if dialog.exec() == QDialog.Accepted:
            config = dialog.get_session_config()
            item.session = config
            item.load_config(config)
            self.config_changed.emit(self.get_all_sessions())

    def delete_session(self, item: SessionItem):
        row = self.list_widget.row(item)
        self.list_widget.takeItem(row)
        self.config_changed.emit(self.get_all_sessions())


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
