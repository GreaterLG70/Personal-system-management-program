import json
import time
import paho.mqtt.client as mqtt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGroupBox, QLineEdit, QTextEdit,
                             QMessageBox, QCheckBox, QProgressBar)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
import subprocess
import ssl
from .web_server import WebServer


# 延迟导入核心模块，避免循环导入
def get_core():
    from .core_manager import core
    return core


class MQTTClient(QThread):
    """MQTT客户端线程"""
    message_received = pyqtSignal(dict)
    status_changed = pyqtSignal(str)

    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.client = None
        self.is_connected = False
        self.config = {
            'broker': 'd596af16.ala.cn-hangzhou.emqxsl.cn',
            'port': 8883,
            'username': 'admin',
            'password': 'public',
            'topic': 'laptop/control',
            'will_topic': 'laptop/status',
            'will_message': '{"status": "control_offline"}'
        }

    def update_config(self, config):
        """更新MQTT配置"""
        self.config.update(config)

    def run(self):
        """启动MQTT客户端"""
        try:
            # 创建客户端，使用随机ID
            self.client = mqtt.Client(client_id=f"laptop_control_{int(time.time())}")

            # 设置遗嘱消息
            self.client.will_set(
                self.config['will_topic'],
                self.config['will_message'],
                qos=1,
                retain=True
            )

            # 设置TLS
            self.client.tls_set(cert_reqs=ssl.CERT_NONE)
            self.client.tls_insecure_set(True)  # 允许自签名证书

            # 设置认证
            self.client.username_pw_set(
                self.config['username'],
                self.config['password']
            )

            # 设置回调函数
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_disconnect = self.on_disconnect

            # 连接服务器
            self.logger.log(f"正在连接到MQTT服务器: {self.config['broker']}:{self.config['port']}")
            self.client.connect(
                self.config['broker'],
                self.config['port'],
                60
            )

            self.client.loop_forever()

        except Exception as e:
            self.status_changed.emit(f"连接失败: {str(e)}")
            self.logger.log(f"MQTT连接失败: {str(e)}", 'error')

    def on_connect(self, client, userdata, flags, rc):
        """连接回调"""
        if rc == 0:
            self.is_connected = True
            # 订阅控制主题
            client.subscribe(self.config['topic'], qos=1)

            # 发布上线状态
            client.publish(
                self.config['will_topic'],
                '{"status": "control_online"}',
                qos=1,
                retain=True
            )

            self.status_changed.emit("已连接")
            self.logger.log("MQTT连接成功，已订阅控制主题")
        else:
            error_codes = {
                1: "协议版本错误",
                2: "客户端标识符无效",
                3: "服务器不可用",
                4: "用户名或密码错误",
                5: "未授权"
            }
            error_msg = error_codes.get(rc, f"未知错误代码: {rc}")
            self.status_changed.emit(f"连接失败: {error_msg}")
            self.logger.log(f"MQTT连接失败: {error_msg}", 'error')

    def on_message(self, client, userdata, msg):
        """消息接收回调"""
        try:
            payload = msg.payload.decode('utf-8')
            message = json.loads(payload)
            self.message_received.emit(message)
            self.logger.log(f"收到MQTT消息: {payload}")
        except Exception as e:
            self.logger.log(f"MQTT消息解析失败: {str(e)}", 'error')

    def on_disconnect(self, client, userdata, rc):
        """断开连接回调"""
        self.is_connected = False
        if rc != 0:
            self.status_changed.emit("意外断开连接")
            self.logger.log("MQTT意外断开连接")
        else:
            self.status_changed.emit("已断开连接")
            self.logger.log("MQTT连接断开")

    def stop(self):
        """停止MQTT客户端"""
        if self.client and self.is_connected:
            # 发布离线状态
            self.client.publish(
                self.config['will_topic'],
                '{"status": "control_offline"}',
                qos=1,
                retain=True
            )
            self.client.disconnect()
            self.client.loop_stop()
        self.quit()


class RemoteShutdownTool:
    """远程关机工具"""

    def __init__(self, logger):
        self.logger = logger
        self.mqtt_client = MQTTClient(logger)
        self.web_server = WebServer(logger)

        # 倒计时相关变量
        self.shutdown_timer = QTimer()
        self.shutdown_timer.timeout.connect(self.execute_shutdown)
        self.remaining_seconds = 0
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)

        # UI元素占位符
        self.countdown_label = None
        self.progress_bar = None

        # 延迟注册到核心
        def register_to_core():
            core = get_core()
            core.register_remote_shutdown_tool(self)
            core.add_shutdown_cancelled_callback(self.on_shutdown_cancelled)  # 新增：注册取消回调

        # 使用定时器延迟注册，确保核心模块已加载
        QTimer.singleShot(100, register_to_core)

        self.setup_mqtt_handlers()
        self.setup_web_server_handlers()

    def setup_mqtt_handlers(self):
        """设置MQTT消息处理器"""
        self.mqtt_client.message_received.connect(self.handle_mqtt_message)
        self.mqtt_client.status_changed.connect(self.update_ui_status)

    def setup_web_server_handlers(self):
        """设置HTTP服务器处理器"""
        self.web_server.server_started.connect(self.on_web_server_started)
        self.web_server.server_stopped.connect(self.on_web_server_stopped)
        self.web_server.error_occurred.connect(self.on_web_server_error)

    def on_web_server_started(self, url):
        """HTTP服务器启动回调"""
        self.web_url = url
        self.log_message(f"网页服务已启动: {url}")
        # 自动打开浏览器
        self.web_server.open_browser(url)

    def on_web_server_stopped(self):
        """HTTP服务器停止回调"""
        self.log_message("网页服务已停止")

    def on_web_server_error(self, error):
        """HTTP服务器错误回调"""
        self.log_message(f"网页服务错误: {error}")

    def handle_mqtt_message(self, message):
        """处理MQTT消息"""
        try:
            command = message.get('command', '').lower()
            delay = message.get('delay', 0)  # 延迟时间（秒）
            token = message.get('token', '')
            reason = message.get('reason', '未知')

            # Token验证（可选，增加安全性）
            expected_token = "emqx_cloud_shutdown_2024"
            if token != expected_token:
                self.logger.log(f"Token验证失败，收到: {token}")
                self.send_response("error", "Token验证失败")
                return

            if command == 'shutdown':
                # 将秒转换为分钟
                delay_minutes = delay // 60
                self.execute_remote_shutdown(delay_minutes)
                self.send_response("shutdown", f"将在{delay}秒后关机 - {reason}")

                # 启动倒计时显示
                self.start_countdown(delay)

                # 通知其他工具
                core = get_core()
                core.notify_shutdown_started(delay, "remote")

            elif command == 'cancel':
                self.cancel_remote_shutdown()  # 这个函数现在会通知其他工具
                self.send_response("cancel", "关机计划已取消")


            elif command == 'restart':
                # 将秒转换为分钟
                delay_minutes = delay // 60
                self.execute_remote_restart(delay_minutes)
                self.send_response("restart", f"将在{delay}秒后重启 - {reason}")

                # 启动倒计时显示
                self.start_countdown(delay)

                # 通知其他工具
                core = get_core()
                core.notify_shutdown_started(delay, "remote")

            elif command == 'hibernate':
                self.execute_remote_hibernate()
                self.send_response("hibernate", f"系统进入休眠 - {reason}")

            elif command == 'status':
                self.send_system_status()

            else:
                self.logger.log(f"未知命令: {command}")
                self.send_response("error", f"未知命令: {command}")

        except Exception as e:
            self.logger.log(f"处理MQTT消息失败: {str(e)}", 'error')
            self.send_response("error", f"命令执行失败: {str(e)}")

    def execute_remote_shutdown(self, delay_minutes=0):
        """执行远程关机"""
        try:
            seconds = delay_minutes * 60
            if seconds == 0:
                subprocess.run('shutdown /s /f /t 0', shell=True)
            else:
                subprocess.run(f'shutdown /s /f /t {seconds}', shell=True)
            self.logger.log(f"远程关机命令执行: {delay_minutes}分钟后关机")

        except Exception as e:
            self.logger.log(f"远程关机失败: {str(e)}", 'error')
            raise e

    def execute_remote_restart(self, delay_minutes=0):
        """执行远程重启"""
        try:
            seconds = delay_minutes * 60
            if seconds == 0:
                subprocess.run('shutdown /r /f /t 0', shell=True)
            else:
                subprocess.run(f'shutdown /r /f /t {seconds}', shell=True)
            self.logger.log(f"远程重启命令执行: {delay_minutes}分钟后重启")

        except Exception as e:
            self.logger.log(f"远程重启失败: {str(e)}", 'error')
            raise e

    def execute_remote_hibernate(self):
        """执行远程休眠"""
        try:
            subprocess.run('shutdown /h /f', shell=True)
            self.logger.log("远程休眠命令执行")

        except Exception as e:
            self.logger.log(f"远程休眠失败: {str(e)}", 'error')
            raise e

    def cancel_remote_shutdown(self):
        """取消关机计划"""
        try:
            result = subprocess.run('shutdown /a', shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.log("远程取消关机命令执行成功")

                # 新增：通知其他工具关机已取消
                core = get_core()
                core.notify_shutdown_cancelled("remote")

                # 停止倒计时显示
                self.stop_countdown()
            else:
                self.logger.log("没有活动的关机计划可取消")

        except Exception as e:
            self.logger.log(f"取消关机失败: {str(e)}", 'error')
            raise e

    def send_system_status(self):
        """发送系统状态"""
        try:
            import psutil

            status = {
                'type': 'status_response',
                'online': True,
                'timestamp': time.time(),
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            }

            if self.mqtt_client.is_connected:
                self.mqtt_client.client.publish(
                    'laptop/status',
                    json.dumps(status),
                    qos=1
                )
                self.logger.log("系统状态已发送")

        except Exception as e:
            self.logger.log(f"发送系统状态失败: {str(e)}", 'error')

    def send_response(self, command, message):
        """发送命令响应"""
        try:
            response = {
                'type': 'command_response',
                'command': command,
                'message': message,
                'timestamp': time.time()
            }

            if self.mqtt_client.is_connected:
                self.mqtt_client.client.publish(
                    'laptop/response',
                    json.dumps(response),
                    qos=1
                )
                self.logger.log(f"命令响应已发送: {message}")

        except Exception as e:
            self.logger.log(f"发送命令响应失败: {str(e)}", 'error')

    def on_shutdown_cancelled(self, source):
        """当其他工具取消关机时调用"""
        if source == "local":
            # 本地关机工具取消了关机，停止远程关机工具的倒计时显示
            self.stop_countdown()
            self.logger.log("接收到本地取消关机指令，已停止倒计时显示")

    def start_countdown(self, seconds):
        """开始倒计时显示"""
        # 检查UI元素是否已初始化
        if self.countdown_label is None or self.progress_bar is None:
            return

        self.remaining_seconds = seconds
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(seconds)
        self.progress_bar.setValue(seconds)
        self.countdown_label.setText(f"距离关机还有: {self.format_time(seconds)}")
        self.countdown_timer.start(1000)  # 每秒更新

    def stop_countdown(self):
        """停止倒计时显示"""
        # 检查UI元素是否已初始化
        if self.countdown_label is None or self.progress_bar is None:
            return

        self.countdown_timer.stop()
        self.countdown_label.setText("当前无活动的关机计划")
        self.progress_bar.setVisible(False)

    def update_countdown(self):
        """更新倒计时显示"""
        # 检查UI元素是否已初始化
        if self.countdown_label is None or self.progress_bar is None:
            return

        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.countdown_label.setText(f"距离关机还有: {self.format_time(self.remaining_seconds)}")
            self.progress_bar.setValue(self.remaining_seconds)
        else:
            self.stop_countdown()

    def format_time(self, seconds):
        """格式化时间显示"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def execute_shutdown(self):
        """执行关机（用于定时器）"""
        self.logger.log("执行自动关机")
        subprocess.run('shutdown /s /f /t 0', shell=True)

    def create_page(self):
        """创建远程关机页面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 标题
        title = QLabel("远程关机工具 v2.3")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # MQTT配置组
        config_group = QGroupBox("MQTT服务器配置")
        config_group.setObjectName("functionGroup")
        config_layout = QVBoxLayout(config_group)

        # 服务器配置
        server_layout = QHBoxLayout()
        server_layout.addWidget(QLabel("服务器地址:"))
        self.broker_input = QLineEdit("d596af16.ala.cn-hangzhou.emqxsl.cn")
        self.broker_input.setPlaceholderText("MQTT服务器地址")
        server_layout.addWidget(self.broker_input)

        server_layout.addWidget(QLabel("端口:"))
        self.port_input = QLineEdit("8883")
        self.port_input.setPlaceholderText("端口号")
        server_layout.addWidget(self.port_input)
        config_layout.addLayout(server_layout)

        # 认证配置
        auth_layout = QHBoxLayout()
        auth_layout.addWidget(QLabel("用户名:"))
        self.username_input = QLineEdit("admin")
        self.username_input.setPlaceholderText("用户名")
        auth_layout.addWidget(self.username_input)

        auth_layout.addWidget(QLabel("密码:"))
        self.password_input = QLineEdit("public")
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        auth_layout.addWidget(self.password_input)
        config_layout.addLayout(auth_layout)

        # 主题配置
        topic_layout = QHBoxLayout()
        topic_layout.addWidget(QLabel("控制主题:"))
        self.topic_input = QLineEdit("laptop/control")
        self.topic_input.setPlaceholderText("接收控制命令的主题")
        topic_layout.addWidget(self.topic_input)

        topic_layout.addWidget(QLabel("状态主题:"))
        self.will_topic_input = QLineEdit("laptop/status")
        self.will_topic_input.setPlaceholderText("发布状态的主题")
        topic_layout.addWidget(self.will_topic_input)
        config_layout.addLayout(topic_layout)

        # Token配置
        token_layout = QHBoxLayout()
        token_layout.addWidget(QLabel("安全Token:"))
        self.token_input = QLineEdit("emqx_cloud_shutdown_2024")
        self.token_input.setPlaceholderText("用于验证命令的安全性Token")
        token_layout.addWidget(self.token_input)
        config_layout.addLayout(token_layout)

        # 连接按钮
        btn_layout = QHBoxLayout()
        self.connect_btn = QPushButton("启动远程服务")
        self.disconnect_btn = QPushButton("停止远程服务")
        self.connect_btn.setObjectName("actionButton")
        self.disconnect_btn.setObjectName("cancelButton")
        self.disconnect_btn.setEnabled(False)

        btn_layout.addWidget(self.connect_btn)
        btn_layout.addWidget(self.disconnect_btn)
        config_layout.addLayout(btn_layout)

        layout.addWidget(config_group)

        # 网页服务组
        web_group = QGroupBox("网页控制服务")
        web_group.setObjectName("functionGroup")
        web_layout = QVBoxLayout(web_group)

        web_btn_layout = QHBoxLayout()
        self.web_status_label = QLabel("网页服务: 未启动")
        self.open_browser_btn = QPushButton("打开控制页面")
        self.open_browser_btn.clicked.connect(self.open_web_browser)
        self.open_browser_btn.setEnabled(False)

        web_btn_layout.addWidget(self.web_status_label)
        web_btn_layout.addWidget(self.open_browser_btn)
        web_layout.addLayout(web_btn_layout)

        layout.addWidget(web_group)

        # 关机倒计时组 - 保留进度条显示
        countdown_group = QGroupBox("关机倒计时")
        countdown_group.setObjectName("functionGroup")
        countdown_layout = QVBoxLayout(countdown_group)

        # 倒计时显示
        self.countdown_label = QLabel("当前无活动的关机计划")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setObjectName("countdownLabel")
        countdown_layout.addWidget(self.countdown_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        countdown_layout.addWidget(self.progress_bar)

        layout.addWidget(countdown_group)

        # 状态显示组
        status_group = QGroupBox("服务状态")
        status_group.setObjectName("functionGroup")
        status_layout = QVBoxLayout(status_group)

        self.status_label = QLabel("服务未启动")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: rgba(255, 0, 0, 0.3);
                border-radius: 5px;
                color: white;
                font-weight: bold;
            }
        """)
        status_layout.addWidget(self.status_label)

        # 消息日志
        self.message_log = QTextEdit()
        self.message_log.setMaximumHeight(200)
        self.message_log.setReadOnly(True)
        self.message_log.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 0.7);
                color: #00ff00;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                padding: 5px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
            }
        """)
        status_layout.addWidget(QLabel("消息日志:"))
        status_layout.addWidget(self.message_log)

        layout.addWidget(status_group)

        # 测试命令组 - 只保留必要的测试按钮
        test_group = QGroupBox("功能测试")
        test_group.setObjectName("functionGroup")
        test_layout = QHBoxLayout(test_group)

        test_cancel_btn = QPushButton("测试取消")
        test_status_btn = QPushButton("测试状态")

        test_cancel_btn.clicked.connect(self.cancel_remote_shutdown)
        test_status_btn.clicked.connect(self.send_system_status)

        test_layout.addWidget(test_cancel_btn)
        test_layout.addWidget(test_status_btn)

        layout.addWidget(test_group)

        # 使用说明
        help_group = QGroupBox("使用说明")
        help_group.setObjectName("functionGroup")
        help_layout = QVBoxLayout(help_group)

        help_text = QLabel(
            "1. 启动服务后，电脑会连接到MQTT服务器并订阅控制主题\n"
            "2. 同时会自动启动网页服务器，在浏览器中打开控制页面\n"
            "3. 通过网页向 'laptop/control' 主题发送JSON命令\n"
            "4. 支持的命令: shutdown(关机), restart(重启), cancel(取消), hibernate(休眠), status(状态)\n"
            "5. 网页端可以自定义关机时间\n"
            "6. 关机/重启命令会显示倒计时进度条，并与定时关机工具同步\n"
            "7. 电脑状态会发布到 'laptop/status' 主题\n"
            "8. 命令响应会发布到 'laptop/response' 主题\n"
            "9. 所有命令需要包含正确的token进行验证"
        )
        help_text.setStyleSheet("color: white; font-size: 12px;")
        help_layout.addWidget(help_text)

        layout.addWidget(help_group)
        layout.addStretch()

        # 连接信号
        self.connect_btn.clicked.connect(self.start_mqtt_service)
        self.disconnect_btn.clicked.connect(self.stop_mqtt_service)

        return widget

    def start_mqtt_service(self):
        """启动MQTT服务"""
        try:
            config = {
                'broker': self.broker_input.text().strip(),
                'port': int(self.port_input.text().strip()),
                'username': self.username_input.text().strip(),
                'password': self.password_input.text().strip(),
                'topic': self.topic_input.text().strip(),
                'will_topic': self.will_topic_input.text().strip(),
                'will_message': '{"status": "control_offline"}'
            }

            # 验证必填字段
            if not all([config['broker'], config['username'], config['password']]):
                QMessageBox.warning(None, "警告", "请填写服务器地址、用户名和密码")
                return

            self.mqtt_client.update_config(config)
            self.mqtt_client.start()

            # 启动HTTP服务器
            if self.web_server.start_server():
                self.web_status_label.setText("网页服务: 启动中...")
                self.open_browser_btn.setEnabled(False)

            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)

            # 更新状态标签样式
            self.status_label.setStyleSheet("""
                QLabel {
                    padding: 10px;
                    background-color: rgba(0, 255, 0, 0.3);
                    border-radius: 5px;
                    color: white;
                    font-weight: bold;
                }
            """)

            self.log_message("正在启动远程服务...")
            self.logger.log("远程关机服务启动中...")

        except Exception as e:
            QMessageBox.critical(None, "错误", f"启动服务失败: {str(e)}")
            self.logger.log(f"启动远程关机服务失败: {str(e)}", 'error')

    def stop_mqtt_service(self):
        """停止MQTT服务"""
        self.mqtt_client.stop()
        self.web_server.stop_server()

        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.open_browser_btn.setEnabled(False)

        # 更新状态标签样式
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: rgba(255, 0, 0, 0.3);
                border-radius: 5px;
                color: white;
                font-weight: bold;
            }
        """)

        self.status_label.setText("服务未启动")
        self.web_status_label.setText("网页服务: 未启动")
        self.log_message("远程服务已停止")
        self.logger.log("远程关机服务已停止")

    def open_web_browser(self):
        """打开网页浏览器"""
        if hasattr(self, 'web_url'):
            self.web_server.open_browser(self.web_url)

    def update_ui_status(self, status):
        """更新UI状态"""
        self.status_label.setText(f"状态: {status}")
        self.log_message(f"状态更新: {status}")

    def log_message(self, message):
        """记录消息到日志框"""
        timestamp = time.strftime("%H:%M:%S")
        self.message_log.append(f"[{timestamp}] {message}")

        # 限制日志行数
        if self.message_log.document().lineCount() > 100:
            cursor = self.message_log.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.select(cursor.LineUnderCursor)
            cursor.removeSelectedText()