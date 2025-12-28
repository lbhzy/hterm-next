import qtawesome as qta
from PySide6.QtCore import QSize, Qt, Signal, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QDialog, QPushButton, QToolBar

from hterm.types import QuickConfig
from hterm.ui.quick_dialog import QuickDialog


class QuickBar(QToolBar):
    """快捷命令栏"""

    command_ready = Signal(dict)
    config_changed = Signal(QuickConfig)

    def __init__(self, parent=None):
        super().__init__("快捷命令栏", parent)

        self.config = {}

        self.setup_ui()

    def setup_ui(self):
        self.setMovable(False)
        self.setIconSize(QSize(18, 18))
        self.mgr = QAction(self)
        self.mgr.setIcon(qta.icon("mdi.speedometer"))
        self.mgr.triggered.connect(self.open_dialog)

    def load_config(self, config: QuickConfig):
        """根据配置生成快捷命令按钮"""
        self.clear()
        self.addAction(self.mgr)

        self.config = config
        cmds = self.config.get("command", [])
        for cmd in cmds:
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
            button.setProperty("data", cmd)
            button.clicked.connect(self.on_button_clicked)
            self.addWidget(button)

    @Slot()
    def on_button_clicked(self):
        button = self.sender()
        self.command_ready.emit(button.property("data"))

    @Slot()
    def open_dialog(self):
        dialog = QuickDialog(self.config, self)
        ret = dialog.exec()
        if ret == QDialog.Accepted:
            self.config = dialog.export_config()
            self.load_config(self.config)
            self.config_changed.emit(self.config)


if __name__ == "__main__":
    app = QApplication()
    config = {
        "command": [
            {"name": "命令1", "type": "text", "content": "echo hterm\n"},
            {"name": "命令2", "type": "script", "content": "echo hterm\n"},
            {"name": "命令3", "type": "text", "content": "echo hterm\n"},
        ]
    }
    bar = QuickBar()
    bar.load_config(config)
    bar.command_ready.connect(lambda s: print(f"command: {s}"))
    bar.show()
    app.exec()
