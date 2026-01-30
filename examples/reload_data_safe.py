"""
重新导入数据到数据库（安全模式）

@Author: gongdinghuan
@Date: 2026-01-30
@Description: 从CSV文件重新导入数据到数据库，支持检查和关闭锁定连接
"""
import sys
from pathlib import Path
import duckdb

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DATABASE_PATH, DATA_DIR

def reload_data_safe():
    """安全地重新导入数据"""
    print("=" * 60)
    print("🔄 重新导入数据到数据库（安全模式）")
    print("=" * 60)
    
    print(f"\n📂 数据库路径: {DATABASE_PATH}")
    print(f"📁 数据目录: {DATA_DIR}")
    
    # 检查数据文件是否存在
    csv_files = {
        'users': DATA_DIR / 'users.csv',
        'products': DATA_DIR / 'products.csv',
        'orders': DATA_DIR / 'orders.csv',
        'funnel': DATA_DIR / 'funnel.csv'
    }
    
    print("\n📋 检查数据文件：")
    for table_name, csv_path in csv_files.items():
        if csv_path.exists():
            import pandas as pd
            df = pd.read_csv(csv_path)
            print(f"  ✓ {table_name}: {len(df)} 条记录")
        else:
            print(f"  ✗ {table_name}: 文件不存在")
            return False
    
    # 创建新的数据库连接
    print("\n🔌 连接数据库...")
    try:
        conn = duckdb.connect(str(DATABASE_PATH))
        print("  ✅ 连接成功")
    except Exception as e:
        print(f"  ❌ 连接失败: {e}")
        return False
    
    # 检查并创建表结构
    print("\n🔨 检查表结构...")
    existing_tables = conn.execute("SHOW TABLES").fetchall()
    table_names = [t[0] for t in existing_tables]
    
    if 'users' not in table_names:
        print("  创建用户表...")
        conn.execute("""
            CREATE TABLE users (
                user_id VARCHAR PRIMARY KEY,
                username VARCHAR,
                register_date TIMESTAMP,
                city VARCHAR,
                age INTEGER,
                gender VARCHAR,
                vip_level INTEGER
            )
        """)
    
    if 'products' not in table_names:
        print("  创建商品表...")
        conn.execute("""
            CREATE TABLE products (
                product_id VARCHAR PRIMARY KEY,
                product_name VARCHAR,
                category VARCHAR,
                price DOUBLE,
                cost DOUBLE,
                stock INTEGER,
                rating DOUBLE
            )
        """)
    
    if 'orders' not in table_names:
        print("  创建订单表...")
        conn.execute("""
            CREATE TABLE orders (
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
    
    if 'funnel' not in table_names:
        print("  创建漏斗表...")
        conn.execute("""
            CREATE TABLE funnel (
                stage VARCHAR,
                count INTEGER,
                date TIMESTAMP
            )
        """)
    
    print("  ✅ 表结构检查完成")
    
    # 清空现有数据
    print("\n🗑️  清空现有数据...")
    try:
        conn.execute("DELETE FROM users")
        conn.execute("DELETE FROM products")
        conn.execute("DELETE FROM orders")
        conn.execute("DELETE FROM funnel")
        print("  ✅ 已清空所有表")
    except Exception as e:
        print(f"  ❌ 清空失败: {e}")
        conn.close()
        return False
    
    # 导入数据
    print("\n📥 导入新数据...")
    import pandas as pd
    
    for table_name, csv_path in csv_files.items():
        try:
            df = pd.read_csv(csv_path)
            conn.execute(f"INSERT INTO {table_name} SELECT * FROM df")
            print(f"  ✓ 导入 {table_name}: {len(df)} 条记录")
        except Exception as e:
            print(f"  ✗ 导入 {table_name} 失败: {e}")
            conn.close()
            return False
    
    # 关闭连接
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ 数据导入完成！")
    print("=" * 60)
    
    # 显示统计信息
    print("\n📊 当前数据库统计：")
    conn = duckdb.connect(str(DATABASE_PATH))
    for table_name in ['users', 'products', 'orders', 'funnel']:
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"   {table_name}: {count}")
    conn.close()
    
    return True

if __name__ == "__main__":
    reload_data_safe()
