import PyInstaller.__main__
import os
import shutil


def build_executable():
    # 清理之前的构建文件
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")

    # PyInstaller 配置
    params = [
        "gui_main.py",  # 主程序文件
        "--name=SystemToolbox",  # 生成的exe名称
        "--onefile",  # 打包成单个文件
        "--windowed",  # 不显示命令行窗口
        "--icon=icon.ico",  # 图标文件（可选）
        "--add-data=modules;modules",  # 包含模块目录
        "--hidden-import=psutil",
        "--hidden-import=requests",
        "--clean",  # 清理临时文件
        "--noconfirm"  # 覆盖输出目录而不确认
    ]

    # 执行打包
    PyInstaller.__main__.run(params)

    print("打包完成！可执行文件在 dist 目录中")


if __name__ == "__main__":
    build_executable()