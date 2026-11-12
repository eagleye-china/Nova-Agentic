@echo off
chcp 65001 >nul
:: ==========================================================
:: 企业级 Git 自动化提交工具 (Git Push Pipeline)
:: ==========================================================

echo.
echo ==========================================================
echo                🚀 企业级 Git 自动提交流水线
echo ==========================================================
echo.

:: 1. 检查是否在 Git 仓库中
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo ❌ [ERROR] 当前目录不是 Git 仓库！请确保在项目根目录下运行。
    pause
    exit /b 1
)

:: 2. 检查是否有未提交的更改
git diff --quiet && git diff --cached --quiet
if not errorlevel 1 (
    echo ✨ 工作区非常干净，没有任何更改需要提交。
    pause
    exit /b 0
)

:: 3. 提示用户选择提交类型 (Conventional Commits 规范)
echo 请选择本次提交的类型 (输入数字并回车):
echo   [1] feat     新增功能 (Feature)
echo   [2] fix      修复 Bug (Bug Fix)
echo   [3] docs     文档更新 (Documentation)
echo   [4] style    代码格式/UI调整 (Formatting/UI)
echo   [5] refactor 代码重构 (Refactor)
echo   [6] chore    构建/依赖/配置更改 (Chore)
echo   [7] 自定义   手动输入完整信息
echo.
set /p commit_type="👉 你的选择 (默认 1): "
if "%commit_type%"=="" set commit_type=1

set "prefix="
if "%commit_type%"=="1" set "prefix=feat"
if "%commit_type%"=="2" set "prefix=fix"
if "%commit_type%"=="3" set "prefix=docs"
if "%commit_type%"=="4" set "prefix=style"
if "%commit_type%"=="5" set "prefix=refactor"
if "%commit_type%"=="6" set "prefix=chore"

:: 4. 获取提交描述
if "%commit_type%"=="7" (
    set /p commit_msg="👉 请输入自定义 Commit 信息: "
) else (
    set /p commit_desc="👉 请输入简要描述 (例如: add NovaCard component): "
    set "commit_msg=%prefix%: %commit_desc%"
)

:: 5. 检查信息是否为空
if "%commit_msg%"=="" (
    echo ❌ [ERROR] Commit 信息不能为空！
    pause
    exit /b 1
)

echo.
echo 🔄 [1/4] 正在拉取远程最新代码 (git pull)...
git pull --rebase
if errorlevel 1 (
    echo ⚠️ [WARNING] 拉取失败，可能存在冲突。请手动解决冲突后再试。
    pause
    exit /b 1
)

echo.
echo 📦 [2/4] 正在暂存所有更改 (git add .)...
git add .

echo.
echo 📝 [3/4] 正在提交更改 (git commit)...
git commit -m "%commit_msg%"

echo.
echo ☁️ [4/4] 正在推送到远程仓库 (git push)...
git push
if errorlevel 1 (
    echo ❌ [ERROR] 推送失败！请检查网络或权限配置。
    pause
    exit /b 1
)

echo.
echo ==========================================================
echo 🎉 提交并推送成功！
echo 提交信息: %commit_msg%
echo ==========================================================
pause