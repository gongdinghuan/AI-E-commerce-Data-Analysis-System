"""
独立脚本操作数据库示例

@Author: gongdinghuan
@Date: 2026-01-30
@Description: 演示如何在独立脚本中使用 DataManager 操作数据库
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.data_manager import get_data_manager
from core.analyzer import EcommerceAnalyzer


def example_1_basic_query():
    """示例1：基础查询"""
    print("=" * 50)
    print("示例1：基础查询")
    print("=" * 50)
    
    # 获取数据库管理器
    dm = get_data_manager()
    
    # 查询所有订单
    orders = dm.get_orders(limit=5)
    print(f"\n📊 前5条订单：")
    print(orders[['order_id', 'user_id', 'amount', 'status']].to_string(index=False))
    
    # 查询所有用户
    users = dm.get_users()
    print(f"\n👥 用户总数：{len(users)}")
    
    # 查询所有商品
    products = dm.get_products()
    print(f"📦 商品总数：{len(products)}")


def example_2_filtered_query():
    """示例2：条件筛选查询"""
    print("\n" + "=" * 50)
    print("示例2：条件筛选查询")
    print("=" * 50)
    
    dm = get_data_manager()
    
    # 查询特定日期范围的订单
    orders = dm.get_orders(
        start_date="2025-01-01",
        end_date="2025-01-31",
        status="已完成"
    )
    print(f"\n📊 2025年1月已完成订单：{len(orders)} 条")
    print(f"   总金额：¥{orders['amount'].sum():,.2f}")
    
    # 查询特定类目的订单
    electronics_orders = dm.get_orders(category="电子产品")
    print(f"\n📱 电子产品订单：{len(electronics_orders)} 条")
    
    # 查询特定城市的订单
    beijing_orders = dm.get_orders(city="北京")
    print(f"   北京订单：{len(beijing_orders)} 条")


def example_3_statistics():
    """示例3：统计分析"""
    print("\n" + "=" * 50)
    print("示例3：统计分析")
    print("=" * 50)
    
    dm = get_data_manager()
    
    # 每日统计
    daily_stats = dm.get_daily_stats(days=7)
    print(f"\n📈 最近7天每日统计：")
    print(daily_stats[['date', 'order_count', 'gmv']].to_string(index=False))
    
    # 品类统计
    category_stats = dm.get_category_stats()
    print(f"\n📦 品类统计：")
    print(category_stats[['category', 'gmv', 'order_count']].to_string(index=False))
    
    # 渠道统计
    channel_stats = dm.get_channel_stats()
    print(f"\n📡 渠道统计：")
    print(channel_stats[['channel', 'gmv', 'unique_users']].to_string(index=False))
    
    # 城市统计
    city_stats = dm.get_city_stats()
    print(f"\n🏙 城市统计：")
    print(city_stats[['city', 'gmv', 'refund_rate']].to_string(index=False))


def example_4_custom_sql():
    """示例4：自定义SQL查询"""
    print("\n" + "=" * 50)
    print("示例4：自定义SQL查询")
    print("=" * 50)
    
    dm = get_data_manager()
    
    # 执行自定义SQL
    sql = """
        SELECT 
            city,
            COUNT(*) as order_count,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount
        FROM orders
        WHERE status = '已完成'
        GROUP BY city
        HAVING total_amount > 10000
        ORDER BY total_amount DESC
    """
    
    result = dm.query(sql)
    print(f"\n🏙 高销售额城市（>¥10,000）：")
    print(result.to_string(index=False))


def example_5_data_analysis():
    """示例5：使用分析器"""
    print("\n" + "=" * 50)
    print("示例5：使用分析器")
    print("=" * 50)
    
    dm = get_data_manager()
    
    # 获取订单数据
    orders_df = dm.get_orders()
    
    # 创建分析器
    analyzer = EcommerceAnalyzer(orders_df)
    
    # 核心KPI
    kpi = analyzer.get_kpi()
    print(f"\n📊 核心KPI：")
    print(f"   GMV: ¥{kpi['gmv']:,.2f}")
    print(f"   订单数: {kpi['total_orders']}")
    print(f"   退货率: {kpi['refund_rate']*100:.2f}%")
    print(f"   客单价: ¥{kpi['aov']:,.2f}")
    print(f"   复购率: {kpi['repeat_rate']*100:.2f}%")
    
    # RFM分析
    rfm_data, rfm_summary = analyzer.perform_rfm_clustering()
    print(f"\n👥 RFM用户分层：")
    for cluster, count in rfm_summary.items():
        print(f"   {cluster}: {count} 人")
    
    # 漏斗分析
    funnel_df = dm.get_funnel()
    if funnel_df is not None and len(funnel_df) > 0:
        print(f"\n📊 漏斗分析：")
        print(funnel_df.to_string(index=False))
    else:
        print(f"\n📊 漏斗数据为空，使用估算数据")
        # 使用订单数据估算漏斗
        total_orders = len(orders_df)
        paid_orders = len(orders_df[orders_df['status'].isin(['已完成', 'Paid'])])
        
        funnel_data = {
            'stage': ['浏览', '加购', '下单', '支付'],
            'count': [
                total_orders * 30,  # 浏览量
                total_orders * 5,   # 加购量
                total_orders,       # 下单量
                paid_orders         # 支付量
            ]
        }
        print(pd.DataFrame(funnel_data).to_string(index=False))
    
    # 销售预测
    forecast_data = analyzer.forecast_sales(forecast_days=7)
    print(f"\n📈 未来7天销售预测：")
    print(forecast_data[['date', 'type', 'sales']].tail(10).to_string(index=False))


def example_6_import_data():
    """示例6：导入数据"""
    print("\n" + "=" * 50)
    print("示例6：导入数据")
    print("=" * 50)
    
    dm = get_data_manager()
    
    # 获取当前统计
    stats_before = dm.get_table_stats()
    print(f"\n📊 导入前统计：")
    print(f"   订单数: {stats_before['orders']}")
    print(f"   用户数: {stats_before['users']}")
    
    # 导入订单数据（假设有CSV文件）
    # result = dm.import_orders_from_csv("path/to/your_orders.csv")
    # print(f"\n导入结果: {result['message']}")
    
    # 导入用户数据
    # result = dm.import_users_from_csv("path/to/your_users.csv")
    # print(f"导入结果: {result['message']}")
    
    # 导入商品数据
    # result = dm.import_products_from_csv("path/to/your_products.csv")
    # print(f"导入结果: {result['message']}")


def example_7_export_data():
    """示例7：导出数据"""
    print("\n" + "=" * 50)
    print("示例7：导出数据")
    print("=" * 50)
    
    dm = get_data_manager()
    
    # 查询数据
    orders = dm.get_orders(status="已完成")
    
    # 导出到CSV
    output_path = Path("exported_orders.csv")
    orders.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n✅ 已导出 {len(orders)} 条订单到 {output_path}")
    
    # 导出特定数据
    top_users = dm.query("""
        SELECT user_id, SUM(amount) as total_spend
        FROM orders
        WHERE status = '已完成'
        GROUP BY user_id
        ORDER BY total_spend DESC
        LIMIT 10
    """)
    
    output_path = Path("top_users.csv")
    top_users.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ 已导出 Top10 用户到 {output_path}")


def example_8_batch_operations():
    """示例8：批量操作"""
    print("\n" + "=" * 50)
    print("示例8：批量操作")
    print("=" * 50)
    
    dm = get_data_manager()
    
    # 批量更新（示例）
    # dm.conn.execute("""
    #     UPDATE orders
    #     SET discount = 0.9
    #     WHERE amount > 1000
    # """)
    # print("✅ 已更新高价值订单的折扣")
    
    # 批量删除（示例）
    # dm.conn.execute("DELETE FROM orders WHERE status = '已取消'")
    # print("✅ 已删除已取消的订单")
    
    # 批量插入（示例）
    # new_data = pd.DataFrame({
    #     'order_id': ['NEW001', 'NEW002'],
    #     'user_id': ['U00001', 'U00002'],
    #     'amount': [100.0, 200.0]
    # })
    # dm.conn.execute("INSERT INTO orders SELECT * FROM new_data")
    # print("✅ 已插入新订单")


def example_9_advanced_analysis():
    """示例9：高级分析"""
    print("\n" + "=" * 50)
    print("示例9：高级分析")
    print("=" * 50)
    
    dm = get_data_manager()
    orders_df = dm.get_orders()
    analyzer = EcommerceAnalyzer(orders_df)
    
    # 分析各城市的复购率
    city_repeat = dm.query("""
        SELECT 
            city,
            COUNT(DISTINCT user_id) as total_users,
            COUNT(*) as total_orders,
            COUNT(*) * 1.0 / COUNT(DISTINCT user_id) as avg_orders_per_user
        FROM orders
        WHERE status = '已完成'
        GROUP BY city
        ORDER BY avg_orders_per_user DESC
    """)
    print(f"\n🏙 各城市用户活跃度：")
    print(city_repeat.to_string(index=False))
    
    # 分析各品类的利润率
    category_profit = dm.query("""
        SELECT 
            category,
            SUM(amount) as revenue,
            SUM(profit) as total_profit,
            SUM(profit) * 100.0 / SUM(amount) as profit_margin
        FROM orders
        WHERE status = '已完成'
        GROUP BY category
        ORDER BY total_profit DESC
    """)
    print(f"\n📦 各品类利润率：")
    print(category_profit.to_string(index=False))
    
    # 分析时间趋势
    hourly_sales = dm.query("""
        SELECT 
            EXTRACT(hour FROM order_date) as hour,
            COUNT(*) as order_count,
            SUM(amount) as total_amount
        FROM orders
        WHERE status = '已完成'
        GROUP BY hour
        ORDER BY hour
    """)
    print(f"\n⏰ 各时段销售分布：")
    print(hourly_sales.to_string(index=False))


def example_10_custom_db_path():
    """示例10：使用自定义数据库路径"""
    print("\n" + "=" * 50)
    print("示例10：使用自定义数据库路径")
    print("=" * 50)
    
    from core.data_manager import DataManager
    
    # 使用自定义数据库路径
    custom_dm = DataManager(db_path=Path("custom_database.db"))
    
    # 查询数据
    stats = custom_dm.get_table_stats()
    print(f"\n📊 自定义数据库统计：")
    for table, count in stats.items():
        print(f"   {table}: {count} 条")
    
    # 关闭连接
    custom_dm.close()


def main():
    """主函数"""
    print("\n" + "🚀" * 25)
    print("独立脚本操作数据库示例")
    print("🚀" * 25 + "\n")
    
    # 运行各个示例
    example_1_basic_query()
    example_2_filtered_query()
    example_3_statistics()
    example_4_custom_sql()
    example_5_data_analysis()
    example_6_import_data()
    example_7_export_data()
    example_8_batch_operations()
    example_9_advanced_analysis()
    example_10_custom_db_path()
    
    print("\n" + "=" * 50)
    print("✅ 所有示例运行完成！")
    print("=" * 50)
    print("\n💡 提示：")
    print("1. 使用 get_data_manager() 获取单例数据库连接")
    print("2. 使用 dm.query(sql) 执行自定义SQL")
    print("3. 使用 dm.get_xxx() 方法获取特定数据")
    print("4. 使用 EcommerceAnalyzer 进行高级分析")
    print("5. 无需手动关闭连接（单例模式自动管理）")


if __name__ == "__main__":
    main()
