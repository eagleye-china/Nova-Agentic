import os
import re
import subprocess
import sys
from pathlib import Path

GITHUB_USER = "eagleye-china"

def run(cmd, ignore_error=False):
    print(f"👉 正在执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and not ignore_error:
        print(f"❌ 错误: {result.stderr}")
        raise RuntimeError(result.stderr)
    if result.stdout.strip():
        print(result.stdout.strip())
    return result

def get_project_info():
    current_dir = Path.cwd()
    # ✅ 修复：直接使用生成时写死的 REPO_NAME，防止路径错乱
    repo_name = "Nova-Agentic"
    project_name = "nova-agentic"
    version = "0.1.0"
    toml_path = current_dir / "pyproject.toml"
    if toml_path.exists():
        with open(toml_path, "r", encoding="utf-8") as f:
            content = f.read()
            # ✅ 修复正则转义问题
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

    if not os.path.exists(".git"):
        run(["git", "init"])
        run(["git", "branch", "-M", "main"])
        run(["git", "config", "core.autocrlf", "false"])
        run(["git", "add", "."])
        run(["git", "commit", "-m", f"feat: initial release of {project_name} v{version}"])
        print("✅ 本地 Git 初始化完成！")
    else:
        print("✅ 已检测到 Git 仓库，跳过初始化。")

    try:
        remotes = subprocess.run(["git", "remote"], capture_output=True, text=True).stdout
        if "origin" not in remotes:
            run(["git", "remote", "add", "origin", remote_url])
            print(f"✅ 已关联远程仓库: {remote_url}")
        else:
            current_url = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True).stdout.strip()
            if current_url != remote_url:
                run(["git", "remote", "set-url", "origin", remote_url])
                print(f"✅ 已更新远程仓库地址: {remote_url}")
            else:
                print(f"✅ 远程仓库已配置正确，无需修改。")
    except Exception as e:
        print(f"❌ 配置远程仓库失败: {e}")

    print("\\n📤 正在推送代码到 GitHub...")
    try:
        run(["git", "push", "-f", "-u", "origin", "main"])
        print("✅ 代码推送成功！")
    except RuntimeError:
        print("❌ 推送失败，请检查 SSH Key 或网络连接！")
        sys.exit(1)

    print(f"\\n🏷️ 准备发布版本 {tag_name}...")
    try:
        tags = subprocess.run(["git", "tag"], capture_output=True, text=True).stdout
        if tag_name not in tags.split():
            run(["git", "tag", tag_name])
            print(f"✅ 标签 {tag_name} 创建成功。")
        else:
            print(f"✅ 标签 {tag_name} 已存在。")
        run(["git", "push", "origin", tag_name])
        print(f"🚀 标签 {tag_name} 推送成功！GitHub Actions 发版流水线已触发！")
    except Exception as e:
        print(f"❌ 标签推送失败: {e}")

    print("\\n🎉 全自动发布流程结束！请前往 GitHub 的 Actions 页面查看发版进度。")

if __name__ == "__main__":
    main()
