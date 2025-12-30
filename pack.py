import os
import pathlib
import shutil
import subprocess
import sys

from PyInstaller.__main__ import run

ROOT_DIR = pathlib.Path(__file__).resolve().parent
ASSETS_DIR = ROOT_DIR / "hterm" / "assets"


def get_version_tag():
    tag = os.getenv("GITHUB_REF_NAME")
    return tag


def pack():
    params = [
        "hterm/main.py",  # 打包目标
        "-y",  # 不询问，直接替换旧成果物
        "-w",  # 不显示控制台
        "--specpath=build",  # 不需要 spec 文件，所以将其生成到 build 下
        f"--add-data={ASSETS_DIR}:assets",  # 包含资源文件
        "--name=hterm",  # 设置软件名
    ]
    if sys.platform == "win32":
        params.append("--collect-data=winpty")
        # Windows 图标规格 256x256 透明背景
        params.append(f"-i={ASSETS_DIR / 'icons' / 'icon.png'}")
    elif sys.platform == "darwin":
        # macOS 图标规格 1024x1024 纯白背景
        params.append(f"-i={ROOT_DIR / 'assets' / 'icons' / 'icon-mac.png'}")

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


if __name__ == "__main__":
    pack()
    compress()
