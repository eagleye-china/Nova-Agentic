# src/nova_agentic/core/chat_bridge.py

import datetime
import json
import os
import shutil
import re

from PySide6.QtCore import QObject, QThread, Signal, Slot, QSettings
from openai import OpenAI

SYSTEM_PROMPT_TEMPLATE = """
你是 PySide-Nova 框架的首席 AI 架构师。PySide-Nova 是一个基于 PySide6 + QML 的企业级 UI 组件库，专为工业 HMI、大屏和数据密集型应用设计。

当前系统时间已校准为：{current_time}
"""


class ChatWorker(QThread):
    chunk_received = Signal(str)
    action_log = Signal(str)
    finished_signal = Signal()
    error_signal = Signal(str)

    def __init__(self, messages, project_root):
        super().__init__()
        self.messages = messages
        self.project_root = project_root
        self._is_running = True

        settings = QSettings("NovaFramework", "NovaOrbit")
        self.api_key = str(settings.value("api_key", ""))
        self.base_url = str(settings.value("base_url", "https://api.deepseek.com"))
        self.model = str(settings.value("model", "deepseek-chat"))

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "读取项目中的文件内容。",
                    "parameters": {
                        "type": "object",
                        "properties": {"file_path": {"type": "string", "description": "相对路径"}},
                        "required": ["file_path"]
                    }
                }
            }
        ]

    def stop(self):
        self._is_running = False

    def _read_file(self, file_path):
        full_path = os.path.join(self.project_root, file_path)
        if not os.path.exists(full_path):
            return f"错误: 文件 {file_path} 不存在。"
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"读取失败: {str(e)}"

    def run(self):
        if not self.api_key:
            self.error_signal.emit("未配置 API Key，请前往环境变量或配置文件设置。")
            return
        try:
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            system_prompt = SYSTEM_PROMPT_TEMPLATE.replace("{current_time}", now)
            final_messages = [{"role": "system", "content": system_prompt}] + self.messages

            while self._is_running:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=final_messages,
                    tools=self.tools,
                    stream=True
                )
                tool_calls_buffer = {}
                has_tool_calls = False
                full_content = ""

                for chunk in response:
                    if not self._is_running:
                        break
                    delta = chunk.choices[0].delta

                    if delta.content:
                        full_content += delta.content
                        self.chunk_received.emit(delta.content)

                    if delta.tool_calls:
                        has_tool_calls = True
                        for tc in delta.tool_calls:
                            idx = tc.index
                            if idx not in tool_calls_buffer:
                                tool_calls_buffer[idx] = {"id": tc.id, "type": "function",
                                                          "function": {"name": "", "arguments": ""}}
                            if tc.function.name:
                                tool_calls_buffer[idx]["function"]["name"] += tc.function.name
                            if tc.function.arguments:
                                tool_calls_buffer[idx]["function"]["arguments"] += tc.function.arguments

                if not self._is_running:
                    break

                if has_tool_calls:
                    assistant_msg = {"role": "assistant", "content": full_content or ""}
                    assistant_msg["tool_calls"] = list(tool_calls_buffer.values())
                    self.messages.append(assistant_msg)
                    final_messages.append(assistant_msg)

                    for tc in assistant_msg["tool_calls"]:
                        name = tc["function"]["name"]
                        args_str = tc["function"]["arguments"]
                        tool_content = "执行失败"
                        try:
                            args = json.loads(args_str)
                            if name == "read_file":
                                self.action_log.emit(f"📖 正在读取: {args.get('file_path')}")
                                tool_content = self._read_file(args.get("file_path", ""))
                        except Exception as e:
                            tool_content = f"工具异常: {e}"

                        tool_msg = {"role": "tool", "tool_call_id": tc["id"], "content": tool_content}
                        self.messages.append(tool_msg)
                        final_messages.append(tool_msg)

                    self.action_log.emit("⏳ 工具执行完毕，正在请求 AI 进行下一步思考...")
                    continue

                if full_content:
                    self.messages.append({"role": "assistant", "content": full_content})

                self.finished_signal.emit()
                return
        except Exception as e:
            if self._is_running:
                self.error_signal.emit(str(e))


class ChatBridge(QObject):
    chunkReceived = Signal(str)
    actionLogged = Signal(str)
    replyFinished = Signal()
    replyError = Signal(str)

    def __init__(self):
        super().__init__()
        self.history = []
        self.worker = None
        self._settings = QSettings("NovaFramework", "NovaOrbit")

    @Slot(str)
    def saveApiKey(self, key):
        self._settings.setValue("api_key", key)
        print(f"✅ [Python] API Key 已保存至注册表")

    @Slot(str)
    def sendMessage(self, text: str):
        if self.worker and self.worker.isRunning():
            return

        # ✅ 核心修复：安全清理旧的 worker，防止底层内存崩溃
        if self.worker:
            self.worker.quit()
            self.worker.wait()
            self.worker.deleteLater()
            self.worker = None

        self.history.append({"role": "user", "content": text})
        from pathlib import Path
        project_root = str(Path(__file__).resolve().parent.parent.parent)

        self.worker = ChatWorker(self.history, project_root)
        self.worker.setParent(self)  # ✅ 给线程绑个爹，防止被 Python GC 误杀！

        self.worker.chunk_received.connect(self.chunkReceived)
        self.worker.action_log.connect(self.actionLogged)
        self.worker.finished_signal.connect(self.replyFinished)
        self.worker.error_signal.connect(self.replyError)
        self.worker.start()
