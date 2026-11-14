import logging
import time
from contextlib import contextmanager

_NS_PER_SEC = 1_000_000_000
_NS_PER_MS = 1_000_000
_NS_PER_US = 1_000

_logger = logging.getLogger("timer")


def _format_duration(elapsed_ns: int, precision: int = 3) -> str:
    if elapsed_ns >= _NS_PER_SEC:
        return f"{elapsed_ns / _NS_PER_SEC:.{precision}f} 秒"
    if elapsed_ns >= _NS_PER_MS:
        return f"{elapsed_ns / _NS_PER_MS:.{precision}f} 毫秒"
    if elapsed_ns >= _NS_PER_US:
        return f"{elapsed_ns / _NS_PER_US:.{precision}f} 微秒"
    return f"{elapsed_ns} 纳秒"


@contextmanager
def timer(label: str = "运行时间", *, precision: int = 3, indent: int = 0, level: int = logging.INFO):
    start_ns = time.perf_counter_ns()
    prefix = "  " * indent
    try:
        yield
    finally:
        elapsed_ns = time.perf_counter_ns() - start_ns
        formatted = _format_duration(elapsed_ns, precision)
        plain = f"{prefix}⏱️ {label}：{formatted}"
        # 只交给 logging，由 UI 的 LogHandler 去展示，彻底告别 print 带来的 IO 阻塞
        _logger.log(level, plain)
