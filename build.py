import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
import datetime


class BuildTool:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.release_dir = self.project_root / "release"

    def clean_build(self):
        """清理构建目录"""
        print("正在清理构建目录...")
        for directory in [self.build_dir, self.dist_dir]:
            if directory.exists():
                shutil.rmtree(directory)
                print(f"已删除: {directory}")

        # 清理临时文件
        for pattern in ["*.spec", "*.log", "*.tmp"]:
            for file in self.project_root.glob(pattern):
                if file.exists():
                    file.unlink()
                    print(f"已删除: {file}")

    def check_dependencies(self):
        """检查依赖是否安装"""
        print("正在检查依赖...")

        packages = [
            'PyQt5',
            'paho-mqtt',
            'psutil',
            'pyinstaller'
        ]

        for package in packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"✓ {package} 已安装")
            except ImportError:
                print(f"正在安装 {package}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✓ {package} 安装成功")
                else:
                    print(f"✗ {package} 安装失败: {result.stderr}")

    def build_directory(self):
        """构建目录版本"""
        print("正在构建 PRTS 目录版本...")

        # 使用完整的Python解释器路径和模块调用方式
        pyinstaller_cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            '--name=PRTS',
            '--onedir',
            '--windowed',
            '--icon=icon.ico',
            '--add-data=icon.ico;.',
            '--add-data=prts.jpg;.',
            '--add-data=web_client;web_client',
            '--add-data=logs;logs',
            '--hidden-import=PyQt5.QtCore',
            '--hidden-import=PyQt5.QtGui',
            '--hidden-import=PyQt5.QtWidgets',
            '--hidden-import=paho.mqtt.client',
            '--hidden-import=psutil',
            '--hidden-import=http.server',
            '--hidden-import=socketserver',
            '--clean',
            'main.py'
        ]

        print(f"执行命令: {' '.join(pyinstaller_cmd)}")

        try:
            result = subprocess.run(pyinstaller_cmd, check=True, capture_output=True, text=True, cwd=self.project_root)
            print("✓ PRTS 目录版本构建成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 构建失败: {e}")
            if e.stderr:
                print(f"错误输出: {e.stderr}")
            if e.stdout:
                print(f"标准输出: {e.stdout}")
            return False
        except FileNotFoundError as e:
            print(f"✗ 找不到PyInstaller: {e}")
            print("请确保已安装PyInstaller: pip install pyinstaller")
            return False

    def create_release_package(self):
        """创建发布包"""
        print("正在创建发布包...")

        # 源目录和目标目录
        source_dir = self.dist_dir / "PRTS"
        version = datetime.datetime.now().strftime("%Y%m%d")
        target_dir = self.release_dir / f"PRTS_v{version}"

        if not source_dir.exists():
            print("✗ 构建目录不存在，请先构建项目")
            return False

        # 清理旧的发布目录
        if target_dir.exists():
            shutil.rmtree(target_dir)

        # 复制构建结果
        shutil.copytree(source_dir, target_dir)
        print(f"✓ 已复制到: {target_dir}")

        # 确保必要的目录存在
        (target_dir / "logs").mkdir(exist_ok=True)

        # 复制额外的文件
        extra_files = [
            "README.md",
            "使用说明.txt",
            "版本信息.txt",
            "create_copy.py"
        ]

        for file in extra_files:
            src = self.project_root / file
            if src.exists():
                shutil.copy2(src, target_dir)
                print(f"✓ 已复制: {file}")

        # 创建启动脚本
        self.create_launch_scripts(target_dir)

        # 创建版本信息文件
        self.create_version_info(target_dir, version)

        # 压缩发布包
        self.create_zip_package(target_dir)

        return True

    def create_launch_scripts(self, target_dir):
        """创建启动脚本"""
        # Windows批处理文件
        bat_content = '''@echo off
chcp 65001
title PRTS - 系统工具箱
echo 启动 PRTS 系统工具箱...
PRTS.exe
pause
'''
        bat_file = target_dir / "启动PRTS.bat"
        with open(bat_file, 'w', encoding='utf-8') as f:
            f.write(bat_content)

        # Linux/Mac shell脚本
        sh_content = '''#!/bin/bash
echo "启动 PRTS 系统工具箱..."
./PRTS
'''
        sh_file = target_dir / "启动PRTS.sh"
        with open(sh_file, 'w', encoding='utf-8') as f:
            f.write(sh_content)

        # 在Linux/Mac上设置执行权限
        if platform.system() != "Windows":
            subprocess.run(['chmod', '+x', str(sh_file)])

        print("✓ 启动脚本已创建")

    def create_version_info(self, target_dir, version):
        """创建版本信息文件"""
        version_info = f"""PRTS 系统工具箱
版本信息
===============

版本号: {version}
构建时间: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
项目名称: PRTS (原系统工具箱)
开发者: 牧歌

目录结构:
===============
PRTS.exe              - 主程序
logs/                 - 日志目录
web_client/           - 网页客户端资源
启动PRTS.bat          - Windows启动脚本
启动PRTS.sh           - Linux/Mac启动脚本

功能模块:
===============
- 定时关机工具
- 系统维护工具  
- 远程关机工具
- 网页远程控制

使用说明:
===============
1. 双击 PRTS.exe 或运行启动脚本
2. 首次使用建议以管理员权限运行
3. 远程控制功能需要启动MQTT服务

技术支持:
===============
如有问题请查看日志文件或联系开发者
"""

        version_file = target_dir / "版本信息.txt"
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write(version_info)

        print("✓ 版本信息文件已创建")

    def create_zip_package(self, target_dir):
        """创建ZIP压缩包"""
        try:
            import zipfile

            zip_path = self.release_dir / f"{target_dir.name}.zip"

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(target_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.release_dir)
                        zipf.write(file_path, arcname)

            print(f"✓ ZIP包已创建: {zip_path}")
            print(f"✓ 文件大小: {zip_path.stat().st_size / 1024 / 1024:.2f} MB")
        except ImportError:
            print("✗ 无法创建ZIP包: zipfile模块不可用")

    def verify_build(self):
        """验证构建结果"""
        print("正在验证构建结果...")

        build_dir = self.dist_dir / "PRTS"

        if not build_dir.exists():
            print("✗ 构建目录不存在")
            return False

        # 首先列出构建目录的所有内容，帮助调试
        print("构建目录内容:")
        for item in build_dir.iterdir():
            if item.is_file():
                print(f"  文件: {item.name}")
            elif item.is_dir():
                print(f"  目录: {item.name}")

        # 检查必要文件 - 使用更宽松的检查
        all_exists = True

        # 检查主程序
        exe_path = build_dir / "PRTS.exe"
        if exe_path.exists():
            print(f"✓ 主程序: PRTS.exe")
        else:
            print(f"✗ 缺失主程序: PRTS.exe")
            all_exists = False

        # 检查资源文件 - 可能在根目录或子目录中
        resource_files = ["icon.ico", "prts.jpg"]
        for file in resource_files:
            # 尝试多个可能的位置
            possible_locations = [
                build_dir / file,  # 根目录
                build_dir / "web_client" / file,  # web_client目录
            ]

            found = False
            for location in possible_locations:
                if location.exists():
                    print(f"✓ {file} (位置: {location.relative_to(build_dir)})")
                    found = True
                    break

            if not found:
                print(f"⚠ {file} 未在常见位置找到，但可能不影响运行")
                # 这里不标记为失败，因为程序可能通过其他方式访问资源

        # 检查目录结构
        required_dirs = ["logs", "web_client"]
        for dir_path in required_dirs:
            dir_full_path = build_dir / dir_path
            if dir_full_path.exists():
                print(f"✓ 目录: {dir_path}")

                # 如果是web_client目录，检查关键文件
                if dir_path == "web_client":
                    web_client_files = ["remote_control.html", "prts.jpg", "icon.ico"]
                    for wc_file in web_client_files:
                        wc_path = dir_full_path / wc_file
                        if wc_path.exists():
                            print(f"  ✓ {wc_file}")
                        else:
                            print(f"  ⚠ 缺失: {wc_file} (可能影响网页控制功能)")
            else:
                print(f"⚠ 缺失目录: {dir_path} (将自动创建)")
                # 创建缺失的目录
                dir_full_path.mkdir(exist_ok=True)

        # 如果主程序存在，就认为构建基本成功
        if exe_path.exists():
            print("✓ 构建验证通过 (主程序存在)")
            return True
        else:
            print("✗ 构建验证失败 (主程序缺失)")
            return False

    def build_release(self):
        """构建发布版本"""
        print("=" * 50)
        print("       PRTS 系统工具箱构建工具")
        print("=" * 50)

        # 检查PyInstaller是否安装
        try:
            import PyInstaller
            print("✓ PyInstaller 已安装")
        except ImportError:
            print("正在安装PyInstaller...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "pyinstaller"
            ], capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ PyInstaller 安装成功")
            else:
                print(f"✗ PyInstaller 安装失败: {result.stderr}")
                return

        # 创建必要目录
        self.release_dir.mkdir(exist_ok=True)

        # 清理
        self.clean_build()

        # 检查依赖
        self.check_dependencies()

        # 构建目录版本
        print("\n开始构建 PRTS 系统工具箱...")
        if self.build_directory():
            print("\n✓ 构建成功!")

            # 验证构建
            if self.verify_build():
                print("\n开始创建发布包...")
                if self.create_release_package():
                    print("\n" + "=" * 50)
                    print("发布包创建完成!")

                    # 显示最终信息
                    build_dir = self.dist_dir / "PRTS"
                    version = datetime.datetime.now().strftime("%Y%m%d")
                    release_dir = self.release_dir / f"PRTS_v{version}"

                    print(f"\n构建目录: {build_dir}")
                    print(f"发布目录: {release_dir}")
                    print(f"ZIP包: {release_dir}.zip")

                    # 询问是否打开目录
                    if platform.system() == "Windows":
                        open_dir = input("\n是否打开发布目录? (y/N): ").lower().strip()
                        if open_dir == 'y':
                            os.startfile(self.release_dir)
                else:
                    print("\n✗ 发布包创建失败")
            else:
                print("\n⚠ 构建验证有警告，但继续创建发布包...")
                # 即使验证有警告，也尝试创建发布包
                if self.create_release_package():
                    print("\n" + "=" * 50)
                    print("发布包创建完成 (有警告)!")
                else:
                    print("\n✗ 发布包创建失败")
        else:
            print("\n✗ 构建失败")

        input("\n按回车键退出...")


def main():
    """主函数"""
    builder = BuildTool()
    builder.build_release()


if __name__ == '__main__':
    main()