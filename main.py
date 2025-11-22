import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QBrush, QPixmap, QIcon

# 添加当前目录到Python路径，确保可以导入core模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui_main import MainWindow
from core import Logger, ShutdownTool, SystemTool, create_xiaoai_interface, get_package_info


def resource_path(relative_path):
    """获取资源的绝对路径。在开发环境和打包后都能正常工作"""
    try:
        # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    # 处理嵌套路径
    if relative_path.startswith('styles/'):
        # 对于样式文件，保持目录结构
        return os.path.join(base_path, relative_path)
    else:
        # 对于根目录文件，直接返回
        return os.path.join(base_path, relative_path)


class SystemToolboxApp:
    def __init__(self):
        self.app = None
        self.window = None
        self.logger = None
        self.xiaoai_interface = None

    def initialize(self):
        """初始化应用程序"""
        try:
            # 创建必要的目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            logs_dir = os.path.join(current_dir, 'logs')
            config_dir = os.path.join(current_dir, 'config')

            os.makedirs(logs_dir, exist_ok=True)
            os.makedirs(config_dir, exist_ok=True)

            # 创建Qt应用
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("P  R  T  S")
            self.app.setApplicationVersion("1.2.1")

            # 设置应用程序图标
            icon_path = resource_path("icon.ico")
            if os.path.exists(icon_path):
                self.app.setWindowIcon(QIcon(icon_path))
            else:
                # 如果找不到图标，使用默认图标或跳过
                print(f"警告: 图标文件未找到: {icon_path}")

            # 初始化核心组件
            self.logger = Logger()
            self.xiaoai_interface = create_xiaoai_interface()

            # 显示启动信息
            package_info = get_package_info()
            self.logger.log(f"启动 {package_info['name']} v{package_info['version']}")

            # 创建主窗口，传递资源路径函数
            self.window = MainWindow(self.logger, self.xiaoai_interface, resource_path)
            self.window.show()

            return True

        except Exception as e:
            self.show_error_message(f"应用程序初始化失败: {str(e)}")
            return False

    def show_error_message(self, message):
        """显示错误消息"""
        try:
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "启动错误", message)
        except:
            print(f"错误: {message}")

    def run(self):
        """运行应用程序"""
        if self.initialize():
            # 设置退出处理
            self.app.aboutToQuit.connect(self.cleanup)

            # 运行应用
            return self.app.exec_()
        else:
            return 1

    def cleanup(self):
        """清理资源"""
        if self.logger:
            self.logger.log("应用程序退出")


def main():
    """主函数"""
    app = SystemToolboxApp()
    sys.exit(app.run())


if __name__ == '__main__':
    main()