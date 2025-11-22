import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QTextEdit, QStackedWidget,
                             QFrame, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QIcon, QFont


class MainWindow(QMainWindow):
    # 定义信号
    log_signal = pyqtSignal(str)

    def __init__(self, logger, xiaoai_interface, resource_path_func=None):
        super().__init__()
        self.logger = logger
        self.xiaoai_interface = xiaoai_interface
        self.resource_path = resource_path_func or (lambda x: x)  # 默认返回原路径

        # 初始化功能模块为None
        self.shutdown_tool = None
        self.system_tool = None
        self.remote_shutdown_tool = None
        self.shutdown_page = None
        self.system_page = None
        self.remote_shutdown_page = None

        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        self.setWindowTitle("PRTS - 牧歌")
        # 再次增大窗口大小约10% - 从 1320x880 增加到 1452x968
        self.setGeometry(100, 100, 1800, 1064)
        self.setMinimumSize(1210, 847)  # 相应增大最小尺寸

        # 设置窗口图标
        icon_path = self.resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            # 如果打包后的路径不存在，尝试原始路径
            original_icon_path = "E:\\Auto\\SystemToolbox_V4\\icon.ico"
            if os.path.exists(original_icon_path):
                self.setWindowIcon(QIcon(original_icon_path))
            else:
                self.logger.log(f"图标文件未找到: {icon_path}", 'warning')

        # 设置背景图片 - 使用 resource_path
        background_path = self.resource_path("prts.jpg")
        if os.path.exists(background_path):
            self.set_background(background_path)
        else:
            # 如果打包后的路径不存在，尝试原始路径
            original_background_path = "E:\\Auto\\SystemToolboxV3\\prts.jpg"
            if os.path.exists(original_background_path):
                self.set_background(original_background_path)
            else:
                self.logger.log(f"背景图片不存在: {background_path}", 'warning')

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)  # 增加边距让背景更可见
        main_layout.setSpacing(40)  # 增加间距

        # 左侧功能面板 - 移除边框和背景
        self.create_left_panel(main_layout)

        # 右侧信息面板 - 移除边框和背景
        self.create_right_panel(main_layout)

        # 延迟初始化功能模块，确保UI先创建完成
        from core.shutdown_tool import ShutdownTool
        from core.system_tool import SystemTool
        from core.remote_shutdown import RemoteShutdownTool

        try:
            self.shutdown_tool = ShutdownTool(self.logger)
            self.system_tool = SystemTool(self.logger)
            self.remote_shutdown_tool = RemoteShutdownTool(self.logger)

            # 创建功能页面
            self.shutdown_page = self.shutdown_tool.create_page()
            self.system_page = self.system_tool.create_page()
            self.remote_shutdown_page = self.remote_shutdown_tool.create_page()

            # 添加到堆叠窗口
            self.stacked_widget.addWidget(self.shutdown_page)
            self.stacked_widget.addWidget(self.system_page)
            self.stacked_widget.addWidget(self.remote_shutdown_page)

            self.logger.log("功能模块初始化成功")
        except Exception as e:
            self.logger.log(f"功能模块初始化失败: {str(e)}", 'error')
            # 创建错误页面作为备用
            self.create_error_pages()

        # 设置默认页面
        self.show_welcome_page()

    def set_background(self, image_path):
        """设置背景图片"""
        try:
            palette = QPalette()
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                palette.setBrush(QPalette.Window, QBrush(pixmap.scaled(
                    self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
                self.setPalette(palette)
            else:
                self.logger.log(f"无法加载背景图片: {image_path}", 'warning')
        except Exception as e:
            self.logger.log(f"设置背景失败: {str(e)}", 'warning')

    def create_left_panel(self, main_layout):
        # 左侧面板容器 - 完全透明，无边框
        left_widget = QWidget()
        left_widget.setMaximumWidth(400)  # 增大宽度

        left_layout = QVBoxLayout(left_widget)
        left_layout.setAlignment(Qt.AlignTop)

        # 标题 - 使用更大的字体和更好的样式
        title = QLabel("P  R  T  S v1.2")
        title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 32px;
                font-weight: bold;
                padding: 20px;
                background-color: rgba(0, 0, 0, 0.5);
                border-radius: 15px;
            }
        """)
        title.setAlignment(Qt.AlignCenter)

        # 功能按钮 - 使用更美观的样式
        self.btn_shutdown = self.create_menu_button("定时关机")
        self.btn_system = self.create_menu_button("系统维护")
        self.btn_remote_shutdown = self.create_menu_button("远程关机")
        self.btn_exit = self.create_menu_button("再见")

        # 添加到布局
        left_layout.addWidget(title)
        left_layout.addSpacing(40)
        left_layout.addWidget(self.btn_shutdown)
        left_layout.addWidget(self.btn_system)
        left_layout.addWidget(self.btn_remote_shutdown)
        left_layout.addStretch()
        left_layout.addWidget(self.btn_exit)

        # 底部信息
        bottom_label = QLabel("牧歌 2025.11.5")
        bottom_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 14px;
                padding: 10px;
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 8px;
            }
        """)
        bottom_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(bottom_label)

        main_layout.addWidget(left_widget)

    def create_right_panel(self, main_layout):
        # 右侧面板容器 - 完全透明，无边框
        right_widget = QWidget()

        right_layout = QVBoxLayout(right_widget)

        # 内容堆叠窗口
        self.stacked_widget = QStackedWidget()

        # 欢迎页面
        self.welcome_page = self.create_welcome_page()
        self.stacked_widget.addWidget(self.welcome_page)

        # 信息显示区域
        info_label = QLabel("执行信息:")
        info_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 5px;
            }
        """)

        self.info_display = QTextEdit()
        self.info_display.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 0.7);
                color: #00ff00;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)
        self.info_display.setReadOnly(True)
        self.info_display.setMaximumHeight(250)  # 增加高度

        right_layout.addWidget(self.stacked_widget)
        right_layout.addWidget(info_label)
        right_layout.addWidget(self.info_display)

        main_layout.addWidget(right_widget)

    def create_menu_button(self, text):
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(41, 128, 185, 0.9);
                color: white;
                border: 2px solid rgba(52, 152, 219, 0.9);
                border-radius: 10px;
                padding: 20px;
                font-size: 18px;
                font-weight: bold;
                margin: 8px;
            }
            QPushButton:hover {
                background-color: rgba(52, 152, 219, 0.9);
                border: 2px solid rgba(52, 152, 219, 1);
            }
            QPushButton:pressed {
                background-color: rgba(41, 128, 185, 1);
            }
        """)
        btn.setMinimumHeight(70)  # 增加按钮高度
        return btn

    def create_welcome_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        welcome_label = QLabel("我一直在你身边")
        welcome_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 48px;
                font-weight: bold;
                padding: 40px;
                background-color: rgba(0, 0, 0, 0.5);
                border-radius: 25px;
            }
        """)
        welcome_label.setAlignment(Qt.AlignCenter)

        layout.addStretch()
        layout.addWidget(welcome_label)
        layout.addStretch()

        return widget

    def create_error_pages(self):
        """创建错误页面作为备用"""
        # 关机工具错误页面
        error_shutdown_widget = QWidget()
        layout = QVBoxLayout(error_shutdown_widget)
        error_label = QLabel("定时关机初始化失败")
        error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(error_label)
        self.shutdown_page = error_shutdown_widget
        self.stacked_widget.addWidget(self.shutdown_page)

        # 系统工具错误页面
        error_system_widget = QWidget()
        layout = QVBoxLayout(error_system_widget)
        error_label = QLabel("系统维护初始化失败")
        error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(error_label)
        self.system_page = error_system_widget
        self.stacked_widget.addWidget(self.system_page)

        # 远程关机工具错误页面
        error_remote_shutdown_widget = QWidget()
        layout = QVBoxLayout(error_remote_shutdown_widget)
        error_label = QLabel("远程关机初始化失败")
        error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(error_label)
        self.remote_shutdown_page = error_remote_shutdown_widget
        self.stacked_widget.addWidget(self.remote_shutdown_page)

    def setup_connections(self):
        self.btn_shutdown.clicked.connect(self.show_shutdown_page)
        self.btn_system.clicked.connect(self.show_system_page)
        self.btn_remote_shutdown.clicked.connect(self.show_remote_shutdown_page)
        self.btn_exit.clicked.connect(self.close)

        # 连接日志信号
        self.logger.log_signal.connect(self.update_info_display)

    def show_welcome_page(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_shutdown_page(self):
        if self.shutdown_page:
            index = self.stacked_widget.indexOf(self.shutdown_page)
            self.stacked_widget.setCurrentIndex(index)
            self.logger.log("进入定时关机")
        else:
            self.logger.log("定时关机不可用", 'error')

    def show_system_page(self):
        if self.system_page:
            index = self.stacked_widget.indexOf(self.system_page)
            self.stacked_widget.setCurrentIndex(index)
            self.logger.log("进入系统维护")
        else:
            self.logger.log("系统维护不可用", 'error')

    def show_remote_shutdown_page(self):
        """显示远程关机页面"""
        if self.remote_shutdown_page:
            index = self.stacked_widget.indexOf(self.remote_shutdown_page)
            self.stacked_widget.setCurrentIndex(index)
            self.logger.log("进入远程关机")
        else:
            self.logger.log("远程关机不可用", 'error')

    def update_info_display(self, message):
        self.info_display.append(f"{message}")
        # 自动滚动到底部
        scrollbar = self.info_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def resizeEvent(self, event):
        # 窗口大小改变时更新背景
        background_path = self.resource_path("prts.jpg")
        if os.path.exists(background_path):
            self.set_background(background_path)
        super().resizeEvent(event)