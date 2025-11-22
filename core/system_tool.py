import os
import subprocess
import psutil
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGroupBox, QMessageBox, QTextEdit,
                             QScrollArea, QProgressBar)
from PyQt5.QtCore import QThread, pyqtSignal, Qt


class SystemTool:
    def __init__(self, logger):
        self.logger = logger

    def create_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 标题
        title = QLabel("系统维护工具")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 创建功能按钮组
        self.create_clean_group(layout)
        self.create_diagnostic_group(layout)
        self.create_info_group(layout)

        layout.addStretch()
        return widget

    def create_clean_group(self, layout):
        group = QGroupBox("系统清理")
        group.setObjectName("functionGroup")
        group_layout = QVBoxLayout(group)

        # 清理按钮
        clean_btn = QPushButton("清理临时文件")
        clean_btn.setObjectName("actionButton")
        clean_btn.clicked.connect(self.clean_temp_files)

        group_layout.addWidget(clean_btn)
        layout.addWidget(group)

    def create_diagnostic_group(self, layout):
        group = QGroupBox("系统诊断")
        group.setObjectName("functionGroup")
        group_layout = QVBoxLayout(group)

        # 诊断按钮布局
        btn_layout1 = QHBoxLayout()
        btn_layout2 = QHBoxLayout()

        disk_btn = QPushButton("磁盘检查")
        network_btn = QPushButton("网络诊断")
        process_btn = QPushButton("进程管理")
        info_btn = QPushButton("系统信息")

        for btn in [disk_btn, network_btn, process_btn, info_btn]:
            btn.setObjectName("actionButton")

        disk_btn.clicked.connect(self.check_disk)
        network_btn.clicked.connect(self.network_diagnose)
        process_btn.clicked.connect(self.manage_process)
        info_btn.clicked.connect(self.show_system_info)

        btn_layout1.addWidget(disk_btn)
        btn_layout1.addWidget(network_btn)
        btn_layout2.addWidget(process_btn)
        btn_layout2.addWidget(info_btn)

        group_layout.addLayout(btn_layout1)
        group_layout.addLayout(btn_layout2)
        layout.addWidget(group)

    def create_info_group(self, layout):
        group = QGroupBox("系统状态")
        group.setObjectName("functionGroup")
        group_layout = QVBoxLayout(group)

        self.status_display = QTextEdit()
        self.status_display.setMaximumHeight(150)
        self.status_display.setReadOnly(True)

        refresh_btn = QPushButton("刷新状态")
        refresh_btn.clicked.connect(self.update_system_status)

        group_layout.addWidget(self.status_display)
        group_layout.addWidget(refresh_btn)
        layout.addWidget(group)

        # 初始更新状态
        self.update_system_status()

    def clean_temp_files(self):
        self.logger.log("开始清理临时文件...")

        try:
            # 清理临时文件
            temp_dirs = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Temp'),
                os.path.join(os.environ.get('USERPROFILE', ''), 'Recent')
            ]

            cleaned_count = 0
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            try:
                                file_path = os.path.join(root, file)
                                os.remove(file_path)
                                cleaned_count += 1
                            except:
                                pass

            self.logger.log(f"临时文件清理完成，共清理 {cleaned_count} 个文件")
            QMessageBox.information(None, "完成", "临时文件清理完成！")

        except Exception as e:
            self.logger.log(f"清理临时文件失败: {str(e)}", 'error')
            QMessageBox.critical(None, "错误", f"清理失败: {str(e)}")

    def check_disk(self):
        self.logger.log("开始磁盘检查...")

        try:
            result = subprocess.run('chkdsk', shell=True,
                                    capture_output=True, text=True)
            self.logger.log("磁盘检查完成")
            QMessageBox.information(None, "完成", "磁盘检查已完成！")
        except Exception as e:
            self.logger.log(f"磁盘检查失败: {str(e)}", 'error')

    def network_diagnose(self):
        self.logger.log("开始网络诊断...")

        try:
            # 获取IP信息
            result = subprocess.run('ipconfig', shell=True,
                                    capture_output=True, text=True, encoding='gbk')

            # 测试网络连接
            ping_result = subprocess.run('ping 8.8.8.8 -n 2', shell=True,
                                         capture_output=True, text=True)

            network_status = "网络连接: 成功" if ping_result.returncode == 0 else "网络连接: 失败"

            self.logger.log(network_status)
            QMessageBox.information(None, "网络诊断", network_status)

        except Exception as e:
            self.logger.log(f"网络诊断失败: {str(e)}", 'error')

    def manage_process(self):
        self.logger.log("打开进程管理器...")

        try:
            subprocess.Popen('taskmgr')
            self.logger.log("进程管理器已打开")
        except Exception as e:
            self.logger.log(f"打开进程管理器失败: {str(e)}", 'error')

    def show_system_info(self):
        self.logger.log("获取系统信息...")

        try:
            # 使用systeminfo命令获取系统信息
            result = subprocess.run('systeminfo', shell=True,
                                    capture_output=True, text=True, encoding='gbk')

            if result.returncode == 0:
                info_lines = result.stdout.split('\n')[:20]  # 只显示前20行
                info_text = '\n'.join(info_lines)

                self.logger.log("系统信息获取成功")

                # 显示在信息框
                msg_box = QMessageBox()
                msg_box.setWindowTitle("系统信息")
                msg_box.setText(info_text)
                msg_box.exec_()

        except Exception as e:
            self.logger.log(f"获取系统信息失败: {str(e)}", 'error')

    def update_system_status(self):
        try:
            status_text = ""

            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            status_text += f"CPU使用率: {cpu_percent}%\n"

            # 内存使用
            memory = psutil.virtual_memory()
            status_text += f"内存使用: {memory.percent}% ({memory.used // 1024 // 1024}MB/{memory.total // 1024 // 1024}MB)\n"

            # 磁盘使用
            disk = psutil.disk_usage('/')
            status_text += f"磁盘使用: {disk.percent}% ({disk.used // 1024 // 1024 // 1024}GB/{disk.total // 1024 // 1024 // 1024}GB)\n"

            self.status_display.setText(status_text)

        except Exception as e:
            self.status_display.setText(f"获取状态失败: {str(e)}")