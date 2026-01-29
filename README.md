# ⚡ Jarvis 电商数据中控

一个基于 AI 的电商数据分析系统，采用"钢铁侠"风格设计，支持自然语言查询、用户智能分层、销售预测等功能。

![架构](https://img.shields.io/badge/架构-三层架构-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ 功能特性

### 📊 数据分析
- **核心KPI监控**: GMV、订单数、退货率、客单价、复购率
- **RFM用户分层**: 使用K-Means智能聚类，自动识别高价值客户
- **漏斗分析**: 浏览→加购→下单→支付转化率分析
- **销售预测**: 基于历史数据的线性回归预测

### 🤖 AI 助手 (Jarvis)
- **自然语言查询**: 用中文提问，自动生成SQL并返回结果
- **数据洞察**: AI自动解读数据，给出业务建议
- **多LLM支持**: 支持DeepSeek、OpenAI、Ollama本地模型

### 🎨 可视化
- **钢铁侠风格UI**: 深色科技风格，霓虹光效
- **3D用户分布图**: Plotly 3D散点图展示RFM聚类
- **交互式图表**: 支持缩放、拖拽、筛选

## 🚀 快速开始

### 1. 安装依赖

```bash
cd c:\Users\Administrator\dianshangshujufenxi
pip install -r requirements.txt
```

### 2. 启动Dashboard

```bash
python run.py dashboard
```

访问 http://localhost:8501 查看数据大屏

### 3. 启动API服务

```bash
python run.py api
```

访问 http://localhost:8000/docs 查看API文档

### 4. 同时启动

```bash
python run.py both
```

## 📁 项目结构

```
ecommerce_ai_brain/
├── config.py              # 全局配置
├── run.py                 # 启动脚本
├── dashboard.py           # Streamlit 主界面
├── requirements.txt       # 依赖文件
├── data/                  # 数据目录
│   ├── users.csv         
│   ├── products.csv      
│   ├── orders.csv        
│   └── funnel.csv        
├── database/             
│   └── analytics.db       # DuckDB 数据库
├── core/                  # 核心模块
│   ├── data_manager.py    # 数据管理 (ETL)
│   ├── analyzer.py        # 分析引擎
│   └── jarvis_agent.py    # AI 助手
├── api/                  
│   └── main.py            # FastAPI 服务
└── utils/                
    └── data_generator.py  # 数据生成器
```

## ⚙️ 配置LLM

编辑 `config.py` 或设置环境变量:

### DeepSeek (推荐)
```bash
set DEEPSEEK_API_KEY=your_api_key
set LLM_PROVIDER=deepseek
```

### OpenAI
```bash
set OPENAI_API_KEY=your_api_key
set LLM_PROVIDER=openai
```

### Ollama (本地)
```bash
set OLLAMA_BASE_URL=http://localhost:11434
set LLM_PROVIDER=ollama
set OLLAMA_MODEL=llama3
```

## 📖 API 接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/kpi` | GET | 获取核心KPI |
| `/api/rfm` | GET | RFM用户分层 |
| `/api/funnel` | GET | 漏斗分析 |
| `/api/forecast` | GET | 销售预测 |
| `/api/chat` | POST | AI对话 |
| `/api/stats/category` | GET | 品类统计 |
| `/api/stats/channel` | GET | 渠道统计 |
| `/api/stats/city` | GET | 城市统计 |

## 🎮 使用示例

### 自然语言查询

```
"找出消费金额最高的前10名用户"
"分析各城市的退货率"
"最近一周的销售趋势如何"
"哪个渠道的转化效果最好"
```

### API调用

```python
import requests

# 获取KPI
response = requests.get("http://localhost:8000/api/kpi")
print(response.json())

# AI对话
response = requests.post(
    "http://localhost:8000/api/chat",
    json={"question": "找出消费最高的用户"}
)
print(response.json())
```

## 🛠️ 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| 交互层 | Streamlit, Plotly | 可视化大屏 |
| API层 | FastAPI | REST API |
| AI层 | LangChain, LLM | 自然语言处理 |
| 计算层 | Pandas, Scikit-learn | 数据分析、ML |
| 数据层 | DuckDB | 嵌入式分析数据库 |

## 📝 License

MIT License
