my-ai-agent/ (独立新项目)
├── src/
│   ├── core/
│   │   ├── chat_worker.py
│   │   └── tools.py      # 后续可以在这里扩展更多的工具（如运行测试、查数据库）
│   ├── ui/
│   │   ├── chat_widget.py
│   │   └── main_window.py
│   └── main.py
├── pyproject.toml        # 依赖 pyside-quasar (通过 pip install -e 挂载)
└── run.py