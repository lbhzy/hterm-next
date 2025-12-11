from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

import qtawesome as qta

from config import Config


class QuickBar(QToolBar):
    command_ready = Signal(str)
    
    def __init__(self):
        super().__init__('快捷命令栏')
        self.cfg = Config('quick')
        self.setup()

    def setup(self):
        self.setStyleSheet("""
            QToolBar {
                padding: 0px;
            }
        """)
        self.setIconSize(QSize(20, 20))
        manager = QAction(self)
        manager.setIcon(qta.icon('mdi.speedometer-slow'))
        manager.triggered.connect(self.open_dialog)
        self.addAction(manager)
        
        data = self.cfg.load()
        if 'quick' in data:
            for item in data['quick']:
                button = QPushButton(item['name'], self)
                button.setIcon(qta.icon('mdi.script-text-outline'))
                button.setToolTip(str(item))
                button.kind = item['kind']
                button.content = item['content']
                button.clicked.connect(self.on_button_clicked)
                self.addWidget(button)

    @Slot()
    def on_button_clicked(self):
        button = self.sender()
        self.command_ready.emit(button.content)

    @Slot()
    def open_dialog(self):
        dialog = QuickDialog(self) 
        dialog.exec()

class QuickDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(QGuiApplication.primaryScreen().size() * 0.5)

    def setup(self):
        layout = QHBoxLayout(self)


if __name__ == '__main__':
    app = QApplication()
    # app.setStyle('Fusion')
    bar = QuickBar()
    bar.command_ready.connect(lambda s: print(f'command: {s}'))
    bar.show()
    app.exec()