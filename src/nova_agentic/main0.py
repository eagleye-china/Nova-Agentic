# src/dev_toolbox_pro/main.py
import ctypes
import sys
from pathlib import Path

from PySide6.QtCore import QTranslator, QLibraryInfo
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from nova_agentic.ui.main_window import MainWindow
from nova_agentic.utils.logger import setup_logger
from nova_agentic.version import APP_USER_MODEL_ID, APP_NAME

try:
    from resources import resources_rc  # noqa
except ImportError:
    print("[WARN] 未找到 resources_rc，图标可能无法显示。")


def main():
    if sys.platform == "win32":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
        except Exception as e:
            print(f"设置 AppUserModelID 失败: {e}")

    logger = setup_logger()
    logger.info(f"{APP_NAME} starting...")

    app = QApplication(sys.argv)

    # 汉化逻辑
    translator = QTranslator()
    translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    if translator.load("qtbase_zh_CN", translations_path):
        app.installTranslator(translator)

    app.setApplicationName(APP_NAME)
    app.setWindowIcon(QIcon(":/icons/chat-chat.svg"))

    # 加载样式表 (因为 main.py 和 ui 同级，直接用相对路径)
    qss_path = Path(__file__).parent / "ui" / "styles.qss"
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
    else:
        logger.warning(f"未找到样式表: {qss_path}")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
