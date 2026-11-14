# src/dev_toolbox_pro/version.py

# --- 应用基础信息 ---
APP_NAME = "企业级开发工具箱 (Pro)"
APP_NAME_EN = "Enterprise Dev Toolbox Pro"
APP_VERSION = "1.0.0"  # 作为 V1.0 正式版
ORG_NAME = "铝脑 (AluBrain)"
ORG_DOMAIN = "alubrain.com"

# --- 开发者与版权信息 ---
AUTHOR = "eagleye"
COPYRIGHT = f"Copyright © 2026 {ORG_NAME}"

# --- Windows 任务栏图标标识 (AppUserModelID) ---
# 规范要求：仅限字母、数字、点、下划线、连字符。不能有空格。
# 建议将版本号的点替换为下划线，例如：com.alubrain.devtoolbox.1_0_0
APP_USER_MODEL_ID = f"com.alubrain.devtoolbox.{APP_VERSION.replace('.', '_')}"
