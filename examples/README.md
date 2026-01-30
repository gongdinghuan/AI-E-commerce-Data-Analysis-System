# 独立脚本操作数据库指南

本目录包含在独立脚本中操作数据库的示例代码。

## 📁 文件说明

### database_operations.py
完整的数据库操作示例脚本，包含10个实用示例：

1. **基础查询** - 简单的数据查询
2. **条件筛选** - 按日期、状态、类别等筛选
3. **统计分析** - 每日统计、品类统计等
4. **自定义SQL** - 执行复杂SQL查询
5. **使用分析器** - KPI、RFM、漏斗、预测
6. **导入数据** - 从CSV导入订单/用户/商品数据
7. **导出数据** - 将查询结果导出为CSV
8. **批量操作** - 批量更新、删除、插入
9. **高级分析** - 复购率、利润率、时段分析
10. **自定义数据库** - 使用非默认路径的数据库

### interactive_sql.py
交互式SQL查询工具，支持：

- **交互式查询** - 直接在命令行输入SQL语句
- **表结构查看** - 查看所有表和字段信息
- **常用示例** - 10个常用SQL查询示例
- **实时执行** - 即时显示查询结果

### reload_data.py / reload_data_safe.py
数据重新导入脚本：

- **reload_data.py** - 基础导入脚本
- **reload_data_safe.py** - 安全导入脚本（推荐）

## 🚀 快速开始

### 运行所有示例

```bash
cd examples
python database_operations.py
```

### 运行单个示例

编辑 `database_operations.py`，在 `main()` 函数中注释不需要的示例：

```python
def main():
    # 只运行需要的示例
    example_1_basic_query()
    example_3_statistics()
    example_5_data_analysis()
    
    print("\n✅ 运行完成！")
```

### 使用交互式SQL工具

```bash
# 启动交互式SQL查询
python interactive_sql.py

# 查看常用SQL示例
python interactive_sql.py --examples
```

交互式SQL工具命令：

- 输入SQL语句直接执行查询
- 输入 `help` 查看帮助信息
- 输入 `tables` 查看表结构
- 输入 `quit` 或 `exit` 退出

### 重新导入数据

```bash
# 使用安全模式重新导入（推荐）
python reload_data_safe.py

# 或使用基础模式
python reload_data.py
```

## 💡 核心概念

### 获取数据库连接

```python
from core.data_manager import get_data_manager

# 获取单例连接（推荐）
dm = get_data_manager()

# 或创建自定义连接
from core.data_manager import DataManager
dm = DataManager(db_path=Path("custom.db"))
```

### 执行查询

```python
# 方式1：使用预定义方法
orders = dm.get_orders(limit=10)
users = dm.get_users()
products = dm.get_products()

# 方式2：使用自定义SQL
result = dm.query("SELECT * FROM orders WHERE amount > 1000")

# 方式3：使用统计方法
daily_stats = dm.get_daily_stats(days=7)
category_stats = dm.get_category_stats()
```

### 使用分析器

```python
from core.analyzer import EcommerceAnalyzer

dm = get_data_manager()
analyzer = EcommerceAnalyzer(dm)

# 计算KPI
kpi = analyzer.calculate_kpi()

# RFM分析
rfm_data, rfm_summary = analyzer.perform_rfm_clustering()

# 销售预测
forecast = analyzer.forecast_sales(days=7)
```

## 📋 常用操作

### 查询数据

```python
# 获取所有订单
orders = dm.get_orders()

# 条件筛选
filtered = dm.get_orders(
    start_date="2025-01-01",
    end_date="2025-01-31",
    status="已完成",
    category="电子产品"
)

# 自定义SQL
result = dm.query("""
    SELECT city, COUNT(*) as count, SUM(amount) as total
    FROM orders
    GROUP BY city
""")
```

### 导入数据

```python
# 导入订单
result = dm.import_orders_from_csv("path/to/orders.csv")
if result['success']:
    print(f"导入成功: {result['imported_count']} 条")

# 导入用户
result = dm.import_users_from_csv("path/to/users.csv")

# 导入商品
result = dm.import_products_from_csv("path/to/products.csv")
```

### 导出数据

```python
# 查询数据
orders = dm.get_orders()

# 导出到CSV
orders.to_csv("output.csv", index=False)

# 或使用Pandas直接导出
df = dm.query("SELECT * FROM orders")
df.to_csv("export.csv", encoding='utf-8-sig')
```

### 批量操作

```python
# 批量更新
dm.conn.execute("UPDATE orders SET discount = 0.9 WHERE amount > 1000")

# 批量删除
dm.conn.execute("DELETE FROM orders WHERE status = '已取消'")

# 批量插入
new_data = pd.DataFrame({'order_id': ['001', '002'], 'amount': [100, 200]})
dm.conn.execute("INSERT INTO orders SELECT * FROM new_data")
```

### SQL查询示例

常用SQL查询语句：

```python
# 查询最近订单
dm.query("SELECT * FROM orders ORDER BY order_date DESC LIMIT 10")

# 城市订单统计
dm.query("SELECT city, COUNT(*) as order_count FROM orders GROUP BY city")

# 品类销售额
dm.query("SELECT category, SUM(amount) as total_sales FROM orders GROUP BY category")

# 高价值订单
dm.query("SELECT * FROM orders WHERE amount > 5000 ORDER BY amount DESC LIMIT 10")

# 用户消费排行
dm.query("SELECT user_id, SUM(amount) as total_spend FROM orders GROUP BY user_id ORDER BY total_spend DESC LIMIT 10")

# 渠道转化
dm.query("SELECT channel, COUNT(*) as orders, SUM(amount) as revenue FROM orders GROUP BY channel")

# 退货订单
dm.query("SELECT * FROM orders WHERE status='已退款' ORDER BY order_date DESC LIMIT 10")

# 平均客单价
dm.query("SELECT AVG(amount) as avg_order_value FROM orders WHERE status='已完成'")

# 每日销售趋势
dm.query("SELECT DATE(order_date) as date, COUNT(*) as orders, SUM(amount) as gmv FROM orders GROUP BY DATE(order_date) ORDER BY date DESC LIMIT 7")

# 商品评分分布
dm.query("SELECT rating, COUNT(*) as count FROM products GROUP BY rating ORDER BY rating DESC")
```

## 🔍 高级用法

### 数据分析

```python
# RFM聚类分析
rfm_data, rfm_summary = analyzer.perform_rfm_clustering()
print(rfm_summary)

# 漏斗分析
funnel = analyzer.get_funnel_analysis()

# 销售预测
forecast = analyzer.forecast_sales(days=30)
print(forecast)
```

### 复杂SQL查询

```python
# 多表关联
sql = """
    SELECT 
        u.username,
        u.city,
        COUNT(o.order_id) as order_count,
        SUM(o.amount) as total_spend
    FROM users u
    LEFT JOIN orders o ON u.user_id = o.user_id
    GROUP BY u.user_id
    ORDER BY total_spend DESC
    LIMIT 10
"""
result = dm.query(sql)

# 窗口函数
sql = """
    SELECT 
        DATE_TRUNC('month', order_date) as month,
        SUM(amount) as monthly_gmv
    FROM orders
    WHERE status = '已完成'
    GROUP BY DATE_TRUNC('month', order_date)
    ORDER BY month DESC
"""
monthly = dm.query(sql)
```

### 数据清洗

```python
# 查询异常数据
anomalies = dm.query("""
    SELECT * FROM orders
    WHERE amount < 0 OR quantity < 0 OR price < 0
""")

# 数据统计
stats = dm.get_table_stats()
print(f"订单数: {stats['orders']}")
print(f"用户数: {stats['users']}")

# 重复检测
duplicates = dm.query("""
    SELECT order_id, COUNT(*) as count
    FROM orders
    GROUP BY order_id
    HAVING count > 1
""")
```

## ⚠️ 注意事项

1. **单例模式**：使用 `get_data_manager()` 获取全局单例
2. **无需关闭**：单例模式下无需手动关闭连接
3. **自定义连接**：如需自定义路径，使用 `DataManager(db_path=...)`
4. **线程安全**：单例模式确保多线程安全
5. **错误处理**：建议使用 try-except 捕获异常

## 🛠️ 故障排除

### 连接问题

```python
# 检查数据库文件
from pathlib import Path
db_path = Path("database/analytics.db")
print(f"数据库存在: {db_path.exists()}")

# 重新初始化
import core.data_manager as dm
dm._data_manager_instance = None
dm = get_data_manager()
```

### 查询问题

```python
# 查看SQL错误
try:
    result = dm.query("SELECT * FROM orders")
except Exception as e:
    print(f"查询失败: {e}")

# 检查表结构
schema = dm.get_table_schema()
print(schema)
```

## 📚 更多资源

- [DataManager API 文档](../core/data_manager.py)
- [Analyzer API 文档](../core/analyzer.py)
- [配置文件](../config.py)
