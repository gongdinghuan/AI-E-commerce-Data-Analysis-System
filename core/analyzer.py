"""
电商分析引擎 - EcommerceAnalyzer

@Author: gongdinghuan
@Date: 2026-01-29
@Description: 核心分析功能，包含KPI计算、RFM聚类、漏斗分析、销售预测
"""
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from typing import Dict, Tuple, Optional, List
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import RFM_CONFIG


class EcommerceAnalyzer:
    """电商数据分析引擎"""
    
    def __init__(self, orders_df: pd.DataFrame):
        """
        初始化分析器
        
        Args:
            orders_df: 订单数据DataFrame
        """
        self.df = orders_df.copy()
        self._preprocess()
    
    def _preprocess(self):
        """数据预处理"""
        # 确保日期格式
        if 'order_date' in self.df.columns:
            self.df['order_date'] = pd.to_datetime(self.df['order_date'])
        elif 'date' in self.df.columns:
            self.df['order_date'] = pd.to_datetime(self.df['date'])
    
    # ==========================================
    # 核心 KPI 计算
    # ==========================================
    
    def get_kpi(self) -> Dict[str, float]:
        """
        计算核心KPI指标
        
        Returns:
            包含各KPI的字典
        """
        # 已完成订单
        paid_orders = self.df[self.df['status'].isin(['已完成', 'Paid'])]
        refunded_orders = self.df[self.df['status'].isin(['已退款', 'Refunded'])]
        
        # GMV
        total_gmv = paid_orders['amount'].sum()
        
        # 订单数
        total_orders = len(self.df)
        paid_count = len(paid_orders)
        
        # 退货率
        refund_count = len(refunded_orders)
        refund_rate = refund_count / total_orders if total_orders > 0 else 0
        
        # 客单价 (AOV)
        aov = total_gmv / paid_count if paid_count > 0 else 0
        
        # 利润
        total_profit = paid_orders['profit'].sum() if 'profit' in paid_orders.columns else 0
        
        # 独立用户数
        unique_users = self.df['user_id'].nunique()
        
        # 复购率
        user_order_counts = self.df.groupby('user_id').size()
        repeat_users = (user_order_counts > 1).sum()
        repeat_rate = repeat_users / unique_users if unique_users > 0 else 0
        
        return {
            'gmv': round(total_gmv, 2),
            'total_orders': total_orders,
            'paid_orders': paid_count,
            'refund_rate': round(refund_rate, 4),
            'aov': round(aov, 2),
            'profit': round(total_profit, 2),
            'unique_users': unique_users,
            'repeat_rate': round(repeat_rate, 4),
        }
    
    def get_kpi_trend(self, days: int = 7) -> pd.DataFrame:
        """
        获取KPI趋势对比
        
        Args:
            days: 对比天数
            
        Returns:
            最近N天与前N天的对比
        """
        current_date = self.df['order_date'].max()
        
        # 最近N天
        recent_start = current_date - timedelta(days=days)
        recent_df = self.df[self.df['order_date'] > recent_start]
        
        # 前N天
        previous_start = recent_start - timedelta(days=days)
        previous_df = self.df[
            (self.df['order_date'] > previous_start) & 
            (self.df['order_date'] <= recent_start)
        ]
        
        recent_gmv = recent_df[recent_df['status'].isin(['已完成', 'Paid'])]['amount'].sum()
        previous_gmv = previous_df[previous_df['status'].isin(['已完成', 'Paid'])]['amount'].sum()
        
        gmv_change = ((recent_gmv - previous_gmv) / previous_gmv * 100) if previous_gmv > 0 else 0
        
        return {
            'recent_gmv': round(recent_gmv, 2),
            'previous_gmv': round(previous_gmv, 2),
            'gmv_change': round(gmv_change, 2),
        }
    
    # ==========================================
    # RFM 用户分层 (K-Means 聚类)
    # ==========================================
    
    def perform_rfm_clustering(
        self, 
        n_clusters: int = None
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        使用K-Means进行RFM用户分层
        
        Args:
            n_clusters: 聚类数量
            
        Returns:
            (rfm_data, cluster_summary)
        """
        if n_clusters is None:
            n_clusters = RFM_CONFIG['n_clusters']
        
        # 只分析已完成订单
        paid_df = self.df[self.df['status'].isin(['已完成', 'Paid'])]
        
        # 计算当前日期
        current_date = paid_df['order_date'].max() + pd.Timedelta(days=1)
        
        # 计算 R, F, M
        rfm = paid_df.groupby('user_id').agg({
            'order_date': lambda x: (current_date - x.max()).days,  # Recency
            'order_id': 'count',  # Frequency
            'amount': 'sum'  # Monetary
        }).reset_index()
        
        rfm.columns = ['user_id', 'Recency', 'Frequency', 'Monetary']
        
        # 标准化数据用于聚类
        scaler = StandardScaler()
        rfm_scaled = scaler.fit_transform(rfm[['Recency', 'Frequency', 'Monetary']])
        
        # K-Means 聚类
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)
        
        # 根据各簇的中心特征分配标签
        cluster_centers = pd.DataFrame(
            scaler.inverse_transform(kmeans.cluster_centers_),
            columns=['Recency', 'Frequency', 'Monetary']
        )
        
        # 根据聚类中心的特征自动分配标签
        cluster_labels = self._assign_rfm_labels(cluster_centers)
        rfm['Label'] = rfm['Cluster'].map(cluster_labels)
        
        # 添加运营策略
        rfm['Strategy'] = rfm['Label'].map(RFM_CONFIG['strategies'])
        
        # 聚类汇总统计
        cluster_summary = rfm.groupby('Label').agg({
            'user_id': 'count',
            'Recency': 'mean',
            'Frequency': 'mean',
            'Monetary': 'mean'
        }).round(2)
        cluster_summary.columns = ['用户数', '平均天数', '平均频次', '平均消费']
        cluster_summary['占比'] = (cluster_summary['用户数'] / len(rfm) * 100).round(1).astype(str) + '%'
        
        return rfm, cluster_summary.to_dict('index')
    
    def _assign_rfm_labels(self, centers: pd.DataFrame) -> Dict[int, str]:
        """根据聚类中心自动分配标签"""
        labels = {}
        
        # 计算每个簇的"价值分数" = 高F + 高M + 低R
        centers['score'] = (
            centers['Frequency'] / centers['Frequency'].max() * 0.3 +
            centers['Monetary'] / centers['Monetary'].max() * 0.5 +
            (1 - centers['Recency'] / centers['Recency'].max()) * 0.2
        )
        
        # 按分数排序分配标签
        sorted_clusters = centers['score'].sort_values(ascending=False).index.tolist()
        
        label_names = list(RFM_CONFIG['labels'].values())
        for i, cluster_id in enumerate(sorted_clusters):
            if i < len(label_names):
                labels[cluster_id] = label_names[i]
            else:
                labels[cluster_id] = f"用户群{cluster_id}"
        
        return labels
    
    # ==========================================
    # 漏斗分析
    # ==========================================
    
    def get_funnel_analysis(self, funnel_df: pd.DataFrame = None) -> pd.DataFrame:
        """
        漏斗分析
        
        Args:
            funnel_df: 漏斗数据DataFrame
            
        Returns:
            带转化率的漏斗数据
        """
        if funnel_df is None:
            # 基于订单数据估算漏斗
            total_orders = len(self.df)
            paid_orders = len(self.df[self.df['status'].isin(['已完成', 'Paid'])])
            
            # 估算: 浏览量约为订单量的30倍, 加购约为订单量的5倍
            funnel_data = {
                'stage': ['浏览', '加购', '下单', '支付'],
                'count': [
                    total_orders * 30,  # 浏览量
                    total_orders * 5,   # 加购量
                    total_orders,       # 下单量
                    paid_orders         # 支付量
                ]
            }
            funnel_df = pd.DataFrame(funnel_data)
        
        # 计算转化率
        funnel_df = funnel_df.copy()
        funnel_df['conversion_rate'] = 0.0
        
        for i in range(len(funnel_df)):
            if i == 0:
                funnel_df.loc[i, 'conversion_rate'] = 100.0
            else:
                prev_count = funnel_df.loc[i-1, 'count']
                curr_count = funnel_df.loc[i, 'count']
                if prev_count > 0:
                    funnel_df.loc[i, 'conversion_rate'] = round(curr_count / prev_count * 100, 2)
        
        # 计算整体转化率
        if len(funnel_df) > 0:
            first_stage = funnel_df.iloc[0]['count']
            last_stage = funnel_df.iloc[-1]['count']
            overall_rate = (last_stage / first_stage * 100) if first_stage > 0 else 0
            funnel_df['overall_rate'] = round(overall_rate, 2)
        
        return funnel_df
    
    # ==========================================
    # 销售预测
    # ==========================================
    
    def forecast_sales(self, forecast_days: int = 7) -> pd.DataFrame:
        """
        使用线性回归预测未来销售
        
        Args:
            forecast_days: 预测天数
            
        Returns:
            包含历史和预测数据的DataFrame
        """
        # 按日汇总销售
        daily_sales = self.df[self.df['status'].isin(['已完成', 'Paid'])].copy()
        daily_sales['date'] = daily_sales['order_date'].dt.date
        
        daily_stats = daily_sales.groupby('date').agg({
            'amount': 'sum',
            'order_id': 'count'
        }).reset_index()
        daily_stats.columns = ['date', 'sales', 'orders']
        daily_stats['date'] = pd.to_datetime(daily_stats['date'])
        daily_stats = daily_stats.sort_values('date')
        
        # 创建时间特征
        daily_stats['day_num'] = (daily_stats['date'] - daily_stats['date'].min()).dt.days
        
        # 线性回归模型
        X = daily_stats[['day_num']].values
        y = daily_stats['sales'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # 预测未来
        last_day = daily_stats['day_num'].max()
        future_days = np.array([[last_day + i] for i in range(1, forecast_days + 1)])
        future_sales = model.predict(future_days)
        
        # 构建预测结果
        last_date = daily_stats['date'].max()
        forecast_dates = [last_date + pd.Timedelta(days=i) for i in range(1, forecast_days + 1)]
        
        forecast_df = pd.DataFrame({
            'date': forecast_dates,
            'sales': future_sales.round(2),
            'orders': (future_sales / daily_stats['sales'].mean() * daily_stats['orders'].mean()).round(0),
            'type': 'forecast'
        })
        
        # 标记历史数据
        daily_stats['type'] = 'actual'
        
        # 合并历史和预测
        result = pd.concat([
            daily_stats[['date', 'sales', 'orders', 'type']],
            forecast_df
        ], ignore_index=True)
        
        return result
    
    # ==========================================
    # 维度分析
    # ==========================================
    
    def analyze_by_dimension(self, dimension: str) -> pd.DataFrame:
        """
        按维度分析数据
        
        Args:
            dimension: 分析维度 (category, channel, city)
            
        Returns:
            维度分析结果
        """
        if dimension not in self.df.columns:
            return pd.DataFrame()
        
        paid_df = self.df[self.df['status'].isin(['已完成', 'Paid'])]
        
        result = paid_df.groupby(dimension).agg({
            'order_id': 'count',
            'amount': 'sum',
            'profit': 'sum' if 'profit' in paid_df.columns else 'count',
            'user_id': 'nunique'
        }).reset_index()
        
        result.columns = [dimension, '订单数', 'GMV', '利润', '用户数']
        result['客单价'] = (result['GMV'] / result['订单数']).round(2)
        result['GMV占比'] = (result['GMV'] / result['GMV'].sum() * 100).round(1)
        
        return result.sort_values('GMV', ascending=False)
    
    def get_top_users(self, n: int = 10) -> pd.DataFrame:
        """获取Top消费用户"""
        paid_df = self.df[self.df['status'].isin(['已完成', 'Paid'])]
        
        top_users = paid_df.groupby('user_id').agg({
            'amount': 'sum',
            'order_id': 'count',
            'order_date': 'max'
        }).reset_index()
        
        top_users.columns = ['user_id', '总消费', '订单数', '最近购买']
        top_users = top_users.sort_values('总消费', ascending=False).head(n)
        
        return top_users
    
    def get_top_products(self, n: int = 10) -> pd.DataFrame:
        """获取Top销售商品"""
        paid_df = self.df[self.df['status'].isin(['已完成', 'Paid'])]
        
        if 'product_id' not in paid_df.columns:
            return pd.DataFrame()
        
        top_products = paid_df.groupby('product_id').agg({
            'amount': 'sum',
            'quantity': 'sum' if 'quantity' in paid_df.columns else 'count',
            'order_id': 'count'
        }).reset_index()
        
        top_products.columns = ['product_id', '销售额', '销量', '订单数']
        top_products = top_products.sort_values('销售额', ascending=False).head(n)
        
        return top_products


if __name__ == "__main__":
    # 测试代码
    from data_manager import get_data_manager
    
    dm = get_data_manager()
    dm.load_csv_to_db()
    
    orders = dm.get_orders()
    analyzer = EcommerceAnalyzer(orders)
    
    print("📊 核心KPI:")
    print(analyzer.get_kpi())
    
    print("\n👥 RFM用户分层:")
    rfm_data, summary = analyzer.perform_rfm_clustering()
    print(summary)
    
    print("\n📈 销售预测:")
    print(analyzer.forecast_sales(7))
