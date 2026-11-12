@echo off
chcp 65001 >nul
echo =========================================
echo       PySide-Quasar 打包与 TestPyPI 发布
echo =========================================

:: 1. 彻底清理旧构建（包括 build 和 egg-info）
echo [1/4] 正在清理旧构建文件...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist src\*.egg-info rmdir /s /q src\*.egg-info
echo ✅ 清理完成。

:: 2. 构建安装包
echo.
echo [2/4] 正在构建安装包 (python -m build)...
python -m build
if errorlevel 1 (
    echo.
    echo ❌ [ERROR] 构建失败！请检查上方错误信息。
    pause
    exit /b 1
)

:: 3. 检查安装包
echo.
echo [3/4] 正在检查 README 和包元数据 (twine check)...
python -m twine check dist/*
if errorlevel 1 (
    echo.
    echo ❌ [ERROR] 检查失败！请修正 README 或 pyproject.toml。
    pause
    exit /b 1
)

:: 4. 上传至 TestPyPI
echo.
echo [4/4] 正在上传至 TestPyPI...
python -m twine upload --repository testpypi dist/*
if errorlevel 1 (
    echo.
    echo ❌ [ERROR] 上传失败！请检查网络或 API Token。
    pause
    exit /b 1
)

echo.
echo =========================================
echo 🎉 发布成功！去 TestPyPI 查看你的页面吧！
echo =========================================
pause