# run.py
import os
import sys
import warnings

# 【核心补丁】把 src 目录加入 sys.path，而不是项目根目录
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

warnings.filterwarnings("ignore", category=DeprecationWarning)

# 注意这里：直接导入 dev_toolbox_pro，去掉了之前的 src. 前缀
from src.nova_agent.main import main

if __name__ == "__main__":
    main()
