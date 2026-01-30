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
    
    def import_orders_from_csv(self, csv_file_path: str) -> Dict[str, Any]:
        """
        从CSV文件导入订单数据
        
        Args:
            csv_file_path: CSV文件路径
            
        Returns:
            导入结果字典，包含成功/失败信息
        """
        result = {
            'success': False,
            'message': '',
            'imported_count': 0,
            'errors': []
        }
        
        try:
            # 读取CSV文件
            df = pd.read_csv(csv_file_path)
            
            # 验证必需字段
            required_fields = ['order_id', 'user_id', 'product_id', 'quantity', 
                          'order_date', 'status', 'price']
            missing_fields = [f for f in required_fields if f not in df.columns]
            
            if missing_fields:
                result['message'] = f"CSV文件缺少必需字段: {', '.join(missing_fields)}"
                return result
            
            # 数据清洗和转换
            df = df.copy()
            
            # 确保日期格式正确
            if 'order_date' in df.columns:
                df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
            
            # 计算缺失字段
            if 'amount' not in df.columns:
                df['amount'] = df['quantity'] * df['price']
            
            if 'cost' not in df.columns:
                df['cost'] = df['price'] * 0.7  # 假设成本为价格的70%
            
            if 'profit' not in df.columns:
                df['profit'] = df['amount'] - df['cost']
            
            if 'discount' not in df.columns:
                df['discount'] = 0.0
            
            if 'category' not in df.columns:
                df['category'] = '其他'
            
            if 'city' not in df.columns:
                df['city'] = '未知'
            
            if 'channel' not in df.columns:
                df['channel'] = '其他'
            
            # 选择需要的列
            columns_to_import = [
                'order_id', 'user_id', 'product_id', 'quantity',
                'order_date', 'status', 'channel', 'discount',
                'price', 'cost', 'category', 'amount', 'profit', 'city'
            ]
            df_import = df[columns_to_import]
            
            # 删除已存在的订单ID
            existing_ids = self.conn.execute("SELECT order_id FROM orders").df()['order_id'].tolist()
            df_import = df_import[~df_import['order_id'].isin(existing_ids)]
            
            # 插入数据
            if len(df_import) > 0:
                self.conn.execute("INSERT INTO orders SELECT * FROM df_import")
                result['success'] = True
                result['imported_count'] = len(df_import)
                result['message'] = f"成功导入 {len(df_import)} 条订单记录"
                
                # 如果有重复的订单ID被跳过
                skipped_count = len(df) - len(df_import)
                if skipped_count > 0:
                    result['message'] += f" (跳过 {skipped_count} 条已存在的订单)"
            else:
                result['message'] = "没有新的订单需要导入"
                result['success'] = True
            
            return result
            
        except Exception as e:
            result['message'] = f"导入失败: {str(e)}"
            result['errors'].append(str(e))
            return result
    
    def import_users_from_csv(self, csv_file_path: str) -> Dict[str, Any]:
        """
        从CSV文件导入用户数据
        
        Args:
            csv_file_path: CSV文件路径
            
        Returns:
            导入结果字典
        """
        result = {
            'success': False,
            'message': '',
            'imported_count': 0,
            'errors': []
        }
        
        try:
            df = pd.read_csv(csv_file_path)
            
            # 验证必需字段
            required_fields = ['user_id']
            missing_fields = [f for f in required_fields if f not in df.columns]
            
            if missing_fields:
                result['message'] = f"CSV文件缺少必需字段: {', '.join(missing_fields)}"
                return result
            
            # 数据清洗
            df = df.copy()
            
            # 确保日期格式正确
            if 'register_date' in df.columns:
                df['register_date'] = pd.to_datetime(df['register_date'], errors='coerce')
            
            # 填充缺失字段
            if 'username' not in df.columns:
                df['username'] = df['user_id']
            
            if 'city' not in df.columns:
                df['city'] = '未知'
            
            if 'age' not in df.columns:
                df['age'] = 30
            
            if 'gender' not in df.columns:
                df['gender'] = '未知'
            
            if 'vip_level' not in df.columns:
                df['vip_level'] = 1
            
            # 选择需要的列
            columns_to_import = ['user_id', 'username', 'register_date', 
                            'city', 'age', 'gender', 'vip_level']
            df_import = df[columns_to_import]
            
            # 删除已存在的用户ID
            existing_ids = self.conn.execute("SELECT user_id FROM users").df()['user_id'].tolist()
            df_import = df_import[~df_import['user_id'].isin(existing_ids)]
            
            # 插入数据
            if len(df_import) > 0:
                self.conn.execute("INSERT INTO users SELECT * FROM df_import")
                result['success'] = True
                result['imported_count'] = len(df_import)
                result['message'] = f"成功导入 {len(df_import)} 条用户记录"
            else:
                result['message'] = "没有新的用户需要导入"
                result['success'] = True
            
            return result
            
        except Exception as e:
            result['message'] = f"导入失败: {str(e)}"
            result['errors'].append(str(e))
            return result
    
    def import_products_from_csv(self, csv_file_path: str) -> Dict[str, Any]:
        """
        从CSV文件导入商品数据
        
        Args:
            csv_file_path: CSV文件路径
            
        Returns:
            导入结果字典
        """
        result = {
            'success': False,
            'message': '',
            'imported_count': 0,
            'errors': []
        }
        
        try:
            df = pd.read_csv(csv_file_path)
            
            # 验证必需字段
            required_fields = ['product_id', 'price']
            missing_fields = [f for f in required_fields if f not in df.columns]
            
            if missing_fields:
                result['message'] = f"CSV文件缺少必需字段: {', '.join(missing_fields)}"
                return result
            
            # 数据清洗
            df = df.copy()
            
            # 填充缺失字段
            if 'product_name' not in df.columns:
                df['product_name'] = df['product_id']
            
            if 'category' not in df.columns:
                df['category'] = '其他'
            
            if 'cost' not in df.columns:
                df['cost'] = df['price'] * 0.7
            
            if 'stock' not in df.columns:
                df['stock'] = 100
            
            if 'rating' not in df.columns:
                df['rating'] = 4.5
            
            # 选择需要的列
            columns_to_import = ['product_id', 'product_name', 'category', 
                            'price', 'cost', 'stock', 'rating']
            df_import = df[columns_to_import]
            
            # 删除已存在的商品ID
            existing_ids = self.conn.execute("SELECT product_id FROM products").df()['product_id'].tolist()
            df_import = df_import[~df_import['product_id'].isin(existing_ids)]
            
            # 插入数据
            if len(df_import) > 0:
                self.conn.execute("INSERT INTO products SELECT * FROM df_import")
                result['success'] = True
                result['imported_count'] = len(df_import)
                result['message'] = f"成功导入 {len(df_import)} 条商品记录"
            else:
                result['message'] = "没有新的商品需要导入"
                result['success'] = True
            
            return result
            
        except Exception as e:
            result['message'] = f"导入失败: {str(e)}"
            result['errors'].append(str(e))
            return result
    
    def get_table_stats(self) -> Dict[str, int]:
        """
        获取各表的记录数统计
        
        Returns:
            统计字典
        """
        stats = {}
        tables = ['users', 'products', 'orders', 'funnel']
        
        for table in tables:
            count = self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            stats[table] = count
        
        return stats
    
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
