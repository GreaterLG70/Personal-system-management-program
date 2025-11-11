import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules import ShutdownTool, SystemTools


class SystemToolboxGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("系统工具箱 v1.0 - 牧歌")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # 设置图标（如果有的话）
        try:
            self.root.iconbitmap("icon.ico")  # 可选
        except:
            pass

        # 初始化工具类
        self.shutdown_tool = ShutdownTool()
        self.system_tools = SystemTools()

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 标题
        title_label = ttk.Label(main_frame,
                                text="系统工具箱 v1.0",
                                font=("Arial", 16, "bold"),
                                foreground="darkgreen")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 作者信息
        author_label = ttk.Label(main_frame,
                                 text="作者: 牧歌 - 2025.11.5",
                                 font=("Arial", 10),
                                 foreground="gray")
        author_label.grid(row=0, column=1, columnspan=2, pady=(0, 20), sticky=tk.E)

        # 创建标签页
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        # 定时关机标签页
        self.create_shutdown_tab()

        # 系统维护标签页
        self.create_system_tools_tab()

        # 关于标签页
        self.create_about_tab()

        # 输出框
        self.output_frame = ttk.LabelFrame(main_frame, text="输出信息", padding="5")
        self.output_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        self.output_frame.columnconfigure(0, weight=1)
        self.output_frame.rowconfigure(0, weight=1)

        self.output_text = scrolledtext.ScrolledText(self.output_frame,
                                                     height=10,
                                                     wrap=tk.WORD,
                                                     state=tk.DISABLED)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def create_shutdown_tab(self):
        """创建定时关机标签页"""
        shutdown_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(shutdown_frame, text="定时关机")

        # 输入框和标签
        ttk.Label(shutdown_frame, text="关机延迟时间（小时）:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.shutdown_entry = ttk.Entry(shutdown_frame, width=20)
        self.shutdown_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        self.shutdown_entry.insert(0, "1.0")

        # 按钮框架
        button_frame = ttk.Frame(shutdown_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame,
                   text="设置定时关机",
                   command=self.set_shutdown).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame,
                   text="取消关机计划",
                   command=self.cancel_shutdown).pack(side=tk.LEFT, padx=5)

        # 状态显示
        self.shutdown_status = ttk.Label(shutdown_frame, text="就绪", foreground="blue")
        self.shutdown_status.grid(row=2, column=0, columnspan=2, pady=5)

        shutdown_frame.columnconfigure(1, weight=1)

    def create_system_tools_tab(self):
        """创建系统维护标签页"""
        tools_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tools_frame, text="系统维护")

        # 创建工具按钮
        tools = [
            ("清理临时文件", self.clean_temp_files),
            ("检查磁盘错误", self.check_disk_errors),
            ("查看系统信息", self.get_system_info),
            ("网络诊断", self.network_diagnosis),
            ("进程管理", self.process_management)
        ]

        for i, (text, command) in enumerate(tools):
            ttk.Button(tools_frame,
                       text=text,
                       command=command,
                       width=20).grid(row=i, column=0, pady=5, sticky=tk.W)

    def create_about_tab(self):
        """创建关于标签页"""
        about_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(about_frame, text="关于")

        about_text = """
系统工具箱 v1.0

功能特点：
• 定时关机管理
• 系统维护工具
• 临时文件清理
• 磁盘错误检查
• 系统信息查看
• 网络诊断
• 进程管理

作者：牧歌
日期：2025年11月5日
版本：1.0.0

本工具基于Python开发，提供便捷的系统管理功能。
        """

        about_label = ttk.Label(about_frame,
                                text=about_text,
                                justify=tk.LEFT,
                                font=("Arial", 10))
        about_label.grid(row=0, column=0, sticky=tk.W)

    def log_message(self, message, message_type="info"):
        """在输出框中显示消息"""
        self.output_text.config(state=tk.NORMAL)

        # 添加时间戳
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")

        # 设置颜色
        if message_type == "error":
            tag = "error"
            self.output_text.tag_config("error", foreground="red")
        elif message_type == "success":
            tag = "success"
            self.output_text.tag_config("success", foreground="green")
        else:
            tag = "info"
            self.output_text.tag_config("info", foreground="blue")

        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def set_shutdown(self):
        """设置定时关机"""
        hours = self.shutdown_entry.get().strip()
        if not hours:
            messagebox.showerror("错误", "请输入关机延迟时间！")
            return

        def execute_shutdown():
            self.shutdown_status.config(text="设置中...", foreground="orange")
            success, message = self.shutdown_tool.set_shutdown(hours)

            if success:
                self.shutdown_status.config(text="设置成功", foreground="green")
                self.log_message(f"定时关机设置成功: {message}", "success")
            else:
                self.shutdown_status.config(text="设置失败", foreground="red")
                self.log_message(f"定时关机设置失败: {message}", "error")

        # 在新线程中执行，避免界面卡顿
        threading.Thread(target=execute_shutdown, daemon=True).start()

    def cancel_shutdown(self):
        """取消关机计划"""

        def execute_cancel():
            self.shutdown_status.config(text="取消中...", foreground="orange")
            success, message = self.shutdown_tool.cancel_shutdown()

            if success:
                self.shutdown_status.config(text="取消成功", foreground="green")
                self.log_message(f"关机计划取消: {message}", "success")
            else:
                self.shutdown_status.config(text="取消失败", foreground="red")
                self.log_message(f"取消关机计划失败: {message}", "error")

        threading.Thread(target=execute_cancel, daemon=True).start()

    def clean_temp_files(self):
        """清理临时文件"""

        def execute_clean():
            self.log_message("开始清理临时文件...", "info")
            result = self.system_tools.clean_temp_files()
            self.log_message(result, "success")

        threading.Thread(target=execute_clean, daemon=True).start()

    def check_disk_errors(self):
        """检查磁盘错误"""

        def execute_check():
            self.log_message("开始检查磁盘错误...", "info")
            result = self.system_tools.check_disk_errors()
            self.log_message(result, "success")

        threading.Thread(target=execute_check, daemon=True).start()

    def get_system_info(self):
        """获取系统信息"""

        def execute_info():
            self.log_message("开始获取系统信息...", "info")
            result = self.system_tools.get_system_info()
            self.log_message(result, "success")

        threading.Thread(target=execute_info, daemon=True).start()

    def network_diagnosis(self):
        """网络诊断"""

        def execute_network():
            self.log_message("开始网络诊断...", "info")
            result = self.system_tools.network_diagnosis()
            self.log_message(result, "success")

        threading.Thread(target=execute_network, daemon=True).start()

    def process_management(self):
        """进程管理"""
        # 创建一个新窗口来管理进程
        process_window = tk.Toplevel(self.root)
        process_window.title("进程管理")
        process_window.geometry("600x400")

        # 进程列表
        process_frame = ttk.Frame(process_window, padding="10")
        process_frame.pack(fill=tk.BOTH, expand=True)

        # 进程列表文本框
        process_text = scrolledtext.ScrolledText(process_frame, height=15, wrap=tk.WORD)
        process_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # 显示进程列表
        try:
            import psutil
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    processes.append(proc)
                    if len(processes) >= 15:
                        break
                except:
                    pass

            process_text.insert(tk.END, "正在运行的进程（前15个）:\n\n")
            for proc in processes:
                process_text.insert(tk.END,
                                    f"PID: {proc.info['pid']}, 名称: {proc.info['name']}, 内存: {proc.info['memory_percent']:.1f}%\n")
        except Exception as e:
            process_text.insert(tk.END, f"获取进程列表失败: {e}")

        process_text.config(state=tk.DISABLED)

        # 结束进程输入框和按钮
        input_frame = ttk.Frame(process_window, padding="10")
        input_frame.pack(fill=tk.X)

        ttk.Label(input_frame, text="进程名:").pack(side=tk.LEFT, padx=5)
        process_entry = ttk.Entry(input_frame, width=20)
        process_entry.pack(side=tk.LEFT, padx=5)

        def kill_process():
            proc_name = process_entry.get().strip()
            if not proc_name:
                messagebox.showerror("错误", "请输入进程名！")
                return

            if messagebox.askyesno("确认", f"确定要结束进程 '{proc_name}' 吗？"):
                result = self.system_tools.process_management_silent(proc_name)
                messagebox.showinfo("结果", result)
                process_window.destroy()

        ttk.Button(input_frame,
                   text="结束进程",
                   command=kill_process).pack(side=tk.LEFT, padx=5)


def main():
    root = tk.Tk()
    app = SystemToolboxGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()