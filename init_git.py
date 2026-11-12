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
            sys.exit(1)
    print(result.stdout.strip() or result.stderr.strip())


def get_project_info():
    """智能读取当前项目信息"""
    # 1. 默认用文件夹名作为仓库名
    current_dir = Path.cwd()
    repo_name = current_dir.name

    project_name = repo_name
    version = "0.1.0"

    # 2. 尝试从 pyproject.toml 读取精准信息
    toml_path = current_dir / "pyproject.toml"
    if toml_path.exists():
        with open(toml_path, "r", encoding="utf-8") as f:
            content = f.read()

            # 提取 name
            name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            if name_match:
                project_name = name_match.group(1)

            # 提取 version
            version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if version_match:
                version = version_match.group(1)

    return repo_name, project_name, version


def main():
    repo_name, project_name, version = get_project_info()

    print(f"🚀 开始初始化【{project_name}】企业级 Git 仓库 (v{version})...")

    if os.path.exists(".git"):
        print("⚠️ 当前目录已经存在 .git 文件夹，已跳过 git init。")
    else:
        # 1. 初始化仓库
        run(["git", "init"])
        run(["git", "branch", "-M", "main"])

        # 2. 配置换行符规范（Windows 必备）
        run(["git", "config", "core.autocrlf", "false"])

        # 3. 添加所有文件并首次提交
        run(["git", "add", "."])
        commit_msg = f"feat: initial release of {project_name} v{version}"
        run(["git", "commit", "-m", commit_msg])

    print("\n✅ 本地 Git 初始化完成！")
    print("====================================")
    print("🔗 接下来请执行以下两步关联远程仓库并推送：")
    print(f"   1. git remote add origin git@github.com:{GITHUB_USER}/{repo_name}.git")
    print("   2. git push -u origin main")
    print("====================================")
    print(f"🏷️ 发布正式版 v{version} 时（推荐用精准打击）：")
    print(f"   1. git tag v{version}")
    print(f"   2. git push origin main v{version}")
    print("====================================")
    print("💡 如需全量同步所有标签：git push origin main --tags")


if __name__ == "__main__":
    main()
