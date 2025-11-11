#!/usr/bin/env python3
"""
系统工具箱启动脚本
如果GUI启动失败，会自动回退到命令行版本
"""

import sys
import os
import traceback


def main():
    try:
        # 尝试启动GUI版本
        from gui_main import main
        main()
    except Exception as e:
        print(f"GUI启动失败: {e}")
        print("正在切换到命令行版本...")

        try:
            # 回退到命令行版本
            from main import SystemToolbox
            toolbox = SystemToolbox()
            toolbox.main_menu()
        except Exception as e2:
            print(f"命令行版本也启动失败: {e2}")
            print("详细信息:")
            traceback.print_exc()
            input("按回车键退出...")


if __name__ == "__main__":
    main()