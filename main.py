import os
import sys
import time
from modules import ShutdownTool, SystemTools


class SystemToolbox:
    def __init__(self):
        self.shutdown_tool = ShutdownTool()
        self.system_tools = SystemTools()

    def clear_screen(self):
        """更可靠的清屏方法"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_header(self, title):
        print("=" * 40)
        print(f"          {title}")
        print("=" * 40)

    def main_menu(self):
        while True:
            self.clear_screen()
            self.display_header("系统工具箱 v1.0")
            print("1. 定时关机工具")
            print("2. 系统维护工具")
            print("3. 退出程序")
            print("          --------牧歌2025.11.5")
            print("=" * 40)

            try:
                choice = input("请选择操作 (1-3): ").strip()

                if choice == '1':
                    self.shutdown_menu()
                elif choice == '2':
                    self.system_maintenance_menu()
                elif choice == '3':
                    self.exit_program()
                else:
                    print("无效选择，请重新输入！")
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n检测到中断信号，退出程序...")
                self.exit_program()
            except Exception as e:
                print(f"发生错误: {e}")
                time.sleep(2)

    def shutdown_menu(self):
        """定时关机菜单"""
        self.shutdown_tool.run_menu()

    def system_maintenance_menu(self):
        """系统维护菜单"""
        self.system_tools.run_menu()

    def exit_program(self):
        self.clear_screen()
        print("=" * 40)
        print("          感谢使用！")
        print("=" * 40)
        print("\n系统工具箱 - 牧歌")
        print("版本：1.0")
        print("日期：2025.11.5")
        print("\n3秒后自动退出...")
        time.sleep(3)
        sys.exit(0)


if __name__ == "__main__":
    toolbox = SystemToolbox()
    toolbox.main_menu()