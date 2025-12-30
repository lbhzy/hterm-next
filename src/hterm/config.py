import pathlib
import tomllib

import tomli_w
from PySide6.QtCore import QCoreApplication, QStandardPaths

CONFIG_DIR_NAME = "profiles"
CONFIG_SUFFIX = ".toml"
QCoreApplication.setOrganizationName("lbhzy")
QCoreApplication.setApplicationName("hterm")


class Config:
    """配置文件管理"""

    def __init__(self, name: str):
        # 程序目录
        base_dir = pathlib.Path(self.get_dir())

        # 配置文件目录
        config_dir = base_dir / CONFIG_DIR_NAME
        config_dir.mkdir(parents=True, exist_ok=True)

        # 配置文件路径
        self.file_path = config_dir / f"{name}{CONFIG_SUFFIX}"

        # 确保文件存在
        self.file_path.touch(exist_ok=True)

    def load(self):
        with self.file_path.open("rb") as f:
            return tomllib.load(f)

    def dump(self, data):
        with self.file_path.open("wb") as f:
            tomli_w.dump(data, f, multiline_strings=True)

    @staticmethod
    def get_dir():
        return QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)


if __name__ == "__main__":
    cfg = Config("test")
    data = {
        "project": {
            "name": "hterm",
            "version": "v0.1.1",
        },
        "other": {
            "number": 10.2,
            "bool": True,
            "list": ["apple", "banana"],
            "dict": {"key1": 1, "key2": 2},
            "str": "hello\nworld",
        },
    }
    cfg.dump(data)
    print(cfg.load())
