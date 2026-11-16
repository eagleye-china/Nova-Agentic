# src/nova_agentic/core/chat_bridge.py

import datetime
import json
import os
import re
import subprocess
import tempfile
import base64
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal, Slot, QSettings, Property
from openai import OpenAI
from .md_renderer import MarkdownRenderer


def load_system_prompt():
    prompt_file = Path(__file__).parent.parent / "prompts" / "system_prompt.md"
    if prompt_file.exists():
        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"🚨 加载提示词失败: {e}")
    return "你是 PySide-Nova 框架的首席 AI 架构师。当前时间：{current_time}"


SYSTEM_PROMPT_TEMPLATE = load_system_prompt()


class ChatWorker(QThread):
    html_updated = Signal(str)
    action_log = Signal(str)
    finished_signal = Signal()
    error_signal = Signal(str)

    def __init__(self, messages, project_root, theme="dark"):
        super().__init__()
        self.messages = messages
        self.project_root = project_root
        self.theme = theme
        self._is_running = True
        self.read_files_cache = set()

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
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "将内容写入到指定文件中。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "相对路径"},
                            "content": {"type": "string", "description": "完整的文件内容"}
                        },
                        "required": ["file_path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_command",
                    "description": "在项目根目录下执行终端命令，并返回输出结果（stdout 和 stderr）。用于运行测试、执行脚本等。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "要执行的命令，如 'python main.py' 或 'pytest'"}
                        },
                        "required": ["command"]
                    }
                }
            }
        ]

    def stop(self):
        self._is_running = False

    def _get_safe_path(self, file_path):
        file_path = file_path.replace("\\", "/")
        if os.path.isabs(file_path):
            full_path = Path(file_path).resolve()
        else:
            full_path = Path(os.path.join(self.project_root, file_path)).resolve()

        base_dir = Path(os.path.join(self.project_root, "..")).resolve()
        try:
            full_path.relative_to(base_dir)
        except ValueError:
            return None
        return str(full_path)

    def _read_file(self, file_path):
        full_path = self._get_safe_path(file_path)
        if not full_path: return "错误: 越权访问！只能读取项目目录内的文件。"
        if not os.path.exists(full_path): return f"错误: 文件 {file_path} 不存在。"
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"读取失败: {str(e)}"

    def _write_file(self, file_path, content):
        full_path = self._get_safe_path(file_path)
        if not full_path: return "错误: 越权访问！只能修改项目目录内的文件。"
        dir_path = os.path.dirname(full_path)
        if not os.path.exists(dir_path):
            return f"错误: 目标文件夹不存在！请确认路径是否正确: {dir_path}。已取消写入。"
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"成功: 文件已成功写入！\n完整绝对路径: {full_path}"
        except Exception as e:
            return f"写入失败: {str(e)}"

    def _run_command(self, command):
        try:
            env = os.environ.copy()
            env["QT_QPA_PLATFORM"] = "offscreen"
            env["PYTHONIOENCODING"] = "utf-8"
            result = subprocess.run(command, shell=True, cwd=self.project_root, capture_output=True, encoding="utf-8",
                                    errors="replace", timeout=15, env=env)
            out = (result.stdout or "").strip()
            err = (result.stderr or "").strip()
            output = f"{out}\n{err}".strip()
            if result.returncode == 0:
                return f"执行成功 (返回码 0):\n{output}"
            else:
                return f"执行失败 (返回码 {result.returncode}):\n{output}"
        except subprocess.TimeoutExpired:
            return "执行失败: 命令超时（超过 15 秒被强制终止）。"
        except Exception as e:
            return f"执行异常: {str(e)}"

    def run(self):
        if not self.api_key:
            self.error_signal.emit("未配置 API Key。")
            return
        try:
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            system_prompt = SYSTEM_PROMPT_TEMPLATE.replace("{current_time}", now)
            final_messages = [{"role": "system", "content": system_prompt}] + self.messages

            while self._is_running:
                response = client.chat.completions.create(model=self.model, messages=final_messages, tools=self.tools,
                                                          stream=True)
                tool_calls_buffer = {}
                has_tool_calls = False
                full_content = ""

                for chunk in response:
                    if not self._is_running: break
                    delta = chunk.choices[0].delta
                    if delta.content:
                        full_content += delta.content
                        rendered_html = MarkdownRenderer.to_html(full_content, self.theme)
                        self.html_updated.emit(rendered_html)
                    if delta.tool_calls:
                        has_tool_calls = True
                        for tc in delta.tool_calls:
                            idx = tc.index
                            if idx not in tool_calls_buffer:
                                tool_calls_buffer[idx] = {"id": tc.id, "type": "function",
                                                          "function": {"name": "", "arguments": ""}}
                            if tc.function.name: tool_calls_buffer[idx]["function"]["name"] += tc.function.name
                            if tc.function.arguments: tool_calls_buffer[idx]["function"][
                                "arguments"] += tc.function.arguments

                if not self._is_running: break

                if has_tool_calls:
                    assistant_msg = {"role": "assistant", "content": full_content or "",
                                     "tool_calls": list(tool_calls_buffer.values())}
                    self.messages.append(assistant_msg)
                    final_messages.append(assistant_msg)

                    for tc in assistant_msg["tool_calls"]:
                        name = tc["function"]["name"]
                        args_str = tc["function"]["arguments"]
                        tool_content = "执行失败"
                        try:
                            args = json.loads(args_str)
                            if name == "read_file":
                                path = args.get("file_path", "")
                                if path not in self.read_files_cache:
                                    self.action_log.emit(f"📖 正在读取: {path}")
                                    self.read_files_cache.add(path)
                                tool_content = self._read_file(path)
                            elif name == "write_file":
                                user_msg = self.messages[-1]["content"]

                                # 如果用户的话里没有“保存”、“写入”、“文件”，直接拦截！
                                if "保存" not in user_msg and "写入" not in user_msg and "文件" not in user_msg:
                                    tool_content = "系统强制拦截：用户仅要求展示代码，未要求保存文件。请立刻停止调用工具，直接在聊天框中用 Markdown 代码块把完整代码输出给用户！"
                                    self.action_log.emit("⚠️ 已拦截 AI 的写文件请求")
                                else:
                                    path = args.get("file_path", "")
                                    content = args.get("content", "")
                                    self.action_log.emit(f"💾 正在写入: {path}")
                                    tool_content = self._write_file(path, content)
                            elif name == "run_command":
                                command = args.get("command", "")
                                self.action_log.emit(f"💻 正在执行命令: {command}")
                                tool_content = self._run_command(command)
                        except Exception as e:
                            tool_content = f"工具执行异常: {e}"

                        tool_msg = {"role": "tool", "tool_call_id": tc["id"], "content": tool_content}
                        self.messages.append(tool_msg)
                        final_messages.append(tool_msg)
                    self.action_log.emit("⏳ 动作执行完毕，AI 正在分析结果...")
                    continue

                if full_content: self.messages.append({"role": "assistant", "content": full_content})
                self.finished_signal.emit()
                return
        except Exception as e:
            if self._is_running: self.error_signal.emit(str(e))


class ChatBridge(QObject):
    htmlUpdated = Signal(str)
    actionLogged = Signal(str)
    replyFinished = Signal()
    replyError = Signal(str)
    requestApiKey = Signal()
    apiKeyChanged = Signal()
    commandExecuted = Signal(str)

    def __init__(self):
        super().__init__()
        self.history = []
        self.worker = None
        self.current_theme = "dark"
        self._settings = QSettings("NovaFramework", "NovaOrbit")

    def _get_has_api_key(self):
        return len(str(self._settings.value("api_key", ""))) > 0

    hasApiKey = Property(bool, _get_has_api_key, notify=apiKeyChanged)

    @Slot(str)
    def saveApiKey(self, key):
        self._settings.setValue("api_key", key)
        self.apiKeyChanged.emit()

    @Slot(str)
    def setTheme(self, theme_name):
        self.current_theme = theme_name

    @Slot(str)
    def sendMessage(self, text: str):
        if not self.hasApiKey:
            self.requestApiKey.emit()
            return
        if self.worker and self.worker.isRunning(): return

        self.history.append({"role": "user", "content": text})
        project_root = str(Path(__file__).resolve().parent.parent.parent.parent)

        self.worker = ChatWorker(self.history, project_root, self.current_theme)
        self.worker.setParent(self)
        self.worker.html_updated.connect(self.htmlUpdated)
        self.worker.action_log.connect(self.actionLogged)
        self.worker.finished_signal.connect(self.replyFinished)
        self.worker.error_signal.connect(self.replyError)
        self.worker.start()

    @Slot(str)
    def copyToClipboard(self, base64_code):
        """处理 QML 里点击的‘复制代码’按钮"""
        import base64
        from PySide6.QtGui import QGuiApplication
        try:
            code = base64.urlsafe_b64decode(base64_code).decode('utf-8')
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(code)
            self.actionLogged.emit("📋 代码已成功复制到剪贴板！")
        except Exception as e:
            self.actionLogged.emit(f"❌ 复制失败: {str(e)}")
