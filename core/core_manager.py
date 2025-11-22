# core/core_manager.py
"""
工具箱核心管理模块，用于工具间通信
"""


class ToolboxCore:
    """工具箱核心管理类，用于工具间通信"""

    def __init__(self):
        self.shutdown_tool = None
        self.remote_shutdown_tool = None
        self._shutdown_callbacks = []
        self._shutdown_cancelled_callbacks = []  # 新增：取消关机回调列表

    def register_shutdown_tool(self, tool):
        """注册关机工具"""
        self.shutdown_tool = tool

    def register_remote_shutdown_tool(self, tool):
        """注册远程关机工具"""
        self.remote_shutdown_tool = tool

    def add_shutdown_callback(self, callback):
        """添加关机回调函数"""
        self._shutdown_callbacks.append(callback)

    def add_shutdown_cancelled_callback(self, callback):
        """添加取消关机回调函数"""
        self._shutdown_cancelled_callbacks.append(callback)

    def notify_shutdown_started(self, seconds, source="remote"):
        """通知关机开始"""
        for callback in self._shutdown_callbacks:
            try:
                callback(seconds, source)
            except Exception as e:
                print(f"关机回调执行失败: {e}")

    def notify_shutdown_cancelled(self, source="local"):
        """通知关机取消"""
        for callback in self._shutdown_cancelled_callbacks:
            try:
                callback(source)
            except Exception as e:
                print(f"取消关机回调执行失败: {e}")


# 创建全局核心实例
core = ToolboxCore()