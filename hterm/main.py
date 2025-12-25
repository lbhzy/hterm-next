import importlib.util

from PySide6.QtCore import (
    QLibraryInfo,
    QLocale,
    QTimer,
    QTranslator,
)
from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
)

from hterm.config import Config
from hterm.session import Session
from hterm.ui import MainWindow


def run_python_script_string(content):
    """运行 python 脚本字符串中的 main() 函数并返回值"""
    spec = importlib.util.spec_from_loader("script", loader=None)
    script = importlib.util.module_from_spec(spec)
    exec(content, script.__dict__)
    return script.main()


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
            self.quickbar.load_commands(quick_config)
        except Exception as e:
            QMessageBox.critical(self, "快捷命令加载出错", str(e))
        try:
            session_config = Config("session").load()
            self.session_list.load_sessions(session_config)
        except Exception as e:
            QMessageBox.critical(self, "快捷命令加载出错", str(e))

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


if __name__ == "__main__":
    app = QApplication()
    app.setStyle("Fusion")
    app.setApplicationName("hterm")
    # 设置中文
    translator = QTranslator(app)
    translator.load(
        QLocale("zh_CN"), "qt", "_", QLibraryInfo.path(QLibraryInfo.TranslationsPath)
    )
    app.installTranslator(translator)

    hterm = Hterm()
    hterm.show()
    app.exec()
