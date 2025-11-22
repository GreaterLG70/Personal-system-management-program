import os
import shutil
import datetime
from pathlib import Path


def create_project_copy():
    """创建项目副本"""

    # 获取当前项目路径
    current_project = Path(__file__).parent
    parent_dir = current_project.parent

    print("=" * 50)
    print("        项目副本创建工具")
    print("=" * 50)

    # 获取版本名称
    version_name = input("请输入新版本名称（例如 v2, new_ui, stable）: ").strip()
    if not version_name:
        version_name = "backup"

    new_folder_name = f"SystemToolbox_{version_name}"
    new_project_path = parent_dir / new_folder_name

    # 检查是否已存在
    if new_project_path.exists():
        print(f"错误: 文件夹 {new_folder_name} 已存在！")
        input("按回车键退出...")
        return

    # 定义要排除的文件和文件夹
    exclude_patterns = [
        '__pycache__',
        'build',
        'dist',
        '*.spec',
        '*.log',
        '*.tmp',
        'temp'
    ]

    print(f"\n正在创建副本: {new_folder_name}")

    try:
        # 创建新文件夹
        new_project_path.mkdir(exist_ok=True)

        # 复制文件
        copy_count = 0
        for item in current_project.iterdir():
            # 检查是否在排除列表中
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern.startswith('*'):
                    # 处理通配符模式
                    if item.name.endswith(pattern[1:]):
                        should_exclude = True
                        break
                elif item.name == pattern:
                    should_exclude = True
                    break

            if should_exclude:
                print(f"跳过: {item.name}")
                continue

            try:
                if item.is_file():
                    shutil.copy2(item, new_project_path / item.name)
                    copy_count += 1
                elif item.is_dir():
                    shutil.copytree(item, new_project_path / item.name,
                                    ignore=shutil.ignore_patterns(*exclude_patterns))
                    copy_count += 1
            except Exception as e:
                print(f"复制 {item.name} 时出错: {e}")

        # 创建版本信息文件
        version_info = f"""项目副本信息
================

原项目: {current_project.name}
副本名称: {new_folder_name}
创建时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
版本说明: {version_name}
文件数量: {copy_count}

迭代开发说明:
1. 此副本用于 {version_name} 版本的开发
2. 可以安全修改，不会影响原项目
3. 开发完成后可以合并回主项目

开发建议:
- 修改主要文件时备份原文件
- 定期测试功能完整性
- 记录重要修改内容
"""

        with open(new_project_path / "版本信息.txt", "w", encoding="utf-8") as f:
            f.write(version_info)

        # 创建gitignore（如果不存在）
        gitignore_content = """# 构建文件
build/
dist/
*.spec

# 缓存文件
__pycache__/
*.pyc
*.pyo

# 日志文件
*.log
logs/

# 临时文件
*.tmp
temp/

# 系统文件
.DS_Store
Thumbs.db
"""
        gitignore_path = new_project_path / ".gitignore"
        if not gitignore_path.exists():
            with open(gitignore_path, "w", encoding="utf-8") as f:
                f.write(gitignore_content)

        print("\n" + "=" * 50)
        print("          副本创建成功！")
        print("=" * 50)
        print(f"新项目位置: {new_project_path}")
        print(f"复制文件数: {copy_count}")
        print(f"创建时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n可以开始在新文件夹中进行迭代开发了！")

        # 询问是否打开新文件夹
        open_new = input("\n是否立即打开新项目文件夹？(y/n): ").lower().strip()
        if open_new == 'y':
            os.startfile(new_project_path)

    except Exception as e:
        print(f"创建副本时出错: {e}")
        # 清理失败创建的文件
        if new_project_path.exists():
            shutil.rmtree(new_project_path)

    input("\n按回车键退出...")


if __name__ == "__main__":
    create_project_copy()