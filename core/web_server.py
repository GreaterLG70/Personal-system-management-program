import http.server
import socketserver
import threading
import os
import webbrowser
import socket
from PyQt5.QtCore import QObject, pyqtSignal


class WebServer(QObject):
    """简单的HTTP服务器，用于提供网页客户端"""
    server_started = pyqtSignal(str)
    server_stopped = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, logger, port=8080, resource_path_func=None):
        super().__init__()
        self.logger = logger
        self.port = port
        self.httpd = None
        self.server_thread = None
        self.is_running = False
        self.resource_path = resource_path_func or (lambda x: x)

        # 获取web_client目录的路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)

        # 尝试多种可能的路径
        possible_paths = [
            os.path.join(project_root, 'styles', 'web_client'),
            os.path.join(project_root, 'web_client'),
            os.path.join(os.path.dirname(project_root), 'styles', 'web_client'),
            self.resource_path('styles/web_client')
        ]

        for path in possible_paths:
            if os.path.exists(path):
                self.web_dir = path
                break
        else:
            # 如果都找不到，使用第一个路径并记录警告
            self.web_dir = possible_paths[0]
            self.logger.log(f"Web目录不存在，使用默认路径: {self.web_dir}", 'warning')

    def get_local_ip(self):
        """获取本机IP地址（纯Python实现）"""
        try:
            # 方法1: 通过连接外部地址获取本机IP（最可靠）
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            try:
                # 方法2: 获取主机名对应的IP
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)
                if ip.startswith('127.'):
                    # 如果是回环地址，尝试获取其他地址
                    return self.get_all_ips()
                return ip
            except:
                # 方法3: 获取所有网络接口的IP
                return self.get_all_ips()

    def get_all_ips(self):
        """获取所有非回环的IP地址"""
        try:
            # 获取所有网络接口的IP地址
            ips = []
            # 尝试获取所有网络接口
            for interface in socket.getaddrinfo(socket.gethostname(), None):
                ip = interface[4][0]
                if ip and not ip.startswith('127.') and not ip.startswith('::') and ip != '0.0.0.0':
                    ips.append(ip)

            # 去重并返回第一个非回环IP
            unique_ips = list(dict.fromkeys(ips))
            if unique_ips:
                return unique_ips[0]

            # 如果没有找到，尝试通过socket连接获取
            return self.get_ip_by_connection()
        except:
            return "127.0.0.1"

    def get_ip_by_connection(self):
        """通过连接到多个外部服务获取IP"""
        test_services = [
            ("8.8.8.8", 80),  # Google DNS
            ("1.1.1.1", 80),  # Cloudflare DNS
            ("208.67.222.222", 80)  # OpenDNS
        ]

        for service_ip, service_port in test_services:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(2)  # 2秒超时
                s.connect((service_ip, service_port))
                ip = s.getsockname()[0]
                s.close()
                return ip
            except:
                continue

        return "127.0.0.1"

    def get_network_info(self):
        """获取网络信息"""
        local_ip = self.get_local_ip()
        hostname = socket.gethostname()

        info = {
            'hostname': hostname,
            'local_ip': local_ip,
            'localhost': '127.0.0.1',
            'port': self.port
        }

        return info

    def start_server(self):
        """启动HTTP服务器"""
        try:
            if not os.path.exists(self.web_dir):
                self.error_occurred.emit(f"Web目录不存在: {self.web_dir}")
                self.logger.log(f"Web目录不存在: {self.web_dir}", 'error')
                return False

            # 创建自定义请求处理器
            class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
                # 将web_dir作为类属性
                directory = self.web_dir

                def __init__(self, *args, **kwargs):
                    # 在调用父类构造函数时传递directory参数
                    super().__init__(*args, directory=self.directory, **kwargs)

                def log_message(self, format, *args):
                    # 重写日志方法，避免在控制台输出过多信息
                    pass

            # 在单独的线程中运行服务器
            def run_server():
                try:
                    # 获取网络信息
                    network_info = self.get_network_info()
                    local_ip = network_info['local_ip']

                    with socketserver.TCPServer(("", self.port), CustomHTTPRequestHandler) as httpd:
                        self.httpd = httpd
                        self.is_running = True

                        # 使用IP地址而不是localhost
                        url = f"http://{local_ip}:{self.port}/remote_control.html"
                        self.server_started.emit(url)

                        # 记录详细的网络信息
                        self.logger.log(f"HTTP服务器已启动")
                        self.logger.log(f"主机名: {network_info['hostname']}")
                        self.logger.log(f"本地IP: {local_ip}")
                        self.logger.log(f"端口: {self.port}")
                        self.logger.log(f"本地访问: http://localhost:{self.port}/remote_control.html")
                        self.logger.log(f"网络访问: {url}")

                        # 如果IP是127.0.0.1，提示用户检查网络连接
                        if local_ip == "127.0.0.1":
                            self.logger.log("警告: 检测到的IP为127.0.0.1，其他设备可能无法访问", 'warning')

                        httpd.serve_forever()
                except OSError as e:
                    if e.errno == 48 or e.errno == 10048:  # 端口被占用
                        self.logger.log(f"端口 {self.port} 被占用，尝试端口 {self.port + 1}")
                        self.port += 1
                        self.start_server()
                    else:
                        self.error_occurred.emit(f"启动HTTP服务器失败: {str(e)}")
                        self.logger.log(f"HTTP服务器启动失败: {str(e)}", 'error')
                except Exception as e:
                    self.error_occurred.emit(f"HTTP服务器错误: {str(e)}")
                    self.logger.log(f"HTTP服务器错误: {str(e)}", 'error')
                finally:
                    self.is_running = False
                    self.server_stopped.emit()

            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            return True

        except Exception as e:
            self.error_occurred.emit(f"启动服务器失败: {str(e)}")
            self.logger.log(f"启动HTTP服务器失败: {str(e)}", 'error')
            return False

    def stop_server(self):
        """停止HTTP服务器"""
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.is_running = False
            self.logger.log("HTTP服务器已停止")

    def open_browser(self, url=None):
        """在浏览器中打开网页客户端"""
        try:
            if url is None:
                # 如果没有提供URL，使用IP地址
                local_ip = self.get_local_ip()
                url = f"http://{local_ip}:{self.port}/remote_control.html"

            webbrowser.open(url)
            self.logger.log(f"已在浏览器中打开: {url}")
        except Exception as e:
            self.error_occurred.emit(f"打开浏览器失败: {str(e)}")
            self.logger.log(f"打开浏览器失败: {str(e)}", 'error')