# run.py
import os
import sys
import warnings

# 【核心补丁】把 src 目录加入 sys.path，而不是项目根目录
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

warnings.filterwarnings("ignore", category=DeprecationWarning)

from main import main

if __name__ == "__main__":
    main()
