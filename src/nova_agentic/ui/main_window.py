# src/nova_chat/ui/main_window.py
import html
import re
import sys

import markdown
from PySide6.QtCore import Qt, Slot, QTimer, QSettings
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser, QScrollArea,
    QTextEdit, QPushButton, QMessageBox, QFrame, QLabel,
    QLineEdit, QSizePolicy, QMainWindow, QApplication
)
from nova_agentic.core.chat_worker import ChatWorker
from pyside_quasar import ChatMessage


class AIBubble(QTextBrowser):
    """AI 专属的富文本气泡（支持代码高亮和复制）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOpenExternalLinks(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("""
            QTextBrowser {
                background-color: #263238;
                border: 1px solid #37474F;
                border-radius: 8px;
                padding: 8px;
                color: #ECEFF1;
            }
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    def update_html(self, html_text: str):
        self.setHtml(html_text)
        self._adjust_height()

    def _adjust_height(self):
        self.document().setTextWidth(self.viewport().width())
        self.setFixedHeight(int(self.document().size().height()) + 20)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._adjust_height()


class ChatWidget(QWidget):
    """独立的 AI 对话核心组件"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.chat_widget = None
        self.api_base = "https://api.deepseek.com"
        self.model_name = "deepseek-chat"
        self.project_root = r"D:\MyProjects\PyCharm\Project_Nova\pyside-nova"
        # self.project_root = r"D:\MyProjects\PyCharm\PySide6\pyside-quasar"

        self.settings = QSettings("eagleye-china", "nova_chat")
        self.api_key = self.settings.value("deepseek_api_key", "")

        self.messages = []
        self.worker = None
        self.current_ai_text = ""
        self.code_snippets = []
        self.current_ai_bubble = None

        self.render_timer = QTimer(self)
        self.render_timer.setInterval(80)
        self.render_timer.timeout.connect(self.update_current_bubble)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # ================= 隐藏的配置抽屉 =================
        self.config_widget = QWidget()
        self.config_widget.setStyleSheet("background-color: transparent;")
        config_layout = QHBoxLayout(self.config_widget)
        config_layout.setContentsMargins(0, 0, 0, 0)

        lbl_api = QLabel("API Key:")
        lbl_api.setStyleSheet("color: #ECEFF1; font-weight: bold;")
        lbl_api.setFixedWidth(60)

        self.input_api_key = QLineEdit()
        self.input_api_key.setPlaceholderText("请输入 DeepSeek API Key (sk-...)")
        self.input_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_api_key.setStyleSheet("""
            QLineEdit { 
                background-color: #263238; color: #ECEFF1; 
                border: 1px solid #37474F; border-radius: 4px; padding: 4px 8px; 
            }
        """)

        self.btn_save_key = QPushButton("保存")
        self.btn_save_key.setFixedWidth(60)
        self.btn_save_key.setStyleSheet("""
            QPushButton { background-color: #0277BD; color: white; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #0288D1; }
        """)
        self.btn_save_key.clicked.connect(self.save_api_key)

        config_layout.addWidget(lbl_api)
        config_layout.addWidget(self.input_api_key)
        config_layout.addWidget(self.btn_save_key)
        layout.addWidget(self.config_widget)

        self.config_widget.setVisible(False)
        if self.api_key:
            self.input_api_key.setText(self.api_key)

        # ================= 聊天滚动区 =================
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea { border: none; background-color: #1A2228; border-radius: 8px; }
            QScrollBar:vertical {
                border: none;
                background: #1A2228;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #455A64;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover { background: #546E7A; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        self.chat_container = QWidget()
        self.chat_container.setStyleSheet("background-color: #1A2228;")
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(15)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)

        self.scroll_area.setWidget(self.chat_container)
        layout.addWidget(self.scroll_area, 1)

        # ================= 底部输入区 =================
        input_frame = QFrame()
        input_frame.setFixedHeight(80)
        input_frame.setStyleSheet(
            "QFrame { background-color: #263238; border: 1px solid #37474F; border-radius: 8px; }")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(10, 10, 10, 10)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("输入你的问题... (Ctrl+Enter 发送)")
        self.input_text.setStyleSheet(
            "QTextEdit { border: none; background-color: transparent; font-size: 14px; color: #ECEFF1; }")
        self.input_text.installEventFilter(self)
        input_layout.addWidget(self.input_text)

        self.btn_send = QPushButton("发送 🚀")
        self.btn_send.setFixedSize(80, 40)
        self.btn_send.setStyleSheet("""
            QPushButton { background-color: #0277BD; color: white; font-weight: bold; border-radius: 6px; }
            QPushButton:hover { background-color: #0288D1; }
            QPushButton:disabled { background-color: #37474F; color: #90A4AE; }
        """)
        self.btn_send.clicked.connect(self.send_message)
        input_layout.addWidget(self.btn_send)

        layout.addWidget(input_frame, 0)

    def _show_dark_messagebox(self, title: str, text: str, icon=QMessageBox.Icon.Warning):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon)
        msg.setStyleSheet("""
            QMessageBox { background-color: #1E272E; }
            QLabel { color: #ECEFF1; font-size: 14px; }
            QPushButton { 
                background-color: #0277BD; color: white; 
                border-radius: 4px; padding: 6px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #0288D1; }
        """)
        msg.exec()

    def eventFilter(self, obj, event):
        if obj == self.input_text and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                self.send_message()
                return True
        return super().eventFilter(obj, event)

    def save_api_key(self):
        key = self.input_api_key.text().strip()
        if key and not key.startswith("sk-"):
            self._show_dark_messagebox("格式错误", "API Key 通常以 'sk-' 开头！")
            return
        self.api_key = key
        self.settings.setValue("deepseek_api_key", key)
        self.btn_save_key.setText("✅ 成功")
        QTimer.singleShot(800, self._on_save_finished)

    def _on_save_finished(self):
        self.btn_save_key.setText("保存")
        self.config_widget.setVisible(False)

    @Slot()
    def send_message(self):
        if not self.api_key:
            self._show_dark_messagebox("缺少 API Key", "请先在顶部配置 API Key！")
            self.config_widget.setVisible(True)
            self.input_api_key.setFocus()
            return

        text = self.input_text.toPlainText().strip()
        if not text: return

        self.input_text.clear()
        self.messages.append({"role": "user", "content": text})

        user_msg = ChatMessage(text=text, sent=True, avatar_text="我")
        self.chat_layout.addWidget(user_msg)
        self.scroll_to_bottom()

        self.current_ai_text = ""
        self.current_ai_bubble = AIBubble()
        self.current_ai_bubble.setStyleSheet(self.current_ai_bubble.styleSheet() + "background-color: #1E272E;")
        self.chat_layout.addWidget(self.current_ai_bubble)

        self.btn_send.setEnabled(False)
        self.btn_send.setText("思考中")
        self.render_timer.start()

        self.worker = ChatWorker(self.api_key, self.api_base, self.model_name, self.messages, self.project_root)
        self.worker.chunk_received.connect(self.on_chunk_received)
        self.worker.action_log.connect(self.on_action_log)
        self.worker.finished_signal.connect(self.on_ai_finished)
        self.worker.error_signal.connect(self.on_error)
        self.worker.start()

    @Slot(str)
    def on_chunk_received(self, chunk):
        self.current_ai_text += chunk

    @Slot(str)
    def on_action_log(self, log_msg):
        sys_bubble = QLabel(f"⚙️ {log_msg}")
        sys_bubble.setWordWrap(True)
        sys_bubble.setStyleSheet("""
            QLabel {
                background-color: #1E272E;
                color: #4CAF50;
                border: 1px solid #2E7D32;
                border-radius: 6px;
                padding: 8px 12px;
                font-family: Consolas, monospace;
                font-size: 13px;
            }
        """)
        self.chat_layout.addWidget(sys_bubble)
        self.scroll_to_bottom()

    def update_current_bubble(self):
        if not self.current_ai_bubble:
            return

        display_text = self.current_ai_text if self.current_ai_text else "思考中..."
        if display_text.count("```") % 2 != 0:
            display_text += "\n```"

        html_content, _ = self.render_markdown(display_text, 0)
        self.current_ai_bubble.update_html(html_content)
        self.scroll_to_bottom()

    @Slot()
    def on_ai_finished(self):
        self.render_timer.stop()
        self.messages.append({"role": "assistant", "content": self.current_ai_text})
        self.update_current_bubble()
        self.btn_send.setEnabled(True)
        self.btn_send.setText("发送 🚀")
        self.current_ai_bubble = None

    @Slot(str)
    def on_error(self, err):
        self.render_timer.stop()
        self.btn_send.setEnabled(True)
        self.btn_send.setText("发送 🚀")
        if self.current_ai_bubble:
            self.current_ai_bubble.update_html(f"<span style='color:#FF5252;'>⚠️ 发生错误: {err}</span>")
        self.current_ai_bubble = None

        # ✅ 核心修复：如果是 Key 失效/认证失败，自动清空本地错误 Key 并弹出配置框
        if "401" in err or "Authentication Fails" in err or "invalid" in err.lower():
            self.api_key = ""
            self.settings.remove("deepseek_api_key")
            self.config_widget.setVisible(True)
            self.input_api_key.clear()
            self.input_api_key.setFocus()
            self._show_dark_messagebox(
                "API Key 已失效",
                "您的 API Key 已被删除或无效，请重新输入并保存！",
                QMessageBox.Icon.Critical
            )

    def scroll_to_bottom(self):
        """✅ 修复：确保这个方法存在并正确滚动"""
        QTimer.singleShot(50, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))

    def render_markdown(self, content: str, start_idx: int) -> tuple[str, int]:
        html_content = markdown.markdown(
            content,
            extensions=['fenced_code', 'codehilite', 'tables'],
            extension_configs={'codehilite': {'noclasses': True, 'pygments_style': 'dracula'}}
        )
        current_idx = start_idx

        def repl(m):
            nonlocal current_idx
            idx = current_idx
            current_idx += 1

            inner_html = m.group(2)
            pure_code = re.sub(r'<[^>]+>', '', inner_html)
            pure_code = html.unescape(pure_code)
            self.code_snippets.append(pure_code.strip())

            block = f"""
            <div style="margin: 12px 0; border-radius: 8px; padding: 0;">
                <div style="background-color: #21222c; padding: 8px 12px; border-top-left-radius: 8px; border-top-right-radius: 8px; text-align: right;">
                    <a href="action://copy/{idx}" style="color: #8be9fd; text-decoration: none; font-size: 12px; margin-right: 15px;">📋 复制</a>
                </div>
                <div style="background-color: #282a36; padding: 12px; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;">
                    <pre style="background-color: transparent; border: none; margin: 0; padding: 0; color: #f8f8f2; font-family: Consolas, monospace; font-size: 13px; white-space: pre-wrap;">{inner_html}</pre>
                </div>
            </div>
            """
            return block

        html_content = re.sub(r'(<pre.*?>)(.*?)(</pre>)', repl, html_content, flags=re.DOTALL)
        return html_content, current_idx

    def closeEvent(self, event):
        """确保主窗口关闭时，后台线程安全退出"""
        if hasattr(self.chat_widget, "worker") and self.chat_widget.worker and self.chat_widget.worker.isRunning():
            self.chat_widget.worker.stop()
            self.chat_widget.worker.wait(1000)
        super().closeEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nova Agent - 你的 AI 架构师")
        self.resize(1000, 800)

        self.chat_widget = ChatWidget(self)
        self.setCentralWidget(self.chat_widget)

        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QLabel { color: #ECEFF1; }
            QWidget { color: #ECEFF1; }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
