import os
import pathlib
import sys

import requests
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

if os.getenv("HTERM_VERSION"):
    HTERM_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
else:
    HTERM_DIR = pathlib.Path(__file__).resolve().parent.parent
LOGO_PATH = HTERM_DIR / "assets" / "icons" / "icon.png"


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("关于软件")
        self.setMinimumWidth(280)

        # 主布局
        layout = QVBoxLayout()

        # 1. 软件图标或标题
        pixmap = QPixmap(LOGO_PATH).scaled(
            60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        logo_label = QLabel(pixmap=pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        title_label = QLabel("Hterm")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label, 2)

        # 2. 作者和版权信息
        info_label = QLabel(
            f"版本: v{os.getenv('HTERM_VERSION')}\n构建日期: {os.getenv('HTERM_PACK_TIME')}"
        )
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        # 3. 按钮区域
        button_layout = QHBoxLayout()

        self.update_btn = QPushButton("检查更新")
        self.close_btn = QPushButton("关闭")

        self.update_btn.clicked.connect(self.check_updates)
        self.close_btn.clicked.connect(self.accept)  # 点击关闭对话框

        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def check_updates(self):
        """模拟检查更新功能"""
        self.update_btn.setEnabled(False)
        self.update_btn.setText("正在检查...")

        try:
            lastest_version = get_latest_version_no_api("lbhzy", "hterm-next")
            QMessageBox.information(self, "检查更新", f"当前最新版本{lastest_version}")
        except Exception as e:
            QMessageBox.critical(self, "出错", str(e))

        self.update_btn.setText("检查更新")
        self.update_btn.setEnabled(True)


def check_for_updates(owner, repo, current_version):
    """
    检查 GitHub 上的最新版本并与当前版本对比
    :param owner: GitHub 用户名或组织名
    :param repo: 仓库名
    :param current_version: 当前本地版本号 (例如 "v1.0.0")
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"

    try:
        response = requests.get(url, timeout=10)
        # 如果请求成功 (200)
        if response.status_code == 200:
            data = response.json()
            latest_version = data["tag_name"]  # 获取最新的 tag 名，如 "v1.2.0"
            download_url = data["html_url"]  # 获取发布页链接

            if latest_version != current_version:
                print(f"发现新版本: {latest_version} (当前: {current_version})")
                print(f"去下载: {download_url}")
                return True, latest_version
            else:
                print("当前已是最新版本。")
                return False, current_version
        else:
            print(f"请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"发生错误: {e}")

    return False, current_version


def get_latest_version_no_api(owner, repo):
    # 直接请求 HTML 页面
    url = f"https://github.com/{owner}/{repo}/releases/latest"
    response = requests.get(url, timeout=10)
    # 从跳转后的 URL 中提取版本号，例如 .../releases/tag/v1.6.1
    version = response.url.split("/")[-1]
    return version


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = AboutDialog()
    dialog.show()
    sys.exit(app.exec())
