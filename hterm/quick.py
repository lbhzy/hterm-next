from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

import toml
import qtawesome as qta

from profile import Profile


class QuickBar(QToolBar):
    def __init__(self):
        super().__init__('快捷栏')
        self.cfg = Profile('quick')
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
                self.addWidget(button)

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
    bar.show()
    app.exec()