import qtawesome as qta
from PySide6.QtCore import QSize, Qt, Signal, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QPushButton, QToolBar

from hterm.ui.quick_dialog import QuickDialog


class QuickBar(QToolBar):
    """快捷命令栏"""

    command_ready = Signal(dict)

    def __init__(self):
        super().__init__("快捷命令栏")
        self.setMovable(False)
        self.setup_ui()

    def setup_ui(self):
        self.setIconSize(QSize(18, 18))
        action = QAction(self)
        action.setIcon(qta.icon("mdi.speedometer"))
        action.triggered.connect(self.open_dialog)
        self.addAction(action)

    def load_commands(self, config):
        """载入快捷命令配置，生成快捷命令按钮"""
        if not config:
            return
        for action in self.actions():
            widget = self.widgetForAction(action)
            if isinstance(widget, QPushButton):
                self.removeAction(action)

        for cmd in config["command"]:
            button = QPushButton(cmd["name"])
            button.setFocusPolicy(Qt.NoFocus)
            metrics = button.fontMetrics()
            text_width = metrics.horizontalAdvance(button.text())
            button.setFixedWidth(text_width + 16 + 20)
            if cmd["type"] == "text":
                button.setIcon(qta.icon("ph.text-t-bold", color="green"))
            elif cmd["type"] == "script":
                button.setIcon(qta.icon("ph.code-bold", color="blue"))
            button.setToolTip(cmd["content"])
            button.cmd = cmd
            button.clicked.connect(self.on_button_clicked)
            self.addWidget(button)

    @Slot()
    def on_button_clicked(self):
        button = self.sender()
        self.command_ready.emit(button.cmd)

    @Slot()
    def open_dialog(self):
        dialog = QuickDialog(self)
        dialog.exec()


if __name__ == "__main__":
    app = QApplication()
    bar = QuickBar()
    bar.command_ready.connect(lambda s: print(f"command: {s}"))
    config = {
        "command": [
            {"name": "命令1", "type": "text", "content": "echo hterm\n"},
            {"name": "命令2", "type": "script", "content": "echo hterm\n"},
            {"name": "命令3", "type": "text", "content": "echo hterm\n"},
        ]
    }
    bar.load_commands(config)
    bar.load_commands(config)
    bar.show()
    app.exec()
