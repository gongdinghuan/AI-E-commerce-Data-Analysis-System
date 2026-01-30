# ⚡ Jarvis 电商数据中控

> 一个基于 AI 的电商数据分析系统，采用"钢铁侠"风格设计，支持自然语言查询、用户智能分层、销售预测等功能。

![架构](https://img.shields.io/badge/架构-三层架构-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Streamlit](https://img.shields.io/badge/Streamlit-1.53+-red)

## 📖 目录

- [功能特性](#-功能特性)
- [系统要求](#-系统要求)
- [快速开始](#-快速开始)
- [项目结构](#-项目结构)
- [配置说明](#-配置说明)
- [API 接口](#-api-接口)
- [使用示例](#-使用示例)
- [技术栈](#-技术栈)
- [开发指南](#-开发指南)
- [故障排除](#-故障排除)
- [贡献指南](#-贡献指南)

## ✨ 功能特性

### 📊 数据分析
- **核心KPI监控**: GMV、订单数、退货率、客单价、复购率
- **RFM用户分层**: 使用K-Means智能聚类，自动识别高价值客户
- **漏斗分析**: 浏览→加购→下单→支付转化率分析
- **销售预测**: 基于历史数据的线性回归预测
- **多维度统计**: 按品类、渠道、城市等维度分析

### 🤖 AI 助手 (Jarvis)
- **自然语言查询**: 用中文提问，自动生成SQL并返回结果
- **数据洞察**: AI自动解读数据，给出业务建议
- **多LLM支持**: 支持DeepSeek、OpenAI、Ollama本地模型
- **模拟模式**: 无需API Key即可体验基础功能

### 🎨 可视化
- **钢铁侠风格UI**: 深色科技风格，霓虹光效
- **3D用户分布图**: Plotly 3D散点图展示RFM聚类
- **交互式图表**: 支持缩放、拖拽、筛选
- **响应式设计**: 适配不同屏幕尺寸

## 💻 系统要求

- **Python**: 3.9 或更高版本
- **操作系统**: Windows / macOS / Linux
- **内存**: 建议 4GB 以上
- **磁盘空间**: 至少 500MB

## 🚀 快速开始

### 方式一：使用虚拟环境（推荐）

```bash
# 1. 克隆或下载项目
cd dianshangshujufenxi

# 2. 创建虚拟环境
python -m venv .venv

# 3. 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 启动 Dashboard
python run.py dashboard
```

### 方式二：直接安装

```bash
# 1. 进入项目目录
cd dianshangshujufenxi

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动 Dashboard
python run.py dashboard
```

### 启动选项

```bash
# 仅启动 Dashboard (默认)
python run.py dashboard

# 仅启动 API 服务
python run.py api

# 同时启动 Dashboard 和 API
python run.py both
```

### 访问地址

启动成功后，可以通过以下地址访问：

- **Dashboard**: http://localhost:8501
- **API 文档**: http://localhost:8000/docs
- **API 端点**: http://localhost:8000/api

## 📁 项目结构

```
dianshangshujufenxi/
├── config.py              # 全局配置文件
├── run.py                 # 启动脚本
├── dashboard.py           # Streamlit 主界面
├── requirements.txt       # Python 依赖
├── README.md             # 项目文档
│
├── data/                  # 数据目录（自动生成）
│   ├── users.csv         # 用户数据
│   ├── products.csv      # 商品数据
│   ├── orders.csv        # 订单数据
│   └── funnel.csv       # 漏斗数据
│
├── database/             # 数据库目录（自动生成）
│   └── analytics.db     # DuckDB 数据库
│
├── core/                # 核心业务模块
│   ├── __init__.py
│   ├── data_manager.py   # 数据管理 (ETL)
│   ├── analyzer.py       # 分析引擎
│   └── jarvis_agent.py  # AI 助手
│
├── api/                 # API 服务模块
│   ├── __init__.py
│   └── main.py         # FastAPI 服务
│
└── utils/               # 工具模块
    ├── __init__.py
    └── data_generator.py # 数据生成器
```

## ⚙️ 配置说明

### LLM 配置

系统支持三种 LLM 提供商，可通过环境变量或直接修改 `config.py` 配置。

#### DeepSeek（推荐）

```bash
# Windows CMD
set DEEPSEEK_API_KEY=your_api_key_here
set LLM_PROVIDER=deepseek

# Windows PowerShell
$env:DEEPSEEK_API_KEY="your_api_key_here"
$env:LLM_PROVIDER="deepseek"

# macOS/Linux
export DEEPSEEK_API_KEY=your_api_key_here
export LLM_PROVIDER=deepseek
```

或在 `config.py` 中直接配置：

```python
LLM_CONFIG = {
    "provider": "deepseek",
    "deepseek": {
        "api_key": "your_api_key_here",
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
    },
}
```

#### OpenAI

```bash
set OPENAI_API_KEY=your_api_key_here
set LLM_PROVIDER=openai
```

#### Ollama（本地模型）

```bash
set LLM_PROVIDER=ollama
set OLLAMA_BASE_URL=http://localhost:11434
set OLLAMA_MODEL=llama3
```

### 数据配置

在 `config.py` 中可以调整数据生成参数：

```python
DATA_CONFIG = {
    "n_orders": 10000,        # 订单数量
    "n_users": 500,           # 用户数量
    "n_products": 200,        # 商品数量
    "date_range_days": 180,   # 数据时间跨度(天)
    "refund_rate": 0.15,      # 基础退货率
}
```

### RFM 分层配置

```python
RFM_CONFIG = {
    "n_clusters": 4,  # 聚类数量
    "labels": {
        0: "重要价值客户",
        1: "潜力发展客户", 
        2: "一般维护客户",
        3: "流失风险客户",
    },
}
```

## 📖 API 接口

### 核心端点

| 端点 | 方法 | 说明 | 参数 |
|------|------|------|------|
| `/api/kpi` | GET | 获取核心KPI | 无 |
| `/api/rfm` | GET | RFM用户分层 | 无 |
| `/api/funnel` | GET | 漏斗分析 | 无 |
| `/api/forecast` | GET | 销售预测 | `days` (默认7) |
| `/api/chat` | POST | AI对话 | `{"question": "问题"}` |
| `/api/stats/category` | GET | 品类统计 | 无 |
| `/api/stats/channel` | GET | 渠道统计 | 无 |
| `/api/stats/city` | GET | 城市统计 | 无 |
| `/api/users/top` | GET | Top用户 | `limit` (默认10) |
| `/api/products/top` | GET | Top商品 | `limit` (默认10) |

### API 示例

```python
import requests

BASE_URL = "http://localhost:8000"

# 获取 KPI
response = requests.get(f"{BASE_URL}/api/kpi")
kpi_data = response.json()
print(f"GMV: {kpi_data['gmv']}")

# RFM 分析
response = requests.get(f"{BASE_URL}/api/rfm")
rfm_data = response.json()
print(f"聚类数量: {len(rfm_data['clusters'])}")

# AI 对话
response = requests.post(
    f"{BASE_URL}/api/chat",
    json={"question": "找出消费最高的10个用户"}
)
result = response.json()
print(f"SQL: {result['sql']}")
print(f"数据: {result['data']}")
print(f"洞察: {result['insight']}")
```

## 🎮 使用示例

### 自然语言查询

在 Dashboard 的 AI 助手区域，可以直接用自然语言提问：

```
"找出消费金额最高的前10名用户"
"分析各城市的退货率"
"最近一周的销售趋势如何"
"哪个渠道的转化效果最好"
"电子产品类目的销售额是多少"
"北京和上海的GMV对比"
```

### 快捷问题

系统预置了常用快捷问题，点击即可快速查询：
- 消费最高的用户
- 各品类销售排行
- 渠道转化率分析
- 城市退货率对比

### 数据刷新

- **刷新数据**: 清除缓存，重新加载数据
- **重新生成数据**: 删除现有数据，生成新的模拟数据

## 🛠️ 技术栈

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 交互层 | Streamlit | 1.53+ | 可视化大屏 |
| 交互层 | Plotly | 5.18+ | 交互式图表 |
| API层 | FastAPI | 0.104+ | REST API |
| API层 | Uvicorn | 0.24+ | ASGI 服务器 |
| AI层 | LangChain | 0.1+ | LLM 集成 |
| AI层 | OpenAI SDK | 1.0+ | LLM 接口 |
| 计算层 | Pandas | 2.0+ | 数据处理 |
| 计算层 | NumPy | 1.24+ | 数值计算 |
| 计算层 | Scikit-learn | 1.3+ | 机器学习 |
| 数据层 | DuckDB | 0.9+ | 嵌入式分析数据库 |

## 👨‍💻 开发指南

### 本地开发

```bash
# 1. 克隆项目
git clone <repository-url>
cd dianshangshujufenxi

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 安装开发依赖
pip install -r requirements.txt

# 4. 启动开发服务器
python run.py dashboard
```

### 代码规范

- 遵循 PEP 8 代码风格
- 所有函数和类添加文档字符串
- 使用类型注解提高代码可读性
- 在文件头部添加作者信息

### 测试

```bash
# 运行测试（如果有）
python -m pytest tests/

# 代码格式检查
black .
flake8 .
```

## 🔧 故障排除

### 常见问题

**Q: 启动时提示 "LangChain未安装"**

A: 虽然已安装 LangChain，但可能缺少特定组件。运行：
```bash
pip install langchain langchain-community langchain-openai langchain-core
```

**Q: AI 功能显示 "使用模拟LLM模式"**

A: 需要配置 LLM API Key。参考 [配置说明](#-配置说明) 章节。

**Q: 数据库连接失败**

A: 检查 `database/` 目录是否存在，确保有写入权限。

**Q: Streamlit 启动失败**

A: 确保端口 8501 未被占用，或修改 `run.py` 中的端口号。

**Q: 图表显示异常**

A: 清除浏览器缓存或使用无痕模式重试。

### 日志查看

Dashboard 和 API 的运行日志会输出到终端，包含：
- 数据加载状态
- LLM 连接状态
- 错误信息

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 贡献类型

- 🐛 Bug 修复
- ✨ 新功能
- 📝 文档改进
- 🎨 代码优化
- ⚡ 性能提升

## 📝 License

本项目采用 MIT License - 详见 [LICENSE](LICENSE) 文件

## 👤 作者

**龚玎焕** - [@gongdinghuan](https://github.com/gongdinghuan)

## 🙏 致谢

感谢以下开源项目：

- [Streamlit](https://streamlit.io/) - 数据可视化框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化 Web 框架
- [LangChain](https://langchain.com/) - LLM 应用开发框架
- [Plotly](https://plotly.com/) - 交互式图表库
- [DuckDB](https://duckdb.org/) - 嵌入式分析数据库

---

⭐ 如果这个项目对你有帮助，请给个 Star！
