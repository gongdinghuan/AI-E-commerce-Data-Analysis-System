"""
电商模拟数据生成器

@Author: gongdinghuan
@Date: 2026-01-29
@Description: 生成真实场景的电商数据，包含用户、商品、订单、漏斗数据
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DATA_DIR, DATA_CONFIG


def generate_users(n_users: int = 500) -> pd.DataFrame:
    """生成用户数据"""
    np.random.seed(42)
    
    users = {
        'user_id': [f'U{str(i).zfill(5)}' for i in range(1, n_users + 1)],
        'username': [f'user_{i}' for i in range(1, n_users + 1)],
        'register_date': pd.date_range(
            end=datetime.now(), 
            periods=n_users, 
            freq='2H'
        ),
        'city': np.random.choice(DATA_CONFIG['cities'], n_users),
        'age': np.random.randint(18, 60, n_users),
        'gender': np.random.choice(['男', '女'], n_users, p=[0.45, 0.55]),
        'vip_level': np.random.choice([0, 1, 2, 3], n_users, p=[0.5, 0.3, 0.15, 0.05]),
    }
    
    return pd.DataFrame(users)


def generate_products(n_products: int = 200) -> pd.DataFrame:
    """生成商品数据"""
    np.random.seed(43)
    
    categories = DATA_CONFIG['categories']
    
    products = {
        'product_id': [f'P{str(i).zfill(4)}' for i in range(1, n_products + 1)],
        'product_name': [f'商品_{i}' for i in range(1, n_products + 1)],
        'category': np.random.choice(categories, n_products),
        'price': np.round(np.random.uniform(10, 2000, n_products), 2),
        'cost': None,  # 稍后计算
        'stock': np.random.randint(0, 1000, n_products),
        'rating': np.round(np.random.uniform(3.5, 5.0, n_products), 1),
    }
    
    df = pd.DataFrame(products)
    # 成本 = 价格 * (0.3~0.7)
    df['cost'] = np.round(df['price'] * np.random.uniform(0.3, 0.7, n_products), 2)
    
    return df


def generate_orders(
    n_orders: int = 10000,
    users_df: pd.DataFrame = None,
    products_df: pd.DataFrame = None,
    date_range_days: int = 180
) -> pd.DataFrame:
    """生成订单数据"""
    np.random.seed(44)
    
    if users_df is None:
        users_df = generate_users()
    if products_df is None:
        products_df = generate_products()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=date_range_days)
    
    # 生成订单时间 (模拟真实分布：晚间订单较多)
    order_dates = []
    for _ in range(n_orders):
        random_date = start_date + timedelta(
            days=int(np.random.randint(0, date_range_days)),
            hours=int(np.random.choice(range(24), p=_get_hour_distribution())),
            minutes=int(np.random.randint(0, 60))
        )
        order_dates.append(random_date)
    
    # 订单状态分布
    statuses = np.random.choice(
        ['已完成', '已完成', '已完成', '已完成', '已退款', '待发货', '已取消'],
        n_orders,
        p=[0.55, 0.15, 0.10, 0.05, 0.08, 0.04, 0.03]
    )
    
    orders = {
        'order_id': [f'ORD{str(i).zfill(8)}' for i in range(1, n_orders + 1)],
        'user_id': np.random.choice(users_df['user_id'], n_orders),
        'product_id': np.random.choice(products_df['product_id'], n_orders),
        'quantity': np.random.choice([1, 1, 1, 2, 2, 3], n_orders),
        'order_date': order_dates,
        'status': statuses,
        'channel': np.random.choice(
            DATA_CONFIG['channels'], 
            n_orders, 
            p=[0.30, 0.25, 0.20, 0.15, 0.10]
        ),
        'discount': np.round(np.random.choice([0, 0, 0, 0.1, 0.2, 0.3], n_orders), 2),
    }
    
    orders_df = pd.DataFrame(orders)
    
    # 合并商品价格计算金额
    orders_df = orders_df.merge(
        products_df[['product_id', 'price', 'cost', 'category']], 
        on='product_id'
    )
    orders_df['amount'] = np.round(
        orders_df['price'] * orders_df['quantity'] * (1 - orders_df['discount']), 
        2
    )
    orders_df['profit'] = np.round(
        (orders_df['price'] - orders_df['cost']) * orders_df['quantity'] * (1 - orders_df['discount']),
        2
    )
    
    # 合并用户城市
    orders_df = orders_df.merge(users_df[['user_id', 'city']], on='user_id')
    
    return orders_df


def generate_funnel_data(n_sessions: int = 50000) -> pd.DataFrame:
    """生成用户行为漏斗数据"""
    np.random.seed(45)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # 漏斗转化率: 浏览 -> 加购 -> 下单 -> 支付
    browse_count = n_sessions
    cart_count = int(browse_count * np.random.uniform(0.25, 0.35))
    order_count = int(cart_count * np.random.uniform(0.35, 0.50))
    pay_count = int(order_count * np.random.uniform(0.70, 0.85))
    
    funnel = {
        'stage': ['浏览', '加购', '下单', '支付'],
        'count': [browse_count, cart_count, order_count, pay_count],
        'date': [end_date] * 4,
    }
    
    return pd.DataFrame(funnel)


def _get_hour_distribution() -> list:
    """获取小时分布权重 (模拟真实购物时段)"""
    # 凌晨低, 上午增长, 中午降低, 下午增长, 晚间高峰
    weights = [
        0.01, 0.005, 0.005, 0.005, 0.01, 0.015,  # 0-5
        0.02, 0.03, 0.04, 0.05, 0.055, 0.05,      # 6-11
        0.045, 0.05, 0.055, 0.06, 0.065, 0.07,    # 12-17
        0.075, 0.08, 0.085, 0.075, 0.05, 0.025    # 18-23
    ]
    # 归一化
    total = sum(weights)
    return [w/total for w in weights]


def generate_data() -> dict:
    """生成完整的模拟数据集并保存"""
    print("🚀 开始生成模拟电商数据...")
    
    # 生成数据
    users_df = generate_users(DATA_CONFIG['n_users'])
    print(f"  ✓ 生成 {len(users_df)} 条用户数据")
    
    products_df = generate_products(DATA_CONFIG['n_products'])
    print(f"  ✓ 生成 {len(products_df)} 条商品数据")
    
    orders_df = generate_orders(
        n_orders=DATA_CONFIG['n_orders'],
        users_df=users_df,
        products_df=products_df,
        date_range_days=DATA_CONFIG['date_range_days']
    )
    print(f"  ✓ 生成 {len(orders_df)} 条订单数据")
    
    funnel_df = generate_funnel_data()
    print(f"  ✓ 生成漏斗数据")
    
    # 保存到CSV
    users_df.to_csv(DATA_DIR / 'users.csv', index=False, encoding='utf-8-sig')
    products_df.to_csv(DATA_DIR / 'products.csv', index=False, encoding='utf-8-sig')
    orders_df.to_csv(DATA_DIR / 'orders.csv', index=False, encoding='utf-8-sig')
    funnel_df.to_csv(DATA_DIR / 'funnel.csv', index=False, encoding='utf-8-sig')
    
    print(f"\n✅ 数据已保存到: {DATA_DIR}")
    
    return {
        'users': users_df,
        'products': products_df,
        'orders': orders_df,
        'funnel': funnel_df
    }


def generate_sample_data() -> pd.DataFrame:
    """生成简单的样本订单数据 (用于快速测试)"""
    np.random.seed(42)
    n_samples = 1000
    
    data = {
        'order_id': range(1, n_samples + 1),
        'user_id': np.random.randint(1, 200, n_samples),
        'amount': np.random.uniform(20, 500, n_samples).round(2),
        'date': pd.date_range(start='2025-01-01', periods=n_samples, freq='H'),
        'category': np.random.choice(['电子产品', '服装', '家居', '美妆'], n_samples),
        'status': np.random.choice(['已完成', '已完成', '已完成', '已退款'], n_samples),
        'channel': np.random.choice(['直播', '搜索', '推荐', '活动'], n_samples),
    }
    
    return pd.DataFrame(data)


if __name__ == "__main__":
    generate_data()
