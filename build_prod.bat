@echo off
chcp 65001 >nul
echo =========================================
echo       nova-agentic 打包与发布
echo =========================================

if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist src\*.egg-info rmdir /s /q src\*.egg-info

python -m build
python -m twine check dist/*
python -m twine upload dist/*
pause
