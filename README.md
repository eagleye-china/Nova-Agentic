# Nova-Agentic 🤖

> **The Ultimate QML-powered AI Agent framework for PySide.**
> *Autonomous coding, blazing fast UI, and enterprise-grade architecture.*

**English** | [简体中文](https://github.com/eagleye-china/Nova-Agentic/blob/main/README_zh.md)

[![PyPI version](https://img.shields.io/pypi/v/nova-agentic?color=blue&label=PyPI)](https://pypi.org/project/nova-agentic/)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://pypi.org/project/nova-agentic/)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/eagleye-china/Nova-Agentic/blob/main/LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/eagleye-china/Nova-Agentic?style=social)](https://github.com/eagleye-china/Nova-Agentic)

**Nova-Agentic** is a fully autonomous AI Agent designed to write, refactor, and execute code natively on your desktop. 

Built on top of the **PySide-Nova** framework, it combines the raw intelligence of LLMs (DeepSeek/OpenAI) with a stunning, GPU-accelerated QML interface. It is not just a chat bot; it has hands and feet—capable of reading local files, writing multiple files, and running syntax checks automatically.

## ✨ Features

- 🧠 **Autonomous ReAct Loop**: Reads, writes, and fixes code automatically.
- 🛡️ **Built-in Constitution**: Strict architectural guidelines to ensure enterprise-grade code generation.
- 🚀 **QML-Powered UI**: Blazing fast, native dark mode, smooth markdown rendering.
- 📦 **Seamless Integration**: Works directly with the `pyside-quasar` and `pyside-nova` frameworks.

## 📦 Installation

```bash
pip install nova-agentic
```

## 🚀 Quick Start

Create a Python script and launch the Agent:

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

## 📸 Screenshots

*(Add your gorgeous QML AI UI screenshot or GIF here!)*

## 📜 License

MIT License.