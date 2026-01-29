"""
Jarvis AI 助手 - 自然语言数据分析

功能:
- Text-to-SQL 自然语言查询
- 数据解读和洞察生成
- 支持多LLM提供商 (DeepSeek/OpenAI/Ollama)
"""
import os
import json
import re
from typing import Optional, Dict, Any, List
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import LLM_CONFIG

# 尝试导入LLM相关库
try:
    from langchain_community.llms import Ollama
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠ LangChain未安装，AI功能将使用模拟模式")

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class JarvisAgent:
    """
    Jarvis AI 智能助手
    
    支持自然语言查询数据库，生成数据洞察
    """
    
    # 数据库表结构说明
    SCHEMA_DESCRIPTION = """
    数据库包含以下表:
    
    1. orders (订单表):
       - order_id: 订单ID
       - user_id: 用户ID
       - product_id: 商品ID
       - quantity: 购买数量
       - order_date: 订单日期
       - status: 订单状态 (已完成/已退款/待发货/已取消)
       - channel: 渠道 (直播/搜索/推荐/活动/复购)
       - discount: 折扣
       - price: 商品单价
       - cost: 成本
       - category: 商品类目 (电子产品/服装/家居/美妆/食品/运动)
       - amount: 订单金额
       - profit: 利润
       - city: 城市
    
    2. users (用户表):
       - user_id: 用户ID
       - username: 用户名
       - register_date: 注册日期
       - city: 城市
       - age: 年龄
       - gender: 性别
       - vip_level: VIP等级
    
    3. products (商品表):
       - product_id: 商品ID
       - product_name: 商品名称
       - category: 类目
       - price: 价格
       - cost: 成本
       - stock: 库存
       - rating: 评分
    """
    
    # SQL生成提示词
    SQL_PROMPT = """你是一个SQL专家。根据用户的自然语言问题，生成DuckDB SQL查询语句。

{schema}

注意事项:
1. 只返回SQL语句，不要有其他解释
2. 使用DuckDB语法
3. 日期函数使用 CURRENT_DATE, DATE_TRUNC 等
4. 确保SQL语法正确

用户问题: {question}

SQL查询:"""

    # 数据解读提示词
    INSIGHT_PROMPT = """你是一个电商数据分析专家，名叫Jarvis。请根据以下数据回答用户的问题。

用户问题: {question}

查询结果:
{data}

请用简洁专业的语言回答，包含:
1. 直接回答问题
2. 关键数据指标
3. 如果合适，给出业务建议

回答:"""

    def __init__(self, data_manager=None):
        """
        初始化Jarvis助手
        
        Args:
            data_manager: DataManager实例，用于执行SQL
        """
        self.data_manager = data_manager
        self.llm = None
        self.provider = LLM_CONFIG['provider']
        self._init_llm()
        
        # 对话历史
        self.conversation_history: List[Dict] = []
    
    def _init_llm(self):
        """初始化LLM"""
        if not LANGCHAIN_AVAILABLE:
            print("⚠ 使用模拟LLM模式")
            return
        
        try:
            if self.provider == 'ollama':
                config = LLM_CONFIG['ollama']
                self.llm = Ollama(
                    base_url=config['base_url'],
                    model=config['model']
                )
                print(f"✅ 已连接Ollama: {config['model']}")
                
            elif self.provider == 'openai':
                config = LLM_CONFIG['openai']
                if config['api_key']:
                    self.llm = ChatOpenAI(
                        api_key=config['api_key'],
                        model=config['model'],
                        base_url=config['base_url']
                    )
                    print(f"✅ 已连接OpenAI: {config['model']}")
                    
            elif self.provider == 'deepseek':
                config = LLM_CONFIG['deepseek']
                if config['api_key']:
                    self.llm = ChatOpenAI(
                        api_key=config['api_key'],
                        model=config['model'],
                        base_url=config['base_url']
                    )
                    print(f"✅ 已连接DeepSeek: {config['model']}")
                    
        except Exception as e:
            print(f"⚠ LLM初始化失败: {e}")
            self.llm = None
    
    def _call_llm(self, prompt: str) -> str:
        """调用LLM"""
        if self.llm is None:
            return self._simulate_response(prompt)
        
        try:
            if hasattr(self.llm, 'invoke'):
                response = self.llm.invoke(prompt)
                if hasattr(response, 'content'):
                    return response.content
                return str(response)
            else:
                return self.llm(prompt)
        except Exception as e:
            print(f"⚠ LLM调用失败: {e}")
            return self._simulate_response(prompt)
    
    def _simulate_response(self, prompt: str) -> str:
        """模拟LLM响应 (当LLM不可用时)"""
        # 检测是否是SQL生成请求
        if "SQL查询:" in prompt:
            return self._simulate_sql(prompt)
        else:
            return self._simulate_insight(prompt)
    
    def _simulate_sql(self, prompt: str) -> str:
        """模拟SQL生成"""
        prompt_lower = prompt.lower()
        
        # 常见查询模式匹配
        patterns = {
            ('top', '用户', '消费'): """
                SELECT user_id, SUM(amount) as total_spend, COUNT(*) as order_count
                FROM orders WHERE status = '已完成'
                GROUP BY user_id ORDER BY total_spend DESC LIMIT 10
            """,
            ('退货率', '城市'): """
                SELECT city, 
                    COUNT(CASE WHEN status = '已退款' THEN 1 END) * 100.0 / COUNT(*) as refund_rate,
                    COUNT(*) as total_orders
                FROM orders GROUP BY city ORDER BY refund_rate DESC
            """,
            ('销售额', '类目', '品类'): """
                SELECT category, SUM(amount) as gmv, COUNT(*) as orders
                FROM orders WHERE status = '已完成'
                GROUP BY category ORDER BY gmv DESC
            """,
            ('渠道', '分析'): """
                SELECT channel, SUM(amount) as gmv, COUNT(DISTINCT user_id) as users
                FROM orders WHERE status = '已完成'
                GROUP BY channel ORDER BY gmv DESC
            """,
            ('每日', '日销', '趋势'): """
                SELECT DATE_TRUNC('day', order_date) as date, 
                    SUM(amount) as daily_sales, COUNT(*) as orders
                FROM orders WHERE status = '已完成'
                GROUP BY DATE_TRUNC('day', order_date)
                ORDER BY date DESC LIMIT 30
            """,
            ('top', '商品', '销量'): """
                SELECT product_id, SUM(quantity) as total_qty, SUM(amount) as revenue
                FROM orders WHERE status = '已完成'
                GROUP BY product_id ORDER BY total_qty DESC LIMIT 10
            """,
        }
        
        for keywords, sql in patterns.items():
            if all(kw in prompt_lower for kw in keywords):
                return sql.strip()
        
        # 默认查询
        return "SELECT * FROM orders LIMIT 10"
    
    def _simulate_insight(self, prompt: str) -> str:
        """模拟数据洞察"""
        return "基于数据分析，我发现以下关键信息。请查看上方的数据表格了解详细信息。如需更深入的分析，请配置LLM API密钥。"
    
    def text_to_sql(self, question: str) -> str:
        """
        将自然语言转换为SQL
        
        Args:
            question: 自然语言问题
            
        Returns:
            SQL查询语句
        """
        prompt = self.SQL_PROMPT.format(
            schema=self.SCHEMA_DESCRIPTION,
            question=question
        )
        
        sql = self._call_llm(prompt)
        
        # 清理SQL (移除markdown代码块标记等)
        sql = re.sub(r'```sql\s*', '', sql)
        sql = re.sub(r'```\s*', '', sql)
        sql = sql.strip()
        
        return sql
    
    def generate_insight(self, question: str, data: pd.DataFrame) -> str:
        """
        生成数据洞察
        
        Args:
            question: 用户问题
            data: 查询结果数据
            
        Returns:
            洞察文本
        """
        # 将DataFrame转为简洁文本
        data_str = data.head(20).to_string() if len(data) > 0 else "无数据"
        
        prompt = self.INSIGHT_PROMPT.format(
            question=question,
            data=data_str
        )
        
        return self._call_llm(prompt)
    
    def chat(self, question: str) -> Dict[str, Any]:
        """
        对话式数据分析
        
        Args:
            question: 用户问题
            
        Returns:
            包含SQL、数据、洞察的字典
        """
        result = {
            'question': question,
            'sql': None,
            'data': None,
            'insight': None,
            'error': None
        }
        
        try:
            # 1. 生成SQL
            sql = self.text_to_sql(question)
            result['sql'] = sql
            
            # 2. 执行查询
            if self.data_manager:
                try:
                    data = self.data_manager.query(sql)
                    result['data'] = data
                    
                    # 3. 生成洞察
                    insight = self.generate_insight(question, data)
                    result['insight'] = insight
                    
                except Exception as e:
                    result['error'] = f"SQL执行错误: {str(e)}"
            else:
                result['error'] = "数据管理器未初始化"
                
        except Exception as e:
            result['error'] = f"处理失败: {str(e)}"
        
        # 记录对话历史
        self.conversation_history.append({
            'role': 'user',
            'content': question
        })
        self.conversation_history.append({
            'role': 'assistant',
            'content': result.get('insight', result.get('error', ''))
        })
        
        return result
    
    def quick_answer(self, question: str) -> str:
        """
        快速回答常见问题
        
        Args:
            question: 用户问题
            
        Returns:
            回答文本
        """
        # 预定义的快速回答
        quick_answers = {
            '帮助': """
我是Jarvis，您的AI数据分析助手。我可以帮您:

📊 **数据查询**: "找出消费最高的10个用户"
📈 **趋势分析**: "最近一周的销售趋势"
🔍 **问题诊断**: "为什么北京退货率这么高"
💡 **业务建议**: "如何提高复购率"

直接用自然语言告诉我您想了解什么！
            """,
            '你是谁': "我是Jarvis，一个基于AI的电商数据分析助手。我可以帮助您用自然语言查询和分析电商数据。",
        }
        
        for key, answer in quick_answers.items():
            if key in question:
                return answer
        
        return None
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []


# 快捷函数
def create_jarvis(data_manager=None) -> JarvisAgent:
    """创建Jarvis实例"""
    return JarvisAgent(data_manager)


if __name__ == "__main__":
    # 测试代码
    from data_manager import get_data_manager
    
    dm = get_data_manager()
    dm.load_csv_to_db()
    
    jarvis = JarvisAgent(dm)
    
    # 测试查询
    result = jarvis.chat("找出消费金额最高的前5名用户")
    print("SQL:", result['sql'])
    print("Data:", result['data'])
    print("Insight:", result['insight'])
