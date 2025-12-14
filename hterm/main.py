from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

import qtawesome as qta

from quick import QuickBar
from session import Session
from session_list import SessionListWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowOpacity(0.95)
        self.resize(QGuiApplication.primaryScreen().size() * 0.7)
        self.menu_bar = self.menuBar()
        self.menu1 = QMenu('menu1')
        self.menu1.addAction('file')
        self.menu_bar.addMenu(self.menu1)
        self.menu_bar.addAction('set')
        self.statusBar().showMessage("准备就绪")

        self.setup()

    def setup(self):
        self.setup_toolbar()
        self.setup_quickbar()
        self.setup_list()

    def setup_toolbar(self):
        toolbar = QToolBar('工具栏')
        self.addToolBar(toolbar)
        toolbar.setMovable(False)
        # 设置按钮
        action = QAction('setting', self)
        action.setIcon(qta.icon('ri.settings-line'))
        # action.setIconText('设置')
        action.triggered.connect(lambda: print('open setting'))
        toolbar.addAction(action)

        # 风格按钮
        style_button = QToolButton(self)
        style_button.setIcon(qta.icon('ph.t-shirt'))
        style_menu = QMenu(self)
        for style in QStyleFactory.keys():
            style_menu.addAction(style, lambda s=style: app.setStyle(s))
        style_button.setMenu(style_menu)
        style_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        toolbar.addWidget(style_button)

        # 帮助按钮
        action = QAction(self)
        action.setIcon(qta.icon('mdi6.help-circle-outline'))
        action.triggered.connect(lambda: print('help'))
        toolbar.addAction(action)

    def setup_quickbar(self):
        self.quickbar = QuickBar()
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.quickbar)

    def setup_list(self):
        dock = SessionListWidget(self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

        local_config = {
            'type': 'local',
            'progname': 'zsh'
        }
        session = Session(local_config, parent=self)
        self.quickbar.command_ready.connect(session.terminal.input)
        self.setCentralWidget(session.terminal)


if __name__ == '__main__':
    app = QApplication()
    app.setStyle('Fusion')
    app.setApplicationName("hterm")
    window = MainWindow()
    window.show()
    app.exec()
