from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

from hterm.channel import LocalChannel, SerialChannel, SshChannel
from hterm.terminal import Terminal


def create_channel(config: dict):
    """
    根据配置字典创建并返回相应的 Channel 实例。
    """
    channel_type = config.get("type")

    if channel_type == "local":
        progname = config.get("progname")
        return LocalChannel(progname)

    elif channel_type == "serial":
        port = config.get("port")
        baudrate = config.get("baudrate")
        if not port:
            raise ValueError("Serial configuration requires a 'port'.")
        return SerialChannel(port, baudrate)

    elif channel_type == "ssh":
        return SshChannel(
            config.get("server"),
            config.get("port"),
            config.get("username"),
            config.get("password"),
        )

    else:
        raise ValueError(f"Unknown channel type: {channel_type}")


class Session(QWidget):
    resized = Signal(int, int)

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.terminal = Terminal(self)
        self.main_layout.addWidget(self.terminal)
        try:
            self.channel = create_channel(config)
            self.channel.setParent(self)
        except ValueError as e:
            self.terminal.feed(f"Error creating channel: {e}")
            raise

        self.terminal.input_ready.connect(self.channel.send_data)
        self.terminal.resized.connect(self.channel.send_window_size)
        self.terminal.resized.connect(lambda cols, rows: self.resized.emit(cols, rows))
        self.channel.received.connect(self.terminal.feed)
        # self.channel.connected.connect(lambda s: self.terminal.feed(s))
        self.channel.disconnected.connect(lambda s: self.terminal.feed(f"\r\n{s}\r\n"))

        self.channel.open()


if __name__ == "__main__":
    app = QApplication()

    local_config = {"type": "local", "progname": "zsh"}

    serial_config = {
        "type": "serial",
        "port": "/dev/cu.debug-console",
        "baudrate": 115200,
    }

    ssh_config = {
        "type": "ssh",
        "server": "10.10.10.1",
        "port": 22,
        "username": "root",
        "password": "password",
    }

    session = Session(local_config)
    session.resize(960, 540)
    session.show()
    app.exec()
