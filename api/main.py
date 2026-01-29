"""
FastAPI 服务 - REST API 接口

提供:
- 数据查询API
- AI分析API
- 健康检查
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.data_manager import DataManager, get_data_manager
from core.analyzer import EcommerceAnalyzer
from core.jarvis_agent import JarvisAgent
from utils.data_generator import generate_data

# 创建FastAPI应用
app = FastAPI(
    title="Jarvis 电商数据分析 API",
    description="AI驱动的电商数据分析服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 数据模型
# ==========================================

class ChatRequest(BaseModel):
    """聊天请求"""
    question: str

class ChatResponse(BaseModel):
    """聊天响应"""
    question: str
    sql: Optional[str] = None
    data: Optional[List[Dict]] = None
    insight: Optional[str] = None
    error: Optional[str] = None

class KPIResponse(BaseModel):
    """KPI响应"""
    gmv: float
    total_orders: int
    paid_orders: int
    refund_rate: float
    aov: float
    profit: float
    unique_users: int
    repeat_rate: float

# ==========================================
# 全局状态
# ==========================================

data_manager: DataManager = None
jarvis: JarvisAgent = None

@app.on_event("startup")
async def startup_event():
    """应用启动初始化"""
    global data_manager, jarvis
    
    data_manager = get_data_manager()
    
    # 检查是否需要生成数据
    from config import DATA_DIR
    if not (DATA_DIR / 'orders.csv').exists():
        print("🚀 首次启动，生成模拟数据...")
        generate_data()
    
    # 加载数据到数据库
    data_manager.load_csv_to_db()
    
    # 初始化Jarvis
    jarvis = JarvisAgent(data_manager)
    
    print("✅ API服务启动成功")

# ==========================================
# API 端点
# ==========================================

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用 Jarvis 电商数据分析 API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "jarvis-api"}

# ==========================================
# KPI 相关
# ==========================================

@app.get("/api/kpi", response_model=KPIResponse)
async def get_kpi():
    """获取核心KPI指标"""
    try:
        orders = data_manager.get_orders()
        analyzer = EcommerceAnalyzer(orders)
        kpi = analyzer.get_kpi()
        return kpi
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/kpi/trend")
async def get_kpi_trend(days: int = Query(default=7, ge=1, le=90)):
    """获取KPI趋势"""
    try:
        orders = data_manager.get_orders()
        analyzer = EcommerceAnalyzer(orders)
        trend = analyzer.get_kpi_trend(days)
        return trend
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# RFM 分析
# ==========================================

@app.get("/api/rfm")
async def get_rfm_analysis(n_clusters: int = Query(default=4, ge=2, le=8)):
    """获取RFM用户分层"""
    try:
        orders = data_manager.get_orders()
        analyzer = EcommerceAnalyzer(orders)
        rfm_data, summary = analyzer.perform_rfm_clustering(n_clusters)
        
        return {
            "data": rfm_data.to_dict('records'),
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 漏斗分析
# ==========================================

@app.get("/api/funnel")
async def get_funnel():
    """获取漏斗分析"""
    try:
        orders = data_manager.get_orders()
        analyzer = EcommerceAnalyzer(orders)
        funnel = analyzer.get_funnel_analysis()
        
        return funnel.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 销售预测
# ==========================================

@app.get("/api/forecast")
async def get_forecast(days: int = Query(default=7, ge=1, le=30)):
    """获取销售预测"""
    try:
        orders = data_manager.get_orders()
        analyzer = EcommerceAnalyzer(orders)
        forecast = analyzer.forecast_sales(days)
        
        return forecast.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 维度分析
# ==========================================

@app.get("/api/stats/category")
async def get_category_stats():
    """获取品类统计"""
    try:
        stats = data_manager.get_category_stats()
        return stats.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/channel")
async def get_channel_stats():
    """获取渠道统计"""
    try:
        stats = data_manager.get_channel_stats()
        return stats.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/city")
async def get_city_stats():
    """获取城市统计"""
    try:
        stats = data_manager.get_city_stats()
        return stats.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/daily")
async def get_daily_stats(days: int = Query(default=30, ge=1, le=180)):
    """获取每日统计"""
    try:
        stats = data_manager.get_daily_stats(days)
        return stats.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# Top排行
# ==========================================

@app.get("/api/top/users")
async def get_top_users(n: int = Query(default=10, ge=1, le=100)):
    """获取Top消费用户"""
    try:
        orders = data_manager.get_orders()
        analyzer = EcommerceAnalyzer(orders)
        top_users = analyzer.get_top_users(n)
        
        return top_users.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/top/products")
async def get_top_products(n: int = Query(default=10, ge=1, le=100)):
    """获取Top销售商品"""
    try:
        orders = data_manager.get_orders()
        analyzer = EcommerceAnalyzer(orders)
        top_products = analyzer.get_top_products(n)
        
        return top_products.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# AI 对话
# ==========================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """AI对话接口"""
    try:
        result = jarvis.chat(request.question)
        
        # 转换DataFrame为列表
        if result.get('data') is not None:
            result['data'] = result['data'].to_dict('records')
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/history")
async def get_chat_history():
    """获取对话历史"""
    return jarvis.conversation_history

@app.delete("/api/chat/history")
async def clear_chat_history():
    """清空对话历史"""
    jarvis.clear_history()
    return {"message": "对话历史已清空"}

# ==========================================
# 数据管理
# ==========================================

@app.post("/api/data/reload")
async def reload_data():
    """重新加载数据"""
    try:
        generate_data()
        data_manager.load_csv_to_db(force_reload=True)
        return {"message": "数据已重新生成和加载"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/schema")
async def get_schema():
    """获取数据库表结构"""
    try:
        schema = data_manager.get_table_schema()
        return schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
