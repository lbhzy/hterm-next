from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from hterm.ui import MainWindow
from hterm.config import Config


class Hterm(MainWindow):
    def __init__(self):
        super().__init__()
        load_timer = QTimer(self)
        load_timer.setSingleShot(True)
        load_timer.timeout.connect(self.load)
        load_timer.start(0)

    def load(self):
        try:
            quick_config = Config('quick').load()
            self.quickbar.load_commands(quick_config)
        except Exception as e:
            QMessageBox.critical(self, "快捷命令加载出错", str(e))
        try:
            session_config = Config('session').load()
            self.session_list.load_sessions(session_config)
        except Exception as e:
            QMessageBox.critical(self, "快捷命令加载出错", str(e))


if __name__ == '__main__':
    app = QApplication()
    app.setStyle('Fusion')
    app.setApplicationName("hterm")
    # 设置中文
    translator = QTranslator(app)
    translator.load(
        QLocale("zh_CN"),
        "qt",
        "_",
        QLibraryInfo.path(QLibraryInfo.TranslationsPath)
    )
    app.installTranslator(translator)

    hterm = Hterm()
    hterm.show()
    app.exec()