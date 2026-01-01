import qtawesome as qta
import serial.tools.list_ports
from PySide6.QtGui import QAction, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class SessionDialog(QDialog):
    """会话创建窗口"""

    def __init__(self, config: dict = None, parent=None):
        super().__init__(parent)

        self.setup_ui()
        if config:
            self.load_config(config)

    def load_config(self, config: dict):
        """加载已有的会话配置"""
        session_type = config.get("type", "ssh").lower()
        index = {"ssh": 0, "serial": 1, "local": 2}.get(session_type, 0)
        self.tabs.setCurrentIndex(index)

        if session_type == "ssh":
            self.ssh_host.setText(config.get("server", ""))
            self.ssh_port.setValue(config.get("port", 22))
            self.ssh_user.setText(config.get("username", ""))
            self.ssh_password.setText(config.get("password", ""))
        elif session_type == "serial":
            self.serial_port.setCurrentText(config.get("port", ""))
            self.serial_baud.setCurrentText(str(config.get("baudrate", "115200")))
        elif session_type == "local":
            self.local_shell.setText(config.get("progname", ""))

        self.session_name.setText(config.get("name", ""))

    def setup_ui(self):
        self.setWindowTitle("创建新会话")
        screen_size = QGuiApplication.primaryScreen().size()
        self.resize(screen_size * 0.5)
        # 主布局
        self.main_layout = QVBoxLayout(self)

        self.common_group = QGroupBox("通用设置")
        self.common_layout = QFormLayout(self.common_group)

        self.session_name = QLineEdit()
        self.session_name.setPlaceholderText("可省略")

        self.term_checkbox = QCheckBox("自定义终端配置")

        self.common_layout.addRow("会话别名:", self.session_name)
        self.common_layout.addRow("", self.term_checkbox)

        # 创建选项卡
        self.tabs = QTabWidget()

        # 初始化各个页面
        self.ssh_tab = self._create_ssh_tab()
        self.serial_tab = self._create_serial_tab()
        self.local_tab = self._create_local_tab()

        self.tabs.addTab(self.ssh_tab, "SSH")
        self.tabs.addTab(self.serial_tab, "Serial")
        self.tabs.addTab(self.local_tab, "Local")

        # 底部按钮 (确定/取消)
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.term_group = self._create_terminal_group()
        self.term_group.setVisible(False)

        self.main_layout.addWidget(self.common_group)
        self.main_layout.addWidget(self.term_group)
        self.main_layout.addWidget(self.tabs)
        self.main_layout.addWidget(self.button_box)

        self.term_checkbox.stateChanged.connect(
            lambda state: self.term_group.setVisible(state)
        )

    def _create_terminal_group(self):
        group = QGroupBox("终端设置")
        layout = QFormLayout(group)

        self.term_type_combo = QComboBox()
        self.term_type_combo.addItems(["xterm-256color", "vt100", "linux", "screen"])

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 48)
        self.font_size_spin.setValue(12)

        layout.addRow("终端类型:", self.term_type_combo)
        layout.addRow("字体大小:", self.font_size_spin)
        return group

    def _create_ssh_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)

        self.ssh_host = QLineEdit()
        self.ssh_port = QSpinBox()
        self.ssh_port.setRange(1, 65535)
        self.ssh_port.setValue(22)
        self.ssh_user = QLineEdit()
        self.ssh_password = QLineEdit()
        self.ssh_password.setEchoMode(QLineEdit.Password)

        self.toggle_pwd_action = QAction(self)
        self.toggle_pwd_action.setIcon(qta.icon("ei.eye-open"))
        self.ssh_password.addAction(self.toggle_pwd_action, QLineEdit.TrailingPosition)
        self.toggle_pwd_action.triggered.connect(self._toggle_password_visibility)

        layout.addRow("主机地址:", self.ssh_host)
        layout.addRow("端口:", self.ssh_port)
        layout.addRow("用户名:", self.ssh_user)
        layout.addRow("密码:", self.ssh_password)
        return widget

    def _create_serial_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)

        self.serial_port = QComboBox()
        self.serial_port.setEditable(True)
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.serial_port.addItems(ports)
        self.serial_baud = QComboBox()
        self.serial_baud.setEditable(True)
        self.serial_baud.addItems(["9600", "115200", "57600"])
        self.serial_baud.setCurrentText("115200")

        layout.addRow("串口号:", self.serial_port)
        layout.addRow("波特率:", self.serial_baud)
        return widget

    def _create_local_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)

        self.local_shell = QLineEdit()

        layout.addRow("程序名:", self.local_shell)
        return widget

    def _toggle_password_visibility(self):
        """切换密码可见性状态"""
        if self.ssh_password.echoMode() == QLineEdit.Password:
            # 切换为明文
            self.ssh_password.setEchoMode(QLineEdit.Normal)
            self.toggle_pwd_action.setIcon(qta.icon("ei.eye-close"))
        else:
            # 切换为密文
            self.ssh_password.setEchoMode(QLineEdit.Password)
            self.toggle_pwd_action.setIcon(qta.icon("ei.eye-open"))

    def get_session_config(self):
        """获取当前选择的会话配置"""
        current_index = self.tabs.currentIndex()
        tab_text = self.tabs.tabText(current_index)

        config = {}
        config["name"] = self.session_name.text()
        config["type"] = tab_text.lower()

        if config["type"] == "ssh":
            config["server"] = self.ssh_host.text()
            config["port"] = self.ssh_port.value()
            config["username"] = self.ssh_user.text()
            config["password"] = self.ssh_password.text()
        elif config["type"] == "serial":
            config["port"] = self.serial_port.currentText()
            config["baudrate"] = int(self.serial_baud.currentText())
        elif config["type"] == "local":
            config["progname"] = self.local_shell.text()

        return config


if __name__ == "__main__":
    app = QApplication()
    # app.setStyle("Fusion")
    dialog = SessionDialog()
    dialog.accepted.connect(lambda: print(dialog.get_session_config()))
    dialog.show()
    app.exec()
