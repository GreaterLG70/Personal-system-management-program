# core/shutdown_tool.py
import os
import subprocess
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QGroupBox, QMessageBox,
                             QFrame, QProgressBar)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QDoubleValidator


# 延迟导入核心模块，避免循环导入
def get_core():
    from .core_manager import core
    return core


class ShutdownTool:
    def __init__(self, logger):
        self.logger = logger
        self.shutdown_timer = QTimer()
        self.shutdown_timer.timeout.connect(self.execute_shutdown)
        self.remaining_seconds = 0

        # 延迟注册到核心
        def register_to_core():
            core = get_core()
            core.register_shutdown_tool(self)
            core.add_shutdown_callback(self.on_shutdown_started)
            core.add_shutdown_cancelled_callback(self.on_shutdown_cancelled)  # 新增：注册取消回调

        # 使用定时器延迟注册，确保核心模块已加载
        QTimer.singleShot(100, register_to_core)

    def create_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 标题
        title = QLabel("定时关机 v1.2")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 设置关机组
        shutdown_group = QGroupBox("设置定时关机")
        shutdown_group.setObjectName("functionGroup")
        shutdown_layout = QVBoxLayout(shutdown_group)

        # 时间输入
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("关机延迟时间:"))
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("请输入小时数（支持小数）")
        self.time_input.setValidator(QDoubleValidator(0.1, 8760.0, 2))
        time_layout.addWidget(self.time_input)
        time_layout.addWidget(QLabel("小时"))
        shutdown_layout.addLayout(time_layout)

        # 按钮布局
        btn_layout = QHBoxLayout()
        self.btn_set = QPushButton("设置关机计划")
        self.btn_cancel = QPushButton("取消关机计划")
        self.btn_set.setObjectName("actionButton")
        self.btn_cancel.setObjectName("cancelButton")

        btn_layout.addWidget(self.btn_set)
        btn_layout.addWidget(self.btn_cancel)
        shutdown_layout.addLayout(btn_layout)

        # 倒计时显示
        self.countdown_label = QLabel("当前无活动的关机计划")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setObjectName("countdownLabel")
        shutdown_layout.addWidget(self.countdown_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        shutdown_layout.addWidget(self.progress_bar)

        layout.addWidget(shutdown_group)
        layout.addStretch()

        # 连接信号
        self.btn_set.clicked.connect(self.set_shutdown)
        self.btn_cancel.clicked.connect(self.cancel_shutdown)

        # 倒计时定时器
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)

        return widget

    def set_shutdown(self):
        try:
            hours = float(self.time_input.text().strip())
            if hours <= 0:
                QMessageBox.warning(None, "错误", "时间必须大于0！")
                return

            seconds = int(hours * 3600)
            self.remaining_seconds = seconds

            # 执行关机命令
            result = subprocess.run(f'shutdown /s /f /t {seconds}',
                                    shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                self.logger.log(f"关机计划已设置: {hours} 小时后关机")

                # 启动倒计时显示
                self.start_countdown(seconds)

                # 通知其他工具
                core = get_core()
                core.notify_shutdown_started(seconds, "local")

                QMessageBox.information(None, "成功",
                                        f"关机计划已生效！\n{hours} 小时后系统将自动关机")
            else:
                QMessageBox.critical(None, "错误", "设置关机计划失败！")
                self.logger.log(f"设置关机失败: {result.stderr}", 'error')

        except ValueError:
            QMessageBox.warning(None, "错误", "请输入有效的数字！")
        except Exception as e:
            QMessageBox.critical(None, "错误", f"发生未知错误: {str(e)}")
            self.logger.log(f"设置关机异常: {str(e)}", 'error')

    def cancel_shutdown(self):
        result = subprocess.run('shutdown /a', shell=True,
                                capture_output=True, text=True)

        if result.returncode == 0:
            self.logger.log("关机计划已取消")
            self.stop_countdown()

            # 新增：通知其他工具关机已取消
            core = get_core()
            core.notify_shutdown_cancelled("local")

            QMessageBox.information(None, "成功", "关机计划已取消！")
        else:
            self.logger.log("没有活动的关机计划可取消")
            QMessageBox.information(None, "提示", "当前没有活动的关机计划")

    def start_countdown(self, seconds):
        self.remaining_seconds = seconds
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(seconds)
        self.progress_bar.setValue(seconds)
        self.countdown_timer.start(1000)  # 每秒更新

    def stop_countdown(self):
        self.countdown_timer.stop()
        self.countdown_label.setText("当前无活动的关机计划")
        self.progress_bar.setVisible(False)

    def update_countdown(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1

            hours = self.remaining_seconds // 3600
            minutes = (self.remaining_seconds % 3600) // 60
            seconds = self.remaining_seconds % 60

            countdown_text = (f"距离关机还有: {hours:02d}:{minutes:02d}:{seconds:02d}")
            self.countdown_label.setText(countdown_text)
            self.progress_bar.setValue(self.remaining_seconds)
        else:
            self.stop_countdown()

    def execute_shutdown(self):
        self.logger.log("执行自动关机")
        subprocess.run('shutdown /s /f /t 0', shell=True)

    def on_shutdown_started(self, seconds, source):
        """当其他工具启动关机时调用"""
        if source == "remote":
            # 远程关机指令，更新本地关机工具的显示
            self.start_countdown(seconds)
            self.logger.log(f"接收到远程关机指令，已同步显示倒计时: {seconds}秒")

    def on_shutdown_cancelled(self, source):
        """当其他工具取消关机时调用"""
        if source == "remote":
            # 远程取消关机指令，停止本地倒计时显示
            self.stop_countdown()
            self.logger.log("接收到远程取消关机指令，已停止倒计时显示")