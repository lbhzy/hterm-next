from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

import qtawesome as qta


class QuickDialog(QDialog):
    """ 快捷命令管理窗口 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('快捷命令管理')
        self.resize(QGuiApplication.primaryScreen().size() * 0.5)
        
        self.setup_ui()

    def setup_ui(self):
        # 主布局：垂直排列 (上方内容区 + 底部按钮区)
        main_layout = QVBoxLayout(self)

        # ---------------- 上方内容区 ----------------
        content_layout = QHBoxLayout()

        # --- 左侧部分 ---
        left_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(1)
        self.list_widget.setMaximumWidth(160)
        
        # 工具区
        tool_layout = QHBoxLayout()
        btn_add = QToolButton()
        btn_add.setIcon(qta.icon('ri.add-line'))
        btn_remove = QToolButton()
        btn_remove.setIcon(qta.icon('ri.subtract-line'))
        btn_up = QToolButton()
        btn_up.setIcon(qta.icon('fa5s.angle-up'))
        btn_down = QToolButton()
        btn_down.setIcon(qta.icon('fa6s.angle-down'))
        tool_layout.addWidget(btn_add)
        tool_layout.addWidget(btn_remove)
        tool_layout.addWidget(btn_up)
        tool_layout.addWidget(btn_down)

        left_layout.addWidget(self.list_widget)
        left_layout.addLayout(tool_layout)

        # --- 右侧部分 ---
        right_layout = QFormLayout()
        right_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.label_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.text_edit = QPlainTextEdit()
        right_layout.addRow("标签：", self.label_edit)
        right_layout.addRow("类型：", self.type_combo)
        right_layout.addRow("内容：", self.text_edit)
        run_btn = QPushButton('测试输出')
        right_layout.addWidget(run_btn)

        # 将左右加入内容区
        content_layout.addLayout(left_layout)
        content_layout.addLayout(right_layout, 2)

        # ---------------- 底部操作按钮 ----------------
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        main_layout.addLayout(content_layout)
        main_layout.addWidget(buttons)
        
        
if __name__ == '__main__':
    app = QApplication()
    # app.setStyle('Fusion')
    dialog = QuickDialog()
    dialog.show()
    app.exec()