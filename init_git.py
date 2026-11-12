import os
import re
import subprocess
import sys
from pathlib import Path

# 🌟 在这里配置你的 GitHub 用户名
GITHUB_USER = "eagleye-china"


def run(cmd, ignore_error=False):
    print(f"👉 正在执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        if not ignore_error:
            print(f"❌ 错误: {result.stderr}")
            # 如果出错，不直接退出，而是抛出异常让上层决定
            raise RuntimeError(result.stderr)
    if result.stdout.strip():
        print(result.stdout.strip())
    return result


def get_project_info():
    """智能读取当前项目信息"""
    current_dir = Path.cwd()
    repo_name = current_dir.name
    project_name = repo_name
    version = "0.1.0"

    toml_path = current_dir / "pyproject.toml"
    if toml_path.exists():
        with open(toml_path, "r", encoding="utf-8") as f:
            content = f.read()
            name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            if name_match: project_name = name_match.group(1)
            version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if version_match: version = version_match.group(1)

    return repo_name, project_name, version


def main():
    repo_name, project_name, version = get_project_info()
    remote_url = f"git@github.com:{GITHUB_USER}/{repo_name}.git"
    tag_name = f"v{version}"

    print(f"🚀 开始自动初始化并发布【{project_name}】 (v{version})...")

    # ================= 1. 本地 Git 初始化 =================
    if not os.path.exists(".git"):
        run(["git", "init"])
        run(["git", "branch", "-M", "main"])
        run(["git", "config", "core.autocrlf", "false"])
        run(["git", "add", "."])
        run(["git", "commit", "-m", f"feat: initial release of {project_name} v{version}"])
        print("✅ 本地 Git 初始化完成！")
    else:
        print("✅ 已检测到 Git 仓库，跳过初始化。")

    # ================= 2. 自动配置远程仓库 =================
    try:
        # 检查是否已有 origin
        remotes = subprocess.run(["git", "remote"], capture_output=True, text=True).stdout
        if "origin" not in remotes:
            run(["git", "remote", "add", "origin", remote_url])
            print(f"✅ 已关联远程仓库: {remote_url}")
        else:
            current_url = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True,
                                         text=True).stdout.strip()
            if current_url != remote_url:
                run(["git", "remote", "set-url", "origin", remote_url])
                print(f"✅ 已更新远程仓库地址: {remote_url}")
            else:
                print(f"✅ 远程仓库已配置正确，无需修改。")
    except Exception as e:
        print(f"❌ 配置远程仓库失败: {e}")

    # ================= 3. 自动推送代码 =================
    print("\n📤 正在推送代码到 GitHub...")
    try:
        # 使用 -f 强制推送，防止远程仓库有初始 README 导致冲突
        run(["git", "push", "-f", "-u", "origin", "main"])
        print("✅ 代码推送成功！")
    except RuntimeError:
        print("❌ 推送失败，请检查 SSH Key 或网络连接！")
        sys.exit(1)

    # ================= 4. 自动打标签并触发发布 =================
    print(f"\n🏷️ 准备发布版本 {tag_name}...")
    try:
        # 检查标签是否已存在
        tags = subprocess.run(["git", "tag"], capture_output=True, text=True).stdout
        if tag_name not in tags.split():
            run(["git", "tag", tag_name])
            print(f"✅ 标签 {tag_name} 创建成功。")
        else:
            print(f"✅ 标签 {tag_name} 已存在。")

        # 精准推送这个标签，触发 GitHub Actions
        run(["git", "push", "origin", tag_name])
        print(f"🚀 标签 {tag_name} 推送成功！GitHub Actions 发版流水线已触发！")
    except Exception as e:
        print(f"❌ 标签推送失败: {e}")

    print("\n🎉 全自动发布流程结束！请前往 GitHub 的 Actions 页面查看发版进度。")


if __name__ == "__main__":
    main()
