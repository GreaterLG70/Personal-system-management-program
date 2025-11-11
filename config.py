"""
系统工具箱配置文件
配置各项系统参数、路径、语音助手设置等

作者: 牧歌
版本: 1.0.0
日期: 2025.11.5
"""

import os
import platform
from pathlib import Path


# ==================== 基础配置 ====================
class BaseConfig:
    """基础配置类"""

    # 程序信息
    APP_NAME = "系统工具箱"
    APP_VERSION = "1.0.0"
    AUTHOR = "牧歌"
    COPYRIGHT_YEAR = "2025"

    # 日志配置
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE = "logs/system_toolbox.log"
    MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5

    # 语言设置
    LANGUAGE = "zh-CN"  # zh-CN, en-US


# ==================== 路径配置 ====================
class PathConfig:
    """路径配置类"""

    # 基础路径
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    TEMP_DIR = BASE_DIR / "temp"

    # 系统路径
    if platform.system() == "Windows":
        SYSTEM_TEMP = Path(os.environ.get('TEMP', 'C:\\Windows\\Temp'))
        USER_TEMP = Path(os.environ.get('TEMP', ''))
        USER_PROFILE = Path(os.environ.get('USERPROFILE', ''))
    else:
        SYSTEM_TEMP = Path("/tmp")
        USER_TEMP = Path("/tmp")
        USER_PROFILE = Path.home()

    # 创建必要的目录
    @classmethod
    def create_directories(cls):
        """创建必要的目录结构"""
        directories = [
            cls.DATA_DIR,
            cls.LOGS_DIR,
            cls.TEMP_DIR
        ]

        for directory in directories:
            directory.mkdir(exist_ok=True, parents=True)


# ==================== 关机工具配置 ====================
class ShutdownConfig:
    """关机工具配置"""

    # 默认关机延迟时间（小时）
    DEFAULT_SHUTDOWN_DELAY = 1.0

    # 最大关机延迟时间（小时）
    MAX_SHUTDOWN_DELAY = 24.0

    # 最小关机延迟时间（小时）
    MIN_SHUTDOWN_DELAY = 0.1

    # 关机前警告时间（秒）
    WARNING_TIME = 300  # 5分钟

    # 关机命令（Windows）
    if platform.system() == "Windows":
        SHUTDOWN_CMD = "shutdown /s /f /t {seconds}"
        CANCEL_SHUTDOWN_CMD = "shutdown /a"
    else:
        # Linux/Mac 关机命令
        SHUTDOWN_CMD = "shutdown -h +{minutes}"
        CANCEL_SHUTDOWN_CMD = "shutdown -c"


# ==================== 系统工具配置 ====================
class SystemToolsConfig:
    """系统工具配置"""

    # 临时文件清理配置
    TEMP_FILE_PATTERNS = [
        "*.tmp",
        "*.temp",
        "*.log",
        "*.cache",
        "*.chk",
        "*.dmp"
    ]

    TEMP_DIRECTORIES = [
        PathConfig.SYSTEM_TEMP,
        PathConfig.USER_TEMP,
        PathConfig.USER_PROFILE / "AppData" / "Local" / "Temp"
    ]

    # 进程管理配置
    MAX_PROCESS_DISPLAY = 15
    ADMIN_REQUIRED_PROCESSES = ["csrss.exe", "winlogon.exe", "services.exe"]

    # 网络诊断配置
    NETWORK_TEST_HOSTS = [
        "8.8.8.8",  # Google DNS
        "114.114.114.114",  # 国内DNS
        "www.baidu.com",  # 百度
        "www.qq.com"  # 腾讯
    ]

    NETWORK_TIMEOUT = 5  # 秒


# ==================== 语音助手配置 ====================
class VoiceConfig:
    """语音助手配置"""

    # 小爱助手集成
    XIAOMI_API_ENABLED = False  # 默认禁用，需要用户手动开启
    XIAOMI_API_URL = "http://localhost:8000/xiaomi/command"
    XIAOMI_API_TIMEOUT = 10

    # 支持的语音命令
    VOICE_COMMANDS = {
        "关机": "shutdown",
        "取消关机": "cancel_shutdown",
        "清理垃圾": "clean_temp",
        "系统信息": "system_info",
        "网络检查": "network_check"
    }

    # 语音响应配置
    RESPONSE_TIMEOUT = 30
    MAX_RESPONSE_LENGTH = 500


# ==================== 界面配置 ====================
class UIConfig:
    """界面配置"""

    # 控制台颜色配置 (Windows)
    COLOR_SUCCESS = "0a"  # 绿底黑字
    COLOR_ERROR = "0c"  # 红底黑字
    COLOR_WARNING = "0e"  # 黄底黑字
    COLOR_INFO = "0b"  # 青底黑字

    # 界面显示配置
    TERMINAL_WIDTH = 80
    SHOW_HEADER = True
    SHOW_FOOTER = True

    # 动画效果
    ENABLE_ANIMATIONS = True
    ANIMATION_SPEED = 0.5  # 秒


# ==================== 安全配置 ====================
class SecurityConfig:
    """安全配置"""

    # 管理员权限要求
    REQUIRE_ADMIN_FOR = [
        "disk_check",
        "system_restore",
        "firewall_management"
    ]

    # 危险操作确认
    CONFIRM_DANGEROUS_ACTIONS = True
    DANGEROUS_ACTIONS = [
        "shutdown",
        "process_kill",
        "registry_edit"
    ]

    # 日志敏感信息过滤
    FILTER_SENSITIVE_INFO = True
    SENSITIVE_PATTERNS = [
        "password",
        "api_key",
        "token",
        "secret"
    ]


# ==================== 开发配置 ====================
class DevelopmentConfig:
    """开发配置"""

    # 调试模式
    DEBUG = False

    # 测试模式
    TESTING = False

    # 开发工具
    ENABLE_PROFILING = False
    ENABLE_METRICS = False

    # 热重载
    ENABLE_HOT_RELOAD = False


# ==================== 配置管理函数 ====================
def load_config():
    """加载配置文件"""
    # 这里可以添加从外部文件加载配置的逻辑
    # 目前使用硬编码配置
    return {
        "base": BaseConfig,
        "paths": PathConfig,
        "shutdown": ShutdownConfig,
        "system_tools": SystemToolsConfig,
        "voice": VoiceConfig,
        "ui": UIConfig,
        "security": SecurityConfig,
        "development": DevelopmentConfig
    }


def save_config():
    """保存配置到文件"""
    # 这里可以添加保存配置到外部文件的逻辑
    # 目前配置是硬编码的，所以这个函数暂时是空的
    pass


def validate_config():
    """验证配置有效性"""
    errors = []

    # 验证关机延迟时间
    if ShutdownConfig.MIN_SHUTDOWN_DELAY >= ShutdownConfig.MAX_SHUTDOWN_DELAY:
        errors.append("最小关机延迟时间不能大于等于最大延迟时间")

    # 验证路径
    if not PathConfig.BASE_DIR.exists():
        errors.append("基础路径不存在")

    return errors


# ==================== 初始化配置 ====================
# 创建必要的目录
PathConfig.create_directories()

# 验证配置
config_errors = validate_config()
if config_errors:
    print("配置错误:")
    for error in config_errors:
        print(f"  - {error}")

# ==================== 导出配置 ====================
# 为了方便使用，导出一个包含所有配置的字典
config = load_config()


# 提供一个便捷的配置访问函数
def get_config(section=None):
    """获取配置"""
    if section:
        return config.get(section)
    return config


# 提供配置信息摘要
def config_summary():
    """获取配置摘要"""
    summary = {
        "app_name": BaseConfig.APP_NAME,
        "version": BaseConfig.APP_VERSION,
        "author": BaseConfig.AUTHOR,
        "language": BaseConfig.LANGUAGE,
        "log_level": BaseConfig.LOG_LEVEL,
        "xiaomi_api_enabled": VoiceConfig.XIAOMI_API_ENABLED,
        "debug_mode": DevelopmentConfig.DEBUG
    }
    return summary


# 程序启动时打印配置摘要（调试模式下）
if DevelopmentConfig.DEBUG:
    print("配置加载完成:")
    for key, value in config_summary().items():
        print(f"  {key}: {value}")