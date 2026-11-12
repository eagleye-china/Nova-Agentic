# -*- coding: utf-8 -*-
from pathlib import Path
import sys

# 优先从本地的 pyproject.toml 读取版本号（开发模式）
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

try:
    # 假设当前文件在 src/项目名/__init__.py，往上找 3 层就是项目根目录
    _pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    with open(_pyproject_path, "rb") as f:
        _data = tomllib.load(f)
        __version__ = _data["project"]["version"]
except Exception:
    # 如果读不到，再尝试从已安装的包元数据读取（生产模式）
    from importlib.metadata import version, PackageNotFoundError
    try:
        __version__ = version("nova-agentic")
    except PackageNotFoundError:
        __version__ = "0.1.0"

__all__ = ["__version__"]
