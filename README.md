PRTS - 系统工具箱
<div align="center">
![PRTS Logo](/prts.jpg)

P  R  T  S

[![Version](https://img.shields.io/badge/版本-1.2.0-blue.svg)](https://github.com/your-repo/PRTS/releases)
[![Python](https://img.shields.io/badge/Python-3.8+-yellow.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/许可证-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/平台-Windows%20%7C%20Linux%20%7C%20Mac-lightgrey.svg)]()

"博士，系统维护工作就交给我吧"

</div>
🌟 系统概述
PRTS（原系统工具箱）是一款基于PyQt5开发的跨平台系统管理工具，集成了多种实用功能，为您的计算机提供全方位的维护和远程控制能力。

"在罗德岛，我们相信最好的防御是完善的系统维护"

🚀 核心功能

🔧 系统维护模块

定时关机工具 - 精确控制计算机开关机时间

系统状态监控 - 实时监控CPU、内存、磁盘使用情况

临时文件清理 - 自动清理系统垃圾，释放存储空间

网络诊断 - 快速检测网络连接状态

🌐 远程控制模块

网页远程控制 - 通过浏览器远程控制计算机

MQTT协议支持 - 安全的远程指令传输

多平台兼容 - 支持Windows、Linux、macOS系统

实时状态反馈 - 随时掌握计算机运行状态

⚡ 特色功能

倒计时显示 - 直观的关机倒计时界面

工具间联动 - 各功能模块间完美协作

日志系统 - 详细的运行日志记录

美观界面 - 明日方舟风格的现代化UI

🛠️ 安装指南

系统要求

操作系统: Windows 7+ / macOS 10.12+ / Ubuntu 16.04+

Python: 3.8 或更高版本

内存: 至少 2GB RAM

存储空间: 至少 100MB 可用空间

快速安装

方法一：使用预编译版本（推荐）

从 Release页面 下载最新版本

解压到任意目录

运行 PRTS.exe（Windows）或 启动PRTS.sh（Linux/macOS）

方法二：从源码运行

# 克隆仓库
bash
git clone https://github.com/your-repo/PRTS.git

cd PRTS

# 安装依赖

pip install -r requirements.txt

# 运行程序

python main.py

依赖安装

bash

pip install PyQt5 paho-mqtt psutil

📖 使用说明

首次启动

启动程序: 双击 PRTS.exe 或运行启动脚本

权限设置: 建议以管理员权限运行以获得完整功能

功能探索: 在左侧面板选择需要的功能模块

定时关机

text

博士，您可以选择：

- 立即关机：紧急情况下使用
  
- 定时关机：设定具体时间后自动关机
  
- 取消计划：随时取消已设定的关机任务
  
远程控制

进入"远程关机工具"页面

启动MQTT服务

使用网页端或移动设备访问控制界面

发送关机、重启或休眠指令

系统维护

磁盘清理: 定期清理临时文件

系统诊断: 检查系统健康状况

进程管理: 查看和管理运行中的进程


🔧 开发指南

项目结构

text

PRTS/
├── core/                 # 核心功能模块

│   ├── logger.py        # 日志系统

│   ├── shutdown_tool.py # 关机工具

│   ├── system_tool.py   # 系统工具

│   └── remote_shutdown.py # 远程控制

├── web_client/          # 网页客户端

├── logs/               # 日志目录

└── main.py            # 程序入口

构建项目

bash

# 使用构建脚本

python build.py

# 或直接使用PyInstaller

pyinstaller --name=PRTS --onedir --windowed --icon=icon.ico main.py

贡献代码

Fork 本仓库

创建特性分支 (git checkout -b feature/AmazingFeature)

提交更改 (git commit -m 'Add some AmazingFeature')

推送到分支 (git push origin feature/AmazingFeature)

开启 Pull Request

⚠️ 注意事项

安全提示

🔒 远程控制功能建议在可信网络环境中使用

🔐 定期更新MQTT连接密码

📱 网页控制端建议使用HTTPS加密

使用建议

💡 定期使用系统清理功能保持计算机性能

🕒 设置关机计划时请确保已保存所有工作

🌐 使用远程功能前请检查网络连接

故障排除

text

常见问题：

1. 程序无法启动 → 检查Python环境和依赖
   
2. 远程控制失败 → 验证网络连接和MQTT配置
   
3. 权限不足 → 以管理员权限重新运行
📄 许可证

本项目采用 MIT 许可证 - 查看 LICENSE 文件了解详情

🤝 支持与反馈

如果您在使用过程中遇到任何问题或有改进建议：

📧 邮箱支持: g2315562507@163.com

🐛 问题反馈: GitHub Issues

💬 讨论区: GitHub Discussions

🙏 致谢

感谢以下开源项目的支持：

PyQt5 - 强大的GUI框架

paho-mqtt - MQTT客户端库

psutil - 系统监控工具

<div align="center">
  
"为了更高效的工作环境，PRTS随时为您服务"

博士，别忘了定期进行系统维护哦~

© 2025 PRTS System | 牧歌

</div>
