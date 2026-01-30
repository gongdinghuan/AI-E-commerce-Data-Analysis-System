"""
交互式SQL查询工具

@Author: gongdinghuan
@Date: 2026-01-30
@Description: 提供交互式SQL查询界面，支持用户直接编写和执行SQL
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.data_manager import get_data_manager

def interactive_sql_query():
    """交互式SQL查询"""
    print("=" * 60)
    print("🔍 交互式SQL查询工具")
    print("=" * 60)
    
    dm = get_data_manager()
    
    print("\n📋 可用的数据表：")
    tables = dm.conn.execute("SHOW TABLES").fetchall()
    for table in tables:
        table_name = table[0]
        count = dm.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"   • {table_name}: {count} 条记录")
    
    print("\n💡 提示：")
    print("   - 输入 'help' 查看帮助")
    print("   - 输入 'tables' 查看表结构")
    print("   - 输入 'quit' 或 'exit' 退出")
    print("   - 直接输入SQL语句执行查询")
    
    while True:
        try:
            print("\n" + "-" * 60)
            sql = input("SQL> ").strip()
            
            if not sql:
                continue
            
            if sql.lower() in ['quit', 'exit', 'q']:
                print("\n👋 再见！")
                break
            
            if sql.lower() == 'help':
                print("\n📖 帮助信息：")
                print("   基本查询：SELECT * FROM orders LIMIT 10")
                print("   条件查询：SELECT * FROM orders WHERE status='已完成'")
                print("   统计查询：SELECT city, COUNT(*) FROM orders GROUP BY city")
                print("   聚合查询：SELECT category, SUM(amount) FROM orders GROUP BY category")
                print("   排序查询：SELECT * FROM orders ORDER BY amount DESC LIMIT 10")
                continue
            
            if sql.lower() == 'tables':
                print("\n📊 表结构：")
                for table in tables:
                    table_name = table[0]
                    print(f"\n   【{table_name}】")
                    schema = dm.conn.execute(f"DESCRIBE {table_name}").fetchall()
                    for col in schema:
                        print(f"      - {col[0]} ({col[1]})")
                continue
            
            if not sql.lower().startswith('select'):
                print("❌ 只支持 SELECT 查询")
                continue
            
            print("\n⏳ 执行查询...")
            result = dm.query(sql)
            
            print(f"\n✅ 查询完成，共 {len(result)} 条结果")
            print("\n" + "=" * 100)
            print(result.to_string(index=False))
            print("=" * 100)
            
            if len(result) > 20:
                print(f"\n💡 提示：结果较多，仅显示前20条。完整结果共 {len(result)} 条")
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 查询失败: {e}")
            print("💡 请检查SQL语法是否正确")

def quick_sql_examples():
    """快速SQL示例"""
    print("\n" + "=" * 60)
    print("📚 常用SQL查询示例")
    print("=" * 60)
    
    dm = get_data_manager()
    
    examples = [
        ("查询最近10条订单", "SELECT * FROM orders ORDER BY order_date DESC LIMIT 10"),
        ("查询各城市订单数", "SELECT city, COUNT(*) as order_count FROM orders GROUP BY city ORDER BY order_count DESC"),
        ("查询各品类销售额", "SELECT category, SUM(amount) as total_sales FROM orders GROUP BY category ORDER BY total_sales DESC"),
        ("查询高价值订单", "SELECT * FROM orders WHERE amount > 5000 ORDER BY amount DESC LIMIT 10"),
        ("查询用户消费排行", "SELECT user_id, SUM(amount) as total_spend FROM orders GROUP BY user_id ORDER BY total_spend DESC LIMIT 10"),
        ("查询各渠道转化率", "SELECT channel, COUNT(*) as orders, SUM(amount) as revenue FROM orders GROUP BY channel"),
        ("查询退货订单", "SELECT * FROM orders WHERE status='已退款' ORDER BY order_date DESC LIMIT 10"),
        ("查询平均客单价", "SELECT AVG(amount) as avg_order_value FROM orders WHERE status='已完成'"),
        ("查询每日销售趋势", "SELECT DATE(order_date) as date, COUNT(*) as orders, SUM(amount) as gmv FROM orders GROUP BY DATE(order_date) ORDER BY date DESC LIMIT 7"),
        ("查询商品评分分布", "SELECT rating, COUNT(*) as count FROM products GROUP BY rating ORDER BY rating DESC"),
    ]
    
    for i, (desc, sql) in enumerate(examples, 1):
        print(f"\n{i}. {desc}")
        print(f"   SQL: {sql}")
        try:
            result = dm.query(sql)
            print(f"   结果: {len(result)} 条记录")
        except Exception as e:
            print(f"   错误: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--examples':
        quick_sql_examples()
    else:
        interactive_sql_query()
