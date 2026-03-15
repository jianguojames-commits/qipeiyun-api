#!/usr/bin/env python3
"""
汽配云助手 - 启动脚本

一键启动所有服务

使用说明:
    python start.py              # 启动主界面
    python start.py --api       # 启动API服务
    python start.py --viz       # 启动可视化
    python start.py --all       # 启动所有服务
"""

import sys
import os
import subprocess
from pathlib import Path
import argparse

# 颜色定义
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

PROJECT_ROOT = Path(__file__).parent


def print_banner():
    """打印启动横幅"""
    print(f"""
{GREEN}╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🚗  汽配云助手 - Auto Parts Management System         ║
║                                                           ║
║   版本: 2.1.0                                          ║
║   作者: 汽配云团队                                       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝{RESET}
""")


def check_database():
    """检查数据库"""
    db_path = PROJECT_ROOT / "data" / "qipeiyun.db"
    if not db_path.exists():
        print(f"{YELLOW}⚠️  数据库文件不存在{RESET}")
        print(f"   请先运行: python migrate_to_sqlite.py")
        return False
    return True


def start_web_app():
    """启动Web主界面"""
    print(f"{BLUE}🚀 启动Web管理界面...{RESET}")
    print(f"   地址: http://localhost:5000")
    print(f"   按 Ctrl+C 停止\n")

    os.chdir(PROJECT_ROOT)
    subprocess.run([sys.executable, "web_app_flask.py"])


def start_api():
    """启动API服务"""
    print(f"{BLUE}🚀 启动API服务...{RESET}")
    print(f"   地址: http://localhost:8000")
    print(f"   文档: http://localhost:8000/docs")
    print(f"   按 Ctrl+C 停止\n")

    os.chdir(PROJECT_ROOT)
    subprocess.run([sys.executable, "api_server_auth.py"])


def start_viz():
    """启动可视化"""
    print(f"{BLUE}🚀 启动数据可视化...{RESET}")
    print(f"   地址: http://localhost:5001")
    print(f"   按 Ctrl+C 停止\n")

    os.chdir(PROJECT_ROOT)
    subprocess.run([sys.executable, "web_app_viz.py"])


def start_all():
    """启动所有服务"""
    print(f"{GREEN}📦 启动所有服务...{RESET}\n")

    # 使用不同的终端启动各个服务
    processes = []

    # Web主界面
    print(f"{BLUE}1. 启动Web管理界面...{RESET}")
    print(f"   地址: http://localhost:5000")
    p1 = subprocess.Popen([sys.executable, "web_app_flask.py"], cwd=PROJECT_ROOT)
    processes.append(("Web", p1))

    # API服务
    print(f"{BLUE}2. 启动API服务...{RESET}")
    print(f"   地址: http://localhost:8000")
    p2 = subprocess.Popen([sys.executable, "api_server_auth.py"], cwd=PROJECT_ROOT)
    processes.append(("API", p2))

    # 可视化
    print(f"{BLUE}3. 启动数据可视化...{RESET}")
    print(f"   地址: http://localhost:5001")
    p3 = subprocess.Popen([sys.executable, "web_app_viz.py"], cwd=PROJECT_ROOT)
    processes.append(("Viz", p3))

    print(f"\n{GREEN}✅ 所有服务已启动!{RESET}")
    print(f"\n服务地址:")
    print(f"   🌐 Web管理界面: http://localhost:5000")
    print(f"   📡 API服务:     http://localhost:8000")
    print(f"   📊 数据可视化:  http://localhost:5001")
    print(f"\n按 Ctrl+C 停止所有服务")

    try:
        # 等待所有进程
        for name, p in processes:
            p.wait()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}🛑 停止所有服务...{RESET}")
        for name, p in processes:
            p.terminate()
            print(f"   {name} 已停止")


def main():
    parser = argparse.ArgumentParser(description="汽配云助手启动脚本")
    parser.add_argument("--web", action="store_true", help="启动Web管理界面")
    parser.add_argument("--api", action="store_true", help="启动API服务")
    parser.add_argument("--viz", action="store_true", help="启动数据可视化")
    parser.add_argument("--all", action="store_true", help="启动所有服务")

    args = parser.parse_args()

    print_banner()

    # 检查数据库
    if not args.web and not args.api and not args.viz and not args.all:
        # 默认启动Web
        args.web = True

    if args.all:
        if not check_database():
            return
        start_all()
    else:
        if args.web:
            if not check_database():
                return
            start_web_app()
        if args.api:
            start_api()
        if args.viz:
            start_viz()


if __name__ == "__main__":
    main()
