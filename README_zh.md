# Nova-Agentic 🤖

> **基于 PySide 和 QML 打造的终极 AI Agent 框架。**
> *自主编码、极速 UI、企业级架构。*

[English](https://github.com/eagleye-china/Nova-Agentic/blob/main/README.md) | **简体中文**

[![PyPI version](https://img.shields.io/pypi/v/nova-agentic?color=blue&label=PyPI)](https://pypi.org/project/nova-agentic/)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://pypi.org/project/nova-agentic/)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/eagleye-china/Nova-Agentic/blob/main/LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/eagleye-china/Nova-Agentic?style=social)](https://github.com/eagleye-china/Nova-Agentic)

**Nova-Agentic** 是一款完全自主的 AI Agent，专为原生桌面端设计，能够自主编写、重构并执行代码。

它构建在 **PySide-Nova** 框架之上，将大语言模型（DeepSeek/OpenAI）的智慧与 GPU 加速的炫酷 QML 界面完美融合。它不仅仅是一个聊天机器人；它拥有“双手和双脚”——能够读取本地文件、批量生成代码，并自动执行语法检查。

## ✨ 核心特性

- 🧠 **自主 ReAct 循环**：自动读取、编写并修复代码。
- 🛡️ **内置架构宪法**：严格遵循开发规范，确保生成企业级高质量代码。
- 🚀 **QML 极速渲染**：毫秒级响应、原生暗黑模式、丝滑 Markdown 渲染。
- 📦 **生态无缝集成**：完美兼容 `pyside-quasar` 和 `pyside-nova` 框架。

## 📦 安装

```bash
pip install nova-agentic
```

## 🚀 快速上手

新建一个 Python 脚本并启动 Agent：

```python
import sys
from PySide6.QtWidgets import QApplication
from nova_agentic.ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

## 📸 效果预览

*(在此处放入你的炫酷 QML AI 界面截图或动图！)*

## 📜 开源协议

MIT License，允许商用和二次修改。