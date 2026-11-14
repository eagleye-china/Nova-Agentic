# main.py (nova-agentic 根目录)

import sys
from pathlib import Path
from PySide6.QtCore import QUrl, qInstallMessageHandler
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from pyside_nova import install_qml_import_path, theme_manager
from nova_agentic.core.chat_bridge import ChatBridge

current_dir = Path(__file__).resolve().parent


# 🚨 核心修复 1：安装 QML 底层报错拦截器
def handler(mode, context, message):
    print(f"🚨 [QML Error] {message}")


qInstallMessageHandler(handler)


def main() -> int:
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # ✅ 捕获加载失败的事件
    engine.warnings.connect(lambda warnings: [print("⚠️ [QML Warning]:", w.toString()) for w in warnings])

    tm = theme_manager()
    tm.setParent(app)

    chat_bridge = ChatBridge()
    chat_bridge.setParent(app)

    engine.rootContext().setContextProperty("ThemeManager", tm)
    engine.rootContext().setContextProperty("ChatBridge", chat_bridge)

    install_qml_import_path(engine)

    qml_file = current_dir / "src" / "nova_agentic" / "qml" / "main.qml"
    print(f"🔍 正在尝试加载 QML: {qml_file}")

    engine.load(QUrl.fromLocalFile(str(qml_file)))

    if not engine.rootObjects():
        print("❌ 加载彻底失败！请查看上方是否有 QML Error 输出。")
        return -1

    print("✅ QML 加载成功，启动事件循环！")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())