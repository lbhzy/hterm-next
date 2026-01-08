import qtawesome as qta
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QAction, QDesktopServices, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenu,
    QSizePolicy,
    QStyleFactory,
    QTabWidget,
    QToolBar,
    QToolButton,
    QWidget,
)

from hterm.config import Config
from hterm.ui.about_dialog import AboutDialog
from hterm.ui.quick_bar import QuickBar
from hterm.ui.session_list import SessionList


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowOpacity(0.95)
        self.resize(QGuiApplication.primaryScreen().size() * 0.7)

        self.setup_ui()

    def setup_ui(self):
        self.setup_menubar()
        self.setup_toolbar()
        self.setup_statusbar()
        # 快捷命令栏
        self.quickbar = QuickBar()
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.quickbar)

        # 会话列表
        self.session_list = SessionList(self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.session_list)

        # 会话区
        self.tabwidget = QTabWidget(self)
        self.tabwidget.setTabsClosable(True)
        self.tabwidget.setMovable(True)
        self.tabwidget.setDocumentMode(True)
        self.setCentralWidget(self.tabwidget)

    def setup_statusbar(self):
        self.terminal_label = QLabel()
        self.statusBar().addPermanentWidget(self.terminal_label)

    def setup_menubar(self):
        self.menu_bar = self.menuBar()
        self.menu1 = QMenu("menu1")
        self.menu1.addAction("file")
        self.menu_bar.addMenu(self.menu1)
        self.menu_bar.addAction("set")
        self.statusBar().showMessage("准备就绪")

    def setup_toolbar(self):
        toolbar = QToolBar("工具栏")
        self.addToolBar(toolbar)
        toolbar.setMovable(False)
        # 新建会话按钮
        self.new_session_action = QAction("新建会话", self)
        self.new_session_action.setIcon(qta.icon("ri.folder-add-line"))
        toolbar.addAction(self.new_session_action)

        # 设置按钮
        action = QAction("setting", self)
        action.setIcon(qta.icon("ri.settings-line"))
        # action.setIconText('设置')
        action.triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(Config.get_dir()))
        )
        toolbar.addAction(action)

        # 风格按钮
        style_button = QToolButton(self)
        style_button.setIcon(qta.icon("ph.t-shirt"))
        style_menu = QMenu(self)
        for style in QStyleFactory.keys():
            style_menu.addAction(
                style, lambda s=style: QApplication.instance().setStyle(s)
            )
        style_button.setMenu(style_menu)
        style_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        toolbar.addWidget(style_button)

        # 关于按钮
        action = QAction(self)
        action.setIcon(qta.icon("mdi6.help-circle-outline"))
        action.triggered.connect(lambda: AboutDialog(self).show())
        toolbar.addAction(action)

        spacer = QWidget()
        # 设置水平方向为 Expanding（扩张），垂直方向为 Preferred
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # 将占位组件加入 Toolbar
        toolbar.addWidget(spacer)

        action = QAction(self)
        action.setIcon(qta.icon("msc.layout-sidebar-left"))
        action.triggered.connect(lambda: print("help"))
        toolbar.addAction(action)

        action = QAction(self)
        action.setIcon(qta.icon("msc.layout-panel"))
        action.triggered.connect(lambda: print("help"))
        toolbar.addAction(action)


if __name__ == "__main__":
    app = QApplication()
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    app.exec()
