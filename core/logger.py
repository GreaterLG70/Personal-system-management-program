import os
import sys
import logging
from datetime import datetime, timedelta
from PyQt5.QtCore import QObject, pyqtSignal
import shutil


class Logger(QObject):
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # 设置日志目录为 C:\SystemToolbox\logs
        self.log_dir = os.path.join(os.environ.get('SystemDrive', 'C:'), 'SystemToolbox', 'logs')
        self.setup_logging()
        self.clean_old_logs()

    def setup_logging(self):
        """设置日志系统"""
        try:
            # 创建日志目录
            os.makedirs(self.log_dir, exist_ok=True)

            # 先创建 logger 实例
            self.logger = logging.getLogger('SystemToolbox')
            self.logger.setLevel(logging.INFO)

            # 清除已有的处理器，避免重复
            if self.logger.handlers:
                self.logger.handlers.clear()

            # 创建日志文件名（按日期）
            log_file = os.path.join(self.log_dir, f"toolbox_{datetime.now().strftime('%Y%m%d')}.log")

            # 创建文件处理器
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)

            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # 创建格式化器
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # 添加处理器到日志器
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

            # 现在可以安全地记录日志了
            self.logger.info(f"日志目录已创建: {self.log_dir}")
            self.logger.info("=" * 50)
            self.logger.info("系统工具箱启动")
            self.logger.info(f"日志文件: {log_file}")
            self.logger.info("=" * 50)

        except Exception as e:
            # 如果创建失败，使用临时目录作为备用
            temp_dir = os.path.join(os.environ.get('TEMP', ''), 'SystemToolbox', 'logs')
            os.makedirs(temp_dir, exist_ok=True)
            self.log_dir = temp_dir

            # 重新设置日志系统
            self.setup_logging()  # 递归调用，但这次应该会成功
            self.logger.error(f"无法创建系统日志目录，使用临时目录: {temp_dir}, 错误: {e}")

    def clean_old_logs(self):
        """清理一周前的日志文件"""
        try:
            cutoff_date = datetime.now() - timedelta(days=7)
            deleted_count = 0

            if not os.path.exists(self.log_dir):
                return

            for filename in os.listdir(self.log_dir):
                if filename.startswith('toolbox_') and filename.endswith('.log'):
                    try:
                        # 从文件名提取日期
                        date_str = filename.split('_')[1].split('.')[0]
                        file_date = datetime.strptime(date_str, '%Y%m%d')

                        if file_date < cutoff_date:
                            file_path = os.path.join(self.log_dir, filename)
                            os.remove(file_path)
                            deleted_count += 1
                            self.log(f"删除过期日志文件: {filename}", 'info')
                    except (ValueError, IndexError) as e:
                        # 文件名格式不正确，跳过
                        continue

            if deleted_count > 0:
                self.log(f"已清理 {deleted_count} 个过期日志文件", 'info')
            else:
                self.log("没有需要清理的过期日志文件", 'info')

        except Exception as e:
            self.log(f"清理旧日志时出错: {str(e)}", 'error')

    def log(self, message, level='info'):
        """记录日志并发送信号更新UI"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {message}"

        # 发送信号到UI
        self.log_signal.emit(formatted_message)

        # 记录到文件
        if level == 'info':
            self.logger.info(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'error':
            self.logger.error(message)

    def get_log_directory(self):
        """获取日志目录路径"""
        return self.log_dir

    def get_current_log_file(self):
        """获取当前日志文件路径"""
        log_file = os.path.join(self.log_dir, f"toolbox_{datetime.now().strftime('%Y%m%d')}.log")
        return log_file

    def open_log_directory(self):
        """打开日志目录（用于调试）"""
        try:
            if os.name == 'nt':  # Windows
                os.system(f'explorer "{self.log_dir}"')
            elif os.name == 'posix':  # Linux/Mac
                if sys.platform == 'darwin':
                    os.system(f'open "{self.log_dir}"')
                else:
                    os.system(f'xdg-open "{self.log_dir}"')
            return True
        except Exception as e:
            self.log(f"打开日志目录失败: {str(e)}", 'error')
            return False

    def get_log_stats(self):
        """获取日志统计信息"""
        try:
            if not os.path.exists(self.log_dir):
                return {"total_files": 0, "total_size": 0, "oldest_log": None, "newest_log": None}

            log_files = []
            total_size = 0

            for filename in os.listdir(self.log_dir):
                if filename.startswith('toolbox_') and filename.endswith('.log'):
                    file_path = os.path.join(self.log_dir, filename)
                    file_size = os.path.getsize(file_path)
                    log_files.append({
                        'name': filename,
                        'size': file_size,
                        'date': datetime.fromtimestamp(os.path.getctime(file_path))
                    })
                    total_size += file_size

            if not log_files:
                return {"total_files": 0, "total_size": 0, "oldest_log": None, "newest_log": None}

            # 按日期排序
            log_files.sort(key=lambda x: x['date'])

            return {
                "total_files": len(log_files),
                "total_size": total_size,
                "oldest_log": log_files[0]['name'] if log_files else None,
                "newest_log": log_files[-1]['name'] if log_files else None
            }
        except Exception as e:
            self.log(f"获取日志统计信息失败: {str(e)}", 'error')
            return {"total_files": 0, "total_size": 0, "oldest_log": None, "newest_log": None}