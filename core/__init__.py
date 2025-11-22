# core/__init__.py
"""
系统工具箱核心模块
包含所有系统管理功能和小爱同学接口
"""

import os
import json
from typing import Dict, Any

from .logger import Logger
from .shutdown_tool import ShutdownTool
from .system_tool import SystemTool
from .remote_shutdown import RemoteShutdownTool
from .web_server import WebServer

# 不再在这里导入 core_manager，避免循环导入

__all__ = ['Logger', 'ShutdownTool', 'SystemTool', 'XiaoAiInterface', 'RemoteShutdownTool', 'WebServer']
__version__ = '2.2.0'
__author__ = '牧歌'


class XiaoAiInterface:
    """小爱同学接口类 - 预留扩展"""

    def __init__(self, logger: Logger = None):
        self.logger = logger or Logger()
        self.shutdown_tool = ShutdownTool(self.logger)
        self.system_tool = SystemTool(self.logger)
        self.remote_shutdown_tool = RemoteShutdownTool(self.logger)

    def execute_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行小爱同学命令
        Args:
            command: 命令类型 ('shutdown', 'system_info', 'clean_temp', etc.)
            params: 命令参数
        Returns:
            执行结果
        """
        params = params or {}

        try:
            if command == 'shutdown':
                hours = params.get('hours', 1.0)
                # 这里可以调用ShutdownTool的方法
                return {"success": True, "message": f"已设置{hours}小时后关机"}

            elif command == 'cancel_shutdown':
                return {"success": True, "message": "已取消关机计划"}

            elif command == 'system_info':
                # 获取系统信息
                return {"success": True, "data": "系统信息获取成功"}

            elif command == 'clean_temp':
                # 清理临时文件
                return {"success": True, "message": "临时文件清理完成"}

            elif command == 'remote_shutdown':
                # 远程关机命令
                return {"success": True, "message": "远程关机服务状态查询"}

            else:
                return {"success": False, "message": f"未知命令: {command}"}

        except Exception as e:
            self.logger.log(f"小爱命令执行失败: {str(e)}", 'error')
            return {"success": False, "message": f"执行失败: {str(e)}"}


def create_xiaoai_interface() -> XiaoAiInterface:
    """创建小爱同学接口实例"""
    return XiaoAiInterface()


# 包版本信息
def get_package_info() -> Dict[str, str]:
    """返回包信息"""
    return {
        "name": "SystemToolbox Core",
        "version": __version__,
        "author": __author__,
        "description": "系统工具箱核心模块，支持小爱同学接口、远程关机和工具间联动"
    }