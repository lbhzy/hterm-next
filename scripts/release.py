import subprocess


def run_command(command):
    """执行 shell 命令并处理错误"""
    result = subprocess.run(
        command, check=True, capture_output=True, text=True, shell=True
    )
    return result.stdout.strip()


def check_stage_clean():
    # 检查 git 暂存区是否干净
    ret = run_command("git diff --cached")
    if ret:
        return False

    # 检查 pyproject.toml 和 uv.lock 是否有未提交的更改
    ret = run_command("git diff pyproject.toml uv.lock")
    if ret:
        return False
    return True


def main():
    if not check_stage_clean():
        print("❌ 请确保没有未提交的更改")
        return

    # 更新项目版本
    current_version = run_command("uv version --short")
    run_command("uv version --bump patch")
    new_version = run_command("uv version --short")
    print(f"🚀 版本更新: {current_version} -> {new_version}")

    # 提交更改并创建 Git 标签
    tag_name = f"v{new_version}"
    commit_msg = f"发布 {tag_name}"

    print(f"📦 提交 pyproject.toml 和 uv.lock 并打标签 {tag_name}")

    run_command("git add pyproject.toml uv.lock")
    run_command(f'git commit -m "{commit_msg}"')
    run_command(f'git tag -a {tag_name} -m "{commit_msg}"')

    print("📤 上传远程仓库")
    run_command("git push origin main")
    run_command("git push origin --tags")

    print(f"✅ 成功发布 {tag_name}!")


if __name__ == "__main__":
    main()
