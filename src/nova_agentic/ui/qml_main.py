# src/nova_chat/ui/qml_main.py
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Slot, Property, QAbstractListModel, QModelIndex, Qt, QTimer, QUrl, QSettings
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
# ✅ 引入你真正的核心引擎
from nova_agentic.core.chat_worker import ChatWorker


class MessageModel(QAbstractListModel):
    TextRole = Qt.ItemDataRole.UserRole + 1
    IsUserRole = Qt.ItemDataRole.UserRole + 2
    IsSystemRole = Qt.ItemDataRole.UserRole + 3

    def __init__(self):
        super().__init__()
        self._messages = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._messages)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._messages)):
            return None
        msg = self._messages[index.row()]
        if role == self.TextRole:
            return msg.get("text", "")
        elif role == self.IsUserRole:
            return msg.get("isUser", False)
        elif role == self.IsSystemRole:
            return msg.get("isSystem", False)
        return None

    def roleNames(self):
        return {
            self.TextRole: b"text",
            self.IsUserRole: b"isUser",
            self.IsSystemRole: b"isSystem"
        }

    def add_message(self, text, is_user, is_system=False):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._messages.append({"text": text, "isUser": is_user, "isSystem": is_system})
        self.endInsertRows()

    def update_last_message(self, text):
        """用于流式更新最后一条 AI 消息"""
        if not self._messages:
            return
        last_index = self.rowCount() - 1
        self._messages[last_index]["text"] = text
        # 通知 QML 数据已改变
        idx = self.index(last_index, 0)
        self.dataChanged.emit(idx, idx, [self.TextRole])


class ChatBridge(QObject):
    def __init__(self):
        super().__init__()
        self._model = MessageModel()
        self.messages = []
        self.current_ai_text = ""
        self.worker = None

        # ✅ 核心修复：动态获取当前 nova-agent 项目的根目录
        import os
        # __file__ 是 .../nova-agent/src/nova_chat/ui/qml_main.py
        # 往上推 4 层得到 nova-agent 的根目录
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

        self.settings = QSettings("eagleye-china", "nova_chat")
        self.api_key = self.settings.value("deepseek_api_key", "")

        self.render_timer = QTimer()
        self.render_timer.setInterval(80)
        self.render_timer.timeout.connect(self._update_ai_bubble)

        self._model.add_message("你好！我是 QML 版架构师。已连接核心引擎，随时准备为你写代码。", False)

    @Property(QObject, constant=True)
    def messagesModel(self):
        return self._model

    @Slot(str)
    def send_user_message(self, text):
        if not self.api_key:
            self._model.add_message("⚠️ 错误：未配置 API Key！请使用 QWidget 版配置，或修改 settings。", False)
            return

        # 1. 添加用户消息
        self._model.add_message(text, True)
        self.messages.append({"role": "user", "content": text})

        # 2. 准备 AI 气泡
        self.current_ai_text = ""
        self._model.add_message("思考中...", False)
        self.render_timer.start()

        # 3. 启动核心 Worker
        self.worker = ChatWorker(self.api_key, "https://api.deepseek.com", "deepseek-chat", self.messages,
                                 self.project_root)
        self.worker.chunk_received.connect(self.on_chunk_received)
        self.worker.action_log.connect(self.on_action_log)
        self.worker.finished_signal.connect(self.on_ai_finished)
        self.worker.error_signal.connect(self.on_error)
        self.worker.start()

    @Slot(str)
    def on_chunk_received(self, chunk):
        self.current_ai_text += chunk

    def _update_ai_bubble(self):
        """定时器触发的流式更新"""
        if self.current_ai_text:
            self._model.update_last_message(self.current_ai_text)

    @Slot(str)
    def on_action_log(self, log_msg):
        # 把 AI 执行的动作（如写文件）作为一条系统特殊消息插入
        self._model.add_message(f"⚙️ {log_msg}", False, is_system=True)

    @Slot()
    def on_ai_finished(self):
        self.render_timer.stop()
        self._update_ai_bubble()  # 确保最终文字完全展示
        self.messages.append({"role": "assistant", "content": self.current_ai_text})

        # 如果没有文字返回（只是执行了工具），补一句完成提示
        if not self.current_ai_text:
            self._model.update_last_message("✅ 任务执行完毕。")
        self.worker = None

    @Slot(str)
    def on_error(self, err):
        self.render_timer.stop()
        self._model.update_last_message(f"⚠️ 发生错误: {err}")
        self.worker = None


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    engine.warnings.connect(lambda warnings: [print("QML Error:", w.toString()) for w in warnings])

    bridge = ChatBridge()
    engine.rootContext().setContextProperty("bridge", bridge)

    qml_file = Path(__file__).parent / "qml_chat_view.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
