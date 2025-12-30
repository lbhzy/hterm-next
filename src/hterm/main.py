import pathlib
import sys

from PySide6.QtCore import (
    QLibraryInfo,
    QLocale,
    QTimer,
    QTranslator,
)
from PySide6.QtGui import QFontDatabase, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
)

from hterm.config import Config
from hterm.session import Session
from hterm.ui import MainWindow
from hterm.utils import run_python_script_string


class Hterm(MainWindow):
    def __init__(self):
        super().__init__()

        self.session_list.requested.connect(self.open_session)
        self.tabwidget.tabCloseRequested.connect(self.close_session)
        self.quickbar.command_ready.connect(self.send_quick_command)

        load_timer = QTimer(self)
        load_timer.setSingleShot(True)
        load_timer.timeout.connect(self.load)
        load_timer.start(0)

    def load(self):
        try:
            quick_config = Config("quick").load()
            self.quickbar.load_config(quick_config)
            self.quickbar.config_changed.connect(lambda c: Config("quick").dump(c))
        except Exception as e:
            QMessageBox.critical(self, "快捷命令加载出错", str(e))
        try:
            session_config = Config("session").load()
            self.session_list.load_sessions(session_config)
        except Exception as e:
            QMessageBox.critical(self, "会话加载出错", str(e))

    def open_session(self, config):
        session = Session(config)
        session.terminal.session = session
        self.tabwidget.addTab(session.terminal, config["name"])
        self.tabwidget.setCurrentIndex(self.tabwidget.indexOf(session.terminal))
        session.terminal.setFocus()

    def close_session(self, index):
        terminal = self.tabwidget.widget(index)
        session = terminal.session
        self.tabwidget.removeTab(index)
        terminal.session.channel.close()
        del session
        terminal.deleteLater()

    def send_quick_command(self, config):
        terminal = self.tabwidget.currentWidget()
        if not terminal:
            return

        if config["type"] == "text":
            terminal.input(config["content"])
        else:
            try:
                ret = run_python_script_string(config["content"])
                if isinstance(ret, str):
                    terminal.input(ret)
            except Exception as e:
                QMessageBox.critical(self, "执行脚本出错", str(e))


def main():
    app = QApplication()
    assets_dir = pathlib.Path(__file__).resolve().parent / "assets"

    # 设置图标
    icon_path = assets_dir / "icons" / "icon.png"
    if sys.platform != "darwin":
        app.setWindowIcon(QIcon(str(icon_path)))

    # 设置中文
    translator = QTranslator(app)
    translator.load(
        QLocale.Language.Chinese,
        "qtbase",
        "_",
        QLibraryInfo.path(QLibraryInfo.TranslationsPath),
    )
    app.installTranslator(translator)

    # 加载字体
    font_dir = assets_dir / "fonts"
    for entry in font_dir.iterdir():
        QFontDatabase.addApplicationFont(str(entry))

    hterm = Hterm()
    hterm.show()
    app.exec()


if __name__ == "__main__":
    main()
