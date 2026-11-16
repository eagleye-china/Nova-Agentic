# main.py

import sys
from pathlib import Path
from PySide6.QtCore import QUrl, qInstallMessageHandler
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from pyside_nova import install_qml_import_path, theme_manager
from nova_agentic.core.chat_bridge import ChatBridge

current_dir = Path(__file__).resolve().parent


def qml_handler(mode, context, message):
    print(f"🚨 [QML]: {message}")


qInstallMessageHandler(qml_handler)


def main() -> int:
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    tm = theme_manager()
    tm.setParent(app)

    chat_bridge = ChatBridge()
    chat_bridge.setParent(app)

    engine.rootContext().setContextProperty("ThemeManager", tm)
    engine.rootContext().setContextProperty("ChatBridge", chat_bridge)
    install_qml_import_path(engine)

    qml_file = current_dir / "src" / "nova_agentic" / "qml" / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))

    if not engine.rootObjects():
        print("❌ 加载失败，请看上面的报错。")
        return -1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())


