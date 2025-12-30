import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from hterm.utils import run_python_script_string


class QuickDialog(QDialog):
    """快捷命令管理窗口"""

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)

        self.commands = config.get("command", [])

        self.setup_ui()
        self.connect_signals()
        self.init_list_items()

    def setup_ui(self):
        self.setWindowTitle("快捷命令管理")
        screen_size = QGuiApplication.primaryScreen().size()
        self.resize(screen_size * 0.5)

        # 主布局：垂直排列 (上方内容区 + 底部按钮区)
        main_layout = QVBoxLayout(self)

        # ---------------- 上方内容区 ----------------
        content_layout = QHBoxLayout()

        # --- 左侧部分 ---
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(1)
        self.list_widget.setMaximumWidth(160)
        self.list_widget.setDragDropMode(QListWidget.InternalMove)  # 内部移动模式

        # 增删按钮，浮动在列表右下角
        floating_layout = QVBoxLayout(self.list_widget)  # 布局设在 list_widget 上
        floating_layout.setAlignment(Qt.AlignRight | Qt.AlignBottom)  # 对齐到右下角
        floating_layout.setContentsMargins(0, 0, 15, 10)  # 距离边缘的间距

        self.btn_add = QPushButton(self.list_widget)
        self.btn_add.setIcon(qta.icon("ri.add-line", color="green"))
        self.btn_add.setFixedWidth(25)

        self.btn_remove = QPushButton(self.list_widget)
        self.btn_remove.setIcon(qta.icon("ri.subtract-line", color="red"))
        self.btn_remove.setFixedWidth(25)
        floating_layout.addWidget(self.btn_add)
        floating_layout.addWidget(self.btn_remove)

        # --- 右侧部分 ---
        right_layout = QFormLayout()
        right_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.label_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["文本", "Python脚本"])
        self.text_edit = QPlainTextEdit()
        right_layout.addRow("标签：", self.label_edit)
        right_layout.addRow("类型：", self.type_combo)
        right_layout.addRow("内容：", self.text_edit)
        overlay_layout = QVBoxLayout(self.text_edit)
        overlay_layout.setContentsMargins(0, 0, 20, 10)  # 设置右下边距
        overlay_layout.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.run_btn = QPushButton(self.text_edit)
        self.run_btn.setText("测试输出")
        self.run_btn.setIcon(qta.icon("fa6s.play", color="green"))
        self.run_btn.clicked.connect(self.run_script_test)
        overlay_layout.addWidget(self.run_btn)

        # 将左右加入内容区
        content_layout.addWidget(self.list_widget)
        content_layout.addLayout(right_layout, 2)

        # ---------------- 底部操作按钮 ----------------
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        main_layout.addLayout(content_layout)
        main_layout.addWidget(buttons)

    def connect_signals(self):
        """绑定信号与槽"""
        # 当左侧列表选中项变化时
        self.list_widget.currentItemChanged.connect(self.on_item_changed)

        # 当右侧输入框内容变化时，实时同步回列表项
        self.text_edit.textChanged.connect(self.update_list_item)
        self.label_edit.textChanged.connect(self.update_list_item)
        self.type_combo.currentTextChanged.connect(self.update_list_item)

        # 增删命令
        self.btn_add.clicked.connect(self.add_cmd)
        self.btn_remove.clicked.connect(self.remove_cmd)

    def init_list_items(self):
        if not self.commands:
            self.clear_and_disable_right()
            return
        self.enable_right()
        for cmd in self.commands:
            item = QListWidgetItem(cmd["name"])
            item.setData(Qt.UserRole, cmd)
            self.list_widget.addItem(item)
            self.list_widget.setCurrentItem(item)

    def clear_and_disable_right(self):
        """清空右侧编辑区并禁用"""
        self.label_edit.clear()
        self.type_combo.setCurrentIndex(-1)
        self.text_edit.clear()
        self.label_edit.setDisabled(True)
        self.type_combo.setDisabled(True)
        self.text_edit.setDisabled(True)

    def enable_right(self):
        """启用右侧编辑区"""
        self.label_edit.setEnabled(True)
        self.type_combo.setEnabled(True)
        self.text_edit.setEnabled(True)

    def on_item_changed(self, item: QListWidgetItem):
        if item is None:
            # 没有项时，清空右侧编辑区并禁用
            self.clear_and_disable_right()
            return

        self.enable_right()

        # 获取当前选中的数据
        cmd = item.data(Qt.UserRole)

        self.label_edit.setText(cmd["name"])
        self.type_combo.setCurrentIndex(0 if cmd["type"] == "text" else 1)
        self.text_edit.setPlainText(cmd["content"])

    def update_list_item(self):
        """将右侧编辑器的内容实时更新到列表项"""
        item = self.list_widget.currentItem()
        if item is None:
            return
        cmd = item.data(Qt.UserRole)

        name = self.label_edit.text()
        cmd["name"] = name
        cmd["type"] = "text" if self.type_combo.currentIndex() == 0 else "script"
        cmd["content"] = self.text_edit.toPlainText()

        item.setText(name)
        item.setData(Qt.UserRole, cmd)

    def add_cmd(self):
        cmd = {"name": "未命名", "type": "text", "content": ""}
        item = QListWidgetItem(cmd["name"])
        item.setData(Qt.UserRole, cmd)
        self.list_widget.addItem(item)
        self.list_widget.setCurrentItem(item)
        self.label_edit.setFocus()
        self.label_edit.selectAll()

    def remove_cmd(self):
        row = self.list_widget.currentRow()
        self.list_widget.takeItem(row)

    def run_script_test(self):
        """运行测试输出"""
        content = self.text_edit.toPlainText()
        if self.type_combo.currentIndex() == 1:
            try:
                content = run_python_script_string(content)
            except Exception as e:
                QMessageBox.critical(self, "脚本运行出错", str(e))
                return

        if not isinstance(content, str):
            QMessageBox.critical(
                self,
                "输出类型错误",
                f"输出类型错误：{type(content).__name__}，应为 str 类型",
            )

        if content:
            QMessageBox.information(
                self,
                "输出内容",
                f"输出字符串: {content}\n\n字节流格式: {content.encode()}",
            )

    def export_config(self) -> dict:
        """导出当前配置"""
        commands = []

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            cmd = item.data(Qt.UserRole)
            commands.append(cmd)
        return {"command": commands}


if __name__ == "__main__":
    app = QApplication()
    # app.setStyle("Fusion")
    config = {
        "command": [
            {"name": "命令1", "type": "text", "content": "echo hterm\n"},
            {"name": "命令2", "type": "script", "content": "echo 123\n"},
            {"name": "命令3", "type": "text", "content": "echo abc\n"},
        ]
    }
    print("before:", config)
    dialog = QuickDialog(config)
    dialog.accepted.connect(lambda: print("after:", dialog.export_config()))
    dialog.show()
    app.exec()
