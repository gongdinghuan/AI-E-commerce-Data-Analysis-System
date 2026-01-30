"""
AI 电商数据分析系统 - 全局配置

@Author: gongdinghuan
@Date: 2026-01-29
@Description: 系统全局配置，包含路径、LLM、应用参数等配置
"""
import os
from pathlib import Path

# ==========================================
# 路径配置
# ==========================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
DATABASE_DIR.mkdir(exist_ok=True)

# 数据库路径
DATABASE_PATH = DATABASE_DIR / "analytics.db"

# ==========================================
# LLM 配置 (支持多提供商)
# ==========================================
LLM_CONFIG = {
    "provider": os.getenv("LLM_PROVIDER", "deepseek"),  # deepseek, openai, ollama
    
    # DeepSeek 配置
    "deepseek": {
        "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
    },
    
    # OpenAI 配置
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
    },
    
    # Ollama 本地配置
    "ollama": {
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "model": os.getenv("OLLAMA_MODEL", "llama3"),
    },
}

# ==========================================
# 应用配置
# ==========================================
APP_CONFIG = {
    "title": "⚡ GDH·Jarvis 电商数据中控",
    "page_icon": "🤖",
    "layout": "wide",
    
    # 主题颜色 (钢铁侠风格)
    "colors": {
        "primary": "#00D4FF",      # 科技蓝
        "secondary": "#FF6B35",    # 警示橙
        "background": "#0A0A0F",   # 深色背景
        "card_bg": "#1A1A2E",      # 卡片背景
        "text": "#FFFFFF",         # 主文字
        "text_secondary": "#8892B0" # 次要文字
    }
}

# ==========================================
# 数据配置
# ==========================================
DATA_CONFIG = {
    # 模拟数据参数
    "n_orders": 10000,        # 订单数量
    "n_users": 500,           # 用户数量
    "n_products": 200,        # 商品数量
    "date_range_days": 180,   # 数据时间跨度(天)
    
    # 业务参数
    "refund_rate": 0.15,      # 基础退货率
    "categories": ["电子产品", "服装", "家居", "美妆", "食品", "运动"],
    "channels": ["直播", "搜索", "推荐", "活动", "复购"],
    "cities": ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "西安"],
}

# ==========================================
# RFM 分层配置
# ==========================================
RFM_CONFIG = {
    "n_clusters": 4,  # 聚类数量
    "labels": {
        0: "重要价值客户",
        1: "潜力发展客户", 
        2: "一般维护客户",
        3: "流失风险客户",
    },
    "strategies": {
        "重要价值客户": "VIP专属服务，优先体验新品，专属客服",
        "潜力发展客户": "个性化推荐，限时优惠，提升复购",
        "一般维护客户": "定期触达，节日营销，唤醒活动",
        "流失风险客户": "大额优惠券，召回短信，限时折扣",
    }
}
