# app/utils/logger.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PySide6.QtCore import QObject, Signal


class LogSignalBridge(QObject):
    """将 Python 标准日志转化为 Qt 信号"""
    new_log = Signal(str)


class QtLogHandler(logging.Handler):
    """自定义日志处理器，把日志发给 UI"""

    def __init__(self, bridge: LogSignalBridge):
        super().__init__()
        self.bridge = bridge

    def emit(self, record):
        msg = self.format(record)
        self.bridge.new_log.emit(msg)


def setup_logger(bridge: LogSignalBridge = None):
    log_dir = Path.home() / ".svg_collector_pro" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger()  # 捕获所有模块的日志，包括 timer
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger  # 已经初始化过则跳过

    # 文件日志
    file_handler = RotatingFileHandler(log_dir / "app.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # noqa
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 如果传入了 UI 桥接对象，则把日志同步推送到 UI 控制台
    if bridge:
        qt_handler = QtLogHandler(bridge)
        qt_handler.setFormatter(logging.Formatter('%(message)s'))  # UI 上只显示纯净内容
        logger.addHandler(qt_handler)

    return logger
