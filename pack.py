import os
import pathlib
import shutil
import subprocess
import sys
import tomllib
from datetime import datetime, timedelta, timezone

import tomli_w
from PyInstaller.__main__ import run

ROOT_DIR = pathlib.Path(__file__).resolve().parent

TARGET = ROOT_DIR / "src" / "hterm" / "main.py"

ASSETS_DIR = ROOT_DIR / "src" / "hterm" / "assets"

WIN_ICON = ROOT_DIR / "assets" / "icons" / "icon-win.png"
MAC_ICON = ROOT_DIR / "assets" / "icons" / "icon-mac.png"

HOOK_ENV_PATH = ROOT_DIR / "build" / "hook_env.toml"
HOOK_SCRIPT_PATH = ROOT_DIR / "scripts" / "hook.py"


def get_version_tag():
    tag = os.getenv("GITHUB_REF_NAME")
    return tag


def pack():
    params = [
        f"{TARGET}",  # 打包目标
        "-y",  # 不询问，直接替换旧成果物
        "-w",  # 不显示控制台
        "--specpath=build",  # 不需要 spec 文件，所以将其生成到 build 下
        f"--add-data={ASSETS_DIR}:assets",  # 包含资源文件
        f"--add-data={HOOK_ENV_PATH}:.",  # 包含 hook 的环境变量
        f"--runtime-hook={HOOK_SCRIPT_PATH}",  # 设置程序运行前 hook 的脚本
        "--name=hterm",  # 设置软件名
    ]
    if sys.platform == "win32":
        params.append("--collect-data=winpty")
        # Windows 图标规格 256x256 透明背景
        params.append(f"-i={WIN_ICON}")
    elif sys.platform == "darwin":
        # macOS 图标规格 1024x1024 纯白背景
        params.append(f"-i={MAC_ICON}")

    run(params)


def compress():
    tag = get_version_tag()
    if not tag:
        return
    match sys.platform:
        case "win32":
            shutil.make_archive(
                f"dist/hterm-{tag}-windows-x86_64", "zip", "dist", "hterm"
            )
        case "linux":
            shutil.make_archive(
                f"dist/hterm-{tag}-linux-x86_64", "gztar", "dist", "hterm"
            )
        case "darwin":
            cmd = ["zip", "-ry", f"hterm-{tag}-macos-arm64.zip", "hterm.app"]
            subprocess.run(cmd, cwd="dist", check=True)
        case _:
            raise RuntimeError(f"Unsupported platform: {sys.platform}")


def generate_hook_env():
    pyproject_path = ROOT_DIR / "pyproject.toml"

    with pyproject_path.open("rb") as f:
        config = tomllib.load(f)

    pack_datetime = datetime.now(timezone(timedelta(hours=8)))
    hook_env = {
        "env": {
            "version": config["project"]["version"],
            "pack_time": pack_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        }
    }

    HOOK_ENV_PATH.touch(exist_ok=True)
    with HOOK_ENV_PATH.open("wb") as f:
        tomli_w.dump(hook_env, f)


if __name__ == "__main__":
    generate_hook_env()
    pack()
    compress()
