"""
AI 电商数据分析系统 - 启动脚本
"""
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """检查依赖是否已安装"""
    try:
        import streamlit
        import duckdb
        import pandas
        import plotly
        import sklearn
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def generate_initial_data():
    """生成初始数据"""
    from config import DATA_DIR
    
    if not (DATA_DIR / 'orders.csv').exists():
        print("🚀 首次启动，生成模拟数据...")
        from utils.data_generator import generate_data
        generate_data()
        print()

def start_dashboard():
    """启动Streamlit Dashboard"""
    print("=" * 50)
    print("🚀 启动 Jarvis 电商数据中控")
    print("=" * 50)
    print()
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 生成数据
    generate_initial_data()
    
    # 启动Streamlit
    print("🌐 启动Dashboard服务...")
    print("📍 访问地址: http://localhost:8501")
    print()
    print("按 Ctrl+C 停止服务")
    print()
    
    # 2秒后打开浏览器
    time.sleep(2)
    webbrowser.open('http://localhost:8501')
    
    # 运行Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "dashboard.py",
        "--server.port=8501",
        "--server.headless=true",
        "--theme.base=dark"
    ])

def start_api():
    """启动FastAPI服务"""
    print("=" * 50)
    print("🚀 启动 Jarvis API 服务")
    print("=" * 50)
    print()
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 生成数据
    generate_initial_data()
    
    print("🌐 API服务启动中...")
    print("📍 API地址: http://localhost:8000")
    print("📚 文档地址: http://localhost:8000/docs")
    print()
    print("按 Ctrl+C 停止服务")
    print()
    
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "api.main:app",
        "--host=0.0.0.0",
        "--port=8000",
        "--reload"
    ])

def start_both():
    """同时启动Dashboard和API"""
    import threading
    
    print("=" * 50)
    print("🚀 启动完整服务 (Dashboard + API)")
    print("=" * 50)
    print()
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 生成数据
    generate_initial_data()
    
    print("🌐 Dashboard: http://localhost:8501")
    print("🔗 API: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print()
    
    # 在后台启动API
    api_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "api.main:app",
        "--host=0.0.0.0",
        "--port=8000"
    ])
    
    time.sleep(2)
    webbrowser.open('http://localhost:8501')
    
    # 前台运行Dashboard
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "dashboard.py",
            "--server.port=8501",
            "--server.headless=true",
            "--theme.base=dark"
        ])
    finally:
        api_process.terminate()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='AI 电商数据分析系统')
    parser.add_argument(
        'mode', 
        nargs='?', 
        default='dashboard',
        choices=['dashboard', 'api', 'both'],
        help='启动模式: dashboard(默认), api, both'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'dashboard':
        start_dashboard()
    elif args.mode == 'api':
        start_api()
    elif args.mode == 'both':
        start_both()
