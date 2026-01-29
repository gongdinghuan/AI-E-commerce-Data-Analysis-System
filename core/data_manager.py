"""
数据管理模块 - DataManager

@Author: gongdinghuan
@Date: 2026-01-29
@Description: 负责ETL数据处理和DuckDB数据库管理
"""
import duckdb
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DATABASE_PATH, DATA_DIR


class DataManager:
    """数据管理类 - 处理ETL和数据库操作"""
    
    def __init__(self, db_path: Path = DATABASE_PATH):
        """
        初始化数据管理器
        
        Args:
            db_path: DuckDB数据库文件路径
        """
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._init_tables()
    
    def _connect(self):
        """连接DuckDB数据库"""
        self.conn = duckdb.connect(str(self.db_path))
        print(f"✅ 已连接数据库: {self.db_path}")
    
    def _init_tables(self):
        """初始化数据表结构"""
        # 用户表
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id VARCHAR PRIMARY KEY,
                username VARCHAR,
                register_date TIMESTAMP,
                city VARCHAR,
                age INTEGER,
                gender VARCHAR,
                vip_level INTEGER
            )
        """)
        
        # 商品表
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id VARCHAR PRIMARY KEY,
                product_name VARCHAR,
                category VARCHAR,
                price DOUBLE,
                cost DOUBLE,
                stock INTEGER,
                rating DOUBLE
            )
        """)
        
        # 订单表
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id VARCHAR PRIMARY KEY,
                user_id VARCHAR,
                product_id VARCHAR,
                quantity INTEGER,
                order_date TIMESTAMP,
                status VARCHAR,
                channel VARCHAR,
                discount DOUBLE,
                price DOUBLE,
                cost DOUBLE,
                category VARCHAR,
                amount DOUBLE,
                profit DOUBLE,
                city VARCHAR
            )
        """)
        
        # 漏斗数据表
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS funnel (
                stage VARCHAR,
                count INTEGER,
                date TIMESTAMP
            )
        """)
    
    def load_csv_to_db(self, force_reload: bool = False) -> bool:
        """
        从CSV文件加载数据到数据库
        
        Args:
            force_reload: 是否强制重新加载数据
            
        Returns:
            是否成功加载
        """
        try:
            # 检查是否已有数据
            count = self.conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
            if count > 0 and not force_reload:
                print(f"📊 数据库已有 {count} 条订单记录，跳过加载")
                return True
            
            # 清空现有数据
            if force_reload:
                self.conn.execute("DELETE FROM users")
                self.conn.execute("DELETE FROM products")
                self.conn.execute("DELETE FROM orders")
                self.conn.execute("DELETE FROM funnel")
            
            # 加载CSV文件
            csv_files = {
                'users': DATA_DIR / 'users.csv',
                'products': DATA_DIR / 'products.csv',
                'orders': DATA_DIR / 'orders.csv',
                'funnel': DATA_DIR / 'funnel.csv'
            }
            
            for table_name, csv_path in csv_files.items():
                if csv_path.exists():
                    df = pd.read_csv(csv_path)
                    self.conn.execute(f"INSERT INTO {table_name} SELECT * FROM df")
                    print(f"  ✓ 加载 {table_name}: {len(df)} 条记录")
                else:
                    print(f"  ⚠ 文件不存在: {csv_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ 加载数据失败: {e}")
            return False
    
    def query(self, sql: str) -> pd.DataFrame:
        """
        执行SQL查询
        
        Args:
            sql: SQL查询语句
            
        Returns:
            查询结果DataFrame
        """
        return self.conn.execute(sql).df()
    
    def get_orders(
        self, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        city: Optional[str] = None,
        limit: int = None
    ) -> pd.DataFrame:
        """
        获取订单数据 (带筛选条件)
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            status: 订单状态
            category: 商品类别
            city: 城市
            limit: 返回条数限制
            
        Returns:
            订单DataFrame
        """
        sql = "SELECT * FROM orders WHERE 1=1"
        
        if start_date:
            sql += f" AND order_date >= '{start_date}'"
        if end_date:
            sql += f" AND order_date <= '{end_date}'"
        if status:
            sql += f" AND status = '{status}'"
        if category:
            sql += f" AND category = '{category}'"
        if city:
            sql += f" AND city = '{city}'"
        
        sql += " ORDER BY order_date DESC"
        
        if limit:
            sql += f" LIMIT {limit}"
        
        return self.query(sql)
    
    def get_users(self) -> pd.DataFrame:
        """获取所有用户数据"""
        return self.query("SELECT * FROM users")
    
    def get_products(self) -> pd.DataFrame:
        """获取所有商品数据"""
        return self.query("SELECT * FROM products")
    
    def get_funnel(self) -> pd.DataFrame:
        """获取漏斗数据"""
        return self.query("SELECT * FROM funnel ORDER BY count DESC")
    
    def get_daily_stats(self, days: int = 30) -> pd.DataFrame:
        """
        获取每日统计数据
        
        Args:
            days: 统计天数
            
        Returns:
            每日统计DataFrame
        """
        sql = f"""
            SELECT 
                DATE_TRUNC('day', order_date) as date,
                COUNT(*) as order_count,
                SUM(CASE WHEN status = '已完成' THEN amount ELSE 0 END) as gmv,
                SUM(CASE WHEN status = '已完成' THEN profit ELSE 0 END) as profit,
                COUNT(DISTINCT user_id) as unique_users,
                AVG(amount) as avg_order_value,
                SUM(CASE WHEN status = '已退款' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as refund_rate
            FROM orders
            WHERE order_date >= CURRENT_DATE - INTERVAL '{days} days'
            GROUP BY DATE_TRUNC('day', order_date)
            ORDER BY date
        """
        return self.query(sql)
    
    def get_category_stats(self) -> pd.DataFrame:
        """获取品类统计"""
        sql = """
            SELECT 
                category,
                COUNT(*) as order_count,
                SUM(CASE WHEN status = '已完成' THEN amount ELSE 0 END) as gmv,
                SUM(CASE WHEN status = '已完成' THEN profit ELSE 0 END) as profit,
                SUM(CASE WHEN status = '已退款' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as refund_rate
            FROM orders
            GROUP BY category
            ORDER BY gmv DESC
        """
        return self.query(sql)
    
    def get_channel_stats(self) -> pd.DataFrame:
        """获取渠道统计"""
        sql = """
            SELECT 
                channel,
                COUNT(*) as order_count,
                SUM(CASE WHEN status = '已完成' THEN amount ELSE 0 END) as gmv,
                COUNT(DISTINCT user_id) as unique_users,
                AVG(amount) as avg_order_value
            FROM orders
            GROUP BY channel
            ORDER BY gmv DESC
        """
        return self.query(sql)
    
    def get_city_stats(self) -> pd.DataFrame:
        """获取城市统计"""
        sql = """
            SELECT 
                city,
                COUNT(*) as order_count,
                SUM(CASE WHEN status = '已完成' THEN amount ELSE 0 END) as gmv,
                COUNT(DISTINCT user_id) as unique_users,
                SUM(CASE WHEN status = '已退款' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as refund_rate
            FROM orders
            GROUP BY city
            ORDER BY gmv DESC
        """
        return self.query(sql)
    
    def get_table_schema(self) -> Dict[str, List[str]]:
        """获取所有表的字段信息 (用于LLM生成SQL)"""
        schema = {}
        tables = ['users', 'products', 'orders', 'funnel']
        
        for table in tables:
            columns = self.conn.execute(f"DESCRIBE {table}").df()
            schema[table] = columns['column_name'].tolist()
        
        return schema
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            print("🔒 数据库连接已关闭")


# 单例模式
_data_manager_instance = None

def get_data_manager() -> DataManager:
    """获取DataManager单例"""
    global _data_manager_instance
    if _data_manager_instance is None:
        _data_manager_instance = DataManager()
    return _data_manager_instance


if __name__ == "__main__":
    # 测试代码
    dm = DataManager()
    dm.load_csv_to_db(force_reload=True)
    
    print("\n📊 订单统计:")
    print(dm.get_daily_stats(7))
    
    print("\n📊 表结构:")
    print(dm.get_table_schema())
