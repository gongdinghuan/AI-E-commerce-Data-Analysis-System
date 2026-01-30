"""
Jarvis 电商数据中控 - Streamlit Dashboard

@Author: gongdinghuan
@Date: 2026-01-29
@Description: 钢铁侠风格的数据可视化大屏
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import APP_CONFIG, DATA_DIR
from core.data_manager import DataManager, get_data_manager
from core.analyzer import EcommerceAnalyzer
from core.jarvis_agent import JarvisAgent
from utils.data_generator import generate_data

# ==========================================
# 页面配置
# ==========================================
st.set_page_config(
    page_title=APP_CONFIG['title'],
    page_icon=APP_CONFIG['page_icon'],
    layout=APP_CONFIG['layout'],
    initial_sidebar_state="expanded"
)

# ==========================================
# 自定义CSS样式 (钢铁侠风格)
# ==========================================
def inject_custom_css():
    """注入自定义CSS"""
    colors = APP_CONFIG['colors']
    
    st.markdown(f"""
    <style>
        /* 全局样式 */
        .stApp {{
            background: linear-gradient(135deg, {colors['background']} 0%, #16213E 100%);
        }}
        
        /* 侧边栏 */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0F0F1A 0%, #1A1A2E 100%);
            border-right: 1px solid {colors['primary']}33;
        }}
        
        /* 指标卡片 */
        [data-testid="stMetricValue"] {{
            font-size: 2.5rem !important;
            font-weight: bold;
            background: linear-gradient(135deg, {colors['primary']}, {colors['secondary']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        [data-testid="stMetricDelta"] {{
            font-size: 1rem !important;
        }}
        
        /* 标题 */
        h1 {{
            background: linear-gradient(90deg, {colors['primary']}, {colors['secondary']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px {colors['primary']}66;
        }}
        
        h2, h3 {{
            color: {colors['primary']} !important;
        }}
        
        /* 卡片容器 */
        .metric-card {{
            background: linear-gradient(145deg, {colors['card_bg']}, #0F0F1A);
            border: 1px solid {colors['primary']}33;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 0 20px {colors['primary']}22;
        }}
        
        /* 输入框 */
        .stTextInput input {{
            background-color: {colors['card_bg']} !important;
            border: 1px solid {colors['primary']}66 !important;
            color: {colors['text']} !important;
            border-radius: 10px !important;
        }}
        
        .stTextInput input:focus {{
            border-color: {colors['primary']} !important;
            box-shadow: 0 0 10px {colors['primary']}44 !important;
        }}
        
        /* 按钮 */
        .stButton button {{
            background: linear-gradient(135deg, {colors['primary']}, #0088CC) !important;
            border: none !important;
            border-radius: 10px !important;
            color: white !important;
            font-weight: bold !important;
            transition: all 0.3s ease !important;
        }}
        
        .stButton button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 20px {colors['primary']}66 !important;
        }}
        
        /* 表格 */
        .dataframe {{
            background-color: {colors['card_bg']} !important;
        }}
        
        /* 分割线 */
        hr {{
            border-color: {colors['primary']}33 !important;
        }}
        
        /* 信息框 */
        .stAlert {{
            background-color: {colors['card_bg']} !important;
            border-left-color: {colors['primary']} !important;
        }}
        
        /* 选择框 */
        .stSelectbox > div > div {{
            background-color: {colors['card_bg']} !important;
            border-color: {colors['primary']}66 !important;
        }}
        
        /* 聊天消息 */
        [data-testid="stChatMessage"] {{
            background-color: {colors['card_bg']} !important;
            border: 1px solid {colors['primary']}22;
            border-radius: 15px;
        }}
        
        /* 霓虹光效 */
        .neon-text {{
            color: {colors['primary']};
            text-shadow: 0 0 10px {colors['primary']}, 0 0 20px {colors['primary']}, 0 0 40px {colors['primary']};
        }}
        
        /* 动画脉冲 */
        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 {colors['primary']}44; }}
            70% {{ box-shadow: 0 0 0 15px {colors['primary']}00; }}
            100% {{ box-shadow: 0 0 0 0 {colors['primary']}00; }}
        }}
        
        .pulse {{
            animation: pulse 2s infinite;
        }}
    </style>
    """, unsafe_allow_html=True)


# ==========================================
# 数据加载与缓存
# ==========================================
@st.cache_data(ttl=300)
def load_data():
    """加载数据"""
    # 检查是否有数据文件
    if not (DATA_DIR / 'orders.csv').exists():
        generate_data()
    
    dm = get_data_manager()
    dm.load_csv_to_db()
    
    orders = dm.get_orders()
    return orders


@st.cache_resource
def get_jarvis():
    """获取Jarvis实例"""
    dm = get_data_manager()
    dm.load_csv_to_db()
    return JarvisAgent(dm)


def create_plotly_theme():
    """创建Plotly主题"""
    colors = APP_CONFIG['colors']
    return {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {'color': colors['text']},
        'colorway': [colors['primary'], colors['secondary'], '#00E676', '#FF5252', '#7C4DFF', '#FFD740'],
    }


# ==========================================
# 可视化组件
# ==========================================
def render_kpi_cards(kpi: dict, trend: dict):
    """渲染KPI指标卡片"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 总GMV",
            value=f"¥{kpi['gmv']:,.0f}",
            delta=f"{trend.get('gmv_change', 0):+.1f}%"
        )
    
    with col2:
        st.metric(
            label="📦 订单数",
            value=f"{kpi['total_orders']:,}",
            delta=f"已付款 {kpi['paid_orders']:,}"
        )
    
    with col3:
        st.metric(
            label="⚠️ 退货率",
            value=f"{kpi['refund_rate']:.1%}",
            delta="-2.1%",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="👤 客单价",
            value=f"¥{kpi['aov']:.0f}",
            delta=f"复购率 {kpi['repeat_rate']:.1%}"
        )


def render_rfm_3d_chart(rfm_data: pd.DataFrame):
    """渲染RFM 3D散点图"""
    colors = APP_CONFIG['colors']
    
    fig = px.scatter_3d(
        rfm_data,
        x='Recency',
        y='Frequency', 
        z='Monetary',
        color='Label',
        opacity=0.8,
        title='用户价值 3D 分布图',
        labels={
            'Recency': '最近购买(天)',
            'Frequency': '购买频次',
            'Monetary': '消费金额'
        },
        color_discrete_sequence=[colors['primary'], colors['secondary'], '#00E676', '#FF5252']
    )
    
    fig.update_layout(
        **create_plotly_theme(),
        height=500,
        scene=dict(
            xaxis=dict(gridcolor='#333', title_font=dict(color=colors['text'])),
            yaxis=dict(gridcolor='#333', title_font=dict(color=colors['text'])),
            zaxis=dict(gridcolor='#333', title_font=dict(color=colors['text'])),
            bgcolor='rgba(0,0,0,0)'
        ),
        legend=dict(
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor=colors['primary'],
            font=dict(color=colors['text'])
        )
    )
    
    return fig


def render_funnel_chart(funnel_data: pd.DataFrame):
    """渲染漏斗图"""
    colors = APP_CONFIG['colors']
    
    fig = go.Figure(go.Funnel(
        y=funnel_data['stage'],
        x=funnel_data['count'],
        textinfo="value+percent initial",
        textfont=dict(color='white', size=14),
        marker=dict(
            color=[colors['primary'], '#00A8CC', colors['secondary'], '#00E676'],
            line=dict(width=2, color='white')
        ),
        connector=dict(line=dict(color=colors['primary'], width=2))
    ))
    
    fig.update_layout(
        **create_plotly_theme(),
        title='转化漏斗分析',
        height=400
    )
    
    return fig


def render_sales_trend_chart(forecast_data: pd.DataFrame):
    """渲染销售趋势图(含预测)"""
    colors = APP_CONFIG['colors']
    
    actual = forecast_data[forecast_data['type'] == 'actual'].tail(30)
    forecast = forecast_data[forecast_data['type'] == 'forecast']
    
    fig = go.Figure()
    
    # 历史数据
    fig.add_trace(go.Scatter(
        x=actual['date'],
        y=actual['sales'],
        mode='lines+markers',
        name='历史销售',
        line=dict(color=colors['primary'], width=3),
        marker=dict(size=6)
    ))
    
    # 预测数据
    fig.add_trace(go.Scatter(
        x=forecast['date'],
        y=forecast['sales'],
        mode='lines+markers',
        name='预测销售',
        line=dict(color=colors['secondary'], width=3, dash='dash'),
        marker=dict(size=6, symbol='diamond')
    ))
    
    # 添加分界线
    if len(actual) > 0 and len(forecast) > 0:
        last_date = actual['date'].iloc[-1]
        fig.add_shape(
            type="line",
            x0=last_date,
            y0=0,
            x1=last_date,
            y1=1,
            yref="paper",
            line=dict(color=colors['text'], width=2, dash="dot")
        )
        fig.add_annotation(
            x=last_date,
            y=1,
            yref="paper",
            text="预测起点",
            showarrow=False,
            yshift=10,
            font=dict(color=colors['text'])
        )
    
    fig.update_layout(
        **create_plotly_theme(),
        title='销售趋势与预测',
        xaxis_title='日期',
        yaxis_title='销售额 (¥)',
        height=400,
        hovermode='x unified'
    )
    
    return fig


def render_category_chart(orders_df: pd.DataFrame):
    """渲染品类分布图"""
    colors = APP_CONFIG['colors']
    
    analyzer = EcommerceAnalyzer(orders_df)
    category_data = analyzer.analyze_by_dimension('category')
    
    fig = px.treemap(
        category_data,
        path=['category'],
        values='GMV',
        color='GMV',
        color_continuous_scale=[colors['background'], colors['primary'], colors['secondary']],
        title='品类GMV分布'
    )
    
    fig.update_layout(
        **create_plotly_theme(),
        height=350
    )
    
    return fig


def render_channel_chart(orders_df: pd.DataFrame):
    """渲染渠道分布图"""
    colors = APP_CONFIG['colors']
    
    analyzer = EcommerceAnalyzer(orders_df)
    channel_data = analyzer.analyze_by_dimension('channel')
    
    fig = px.bar(
        channel_data,
        x='channel',
        y='GMV',
        color='GMV',
        color_continuous_scale=[colors['primary'], colors['secondary']],
        title='渠道GMV分布'
    )
    
    fig.update_layout(
        **create_plotly_theme(),
        height=350,
        xaxis_title='渠道',
        yaxis_title='GMV (¥)'
    )
    
    return fig


# ==========================================
# 主界面
# ==========================================
def main():
    """主函数"""
    inject_custom_css()
    
    # 加载数据
    orders_df = load_data()
    analyzer = EcommerceAnalyzer(orders_df)
    jarvis = get_jarvis()
    
    # ==========================================
    # 侧边栏
    # ==========================================
    with st.sidebar:
        st.markdown("# 🎛️ 控制台")
        st.markdown("---")
        
        # 数据状态
        st.markdown("### 📊 数据状态")
        st.info(f"""
        - 订单数: {len(orders_df):,}
        - 用户数: {orders_df['user_id'].nunique():,}
        - 时间范围: {orders_df['order_date'].min().strftime('%Y-%m-%d')} ~ {orders_df['order_date'].max().strftime('%Y-%m-%d')}
        """)
        
        st.markdown("---")
        
        # 筛选器
        st.markdown("### 🔍 数据筛选")
        
        selected_category = st.multiselect(
            "商品类目",
            options=orders_df['category'].unique().tolist(),
            default=[]
        )
        
        selected_channel = st.multiselect(
            "销售渠道",
            options=orders_df['channel'].unique().tolist(),
            default=[]
        )
        
        selected_city = st.multiselect(
            "城市",
            options=orders_df['city'].unique().tolist(),
            default=[]
        )
        
        # 应用筛选
        filtered_df = orders_df.copy()
        if selected_category:
            filtered_df = filtered_df[filtered_df['category'].isin(selected_category)]
        if selected_channel:
            filtered_df = filtered_df[filtered_df['channel'].isin(selected_channel)]
        if selected_city:
            filtered_df = filtered_df[filtered_df['city'].isin(selected_city)]
        
        st.markdown("---")
        
        # 数据导入功能
        with st.expander("📥 导入数据", expanded=False):
            import_type = st.radio(
                "选择导入类型",
                ["订单数据", "用户数据", "商品数据"],
                horizontal=True
            )
            
            uploaded_file = st.file_uploader(
                "上传CSV文件",
                type=['csv'],
                key=f"upload_{import_type}"
            )
            
            if uploaded_file is not None:
                with st.spinner("正在导入数据..."):
                    # 保存上传的文件
                    temp_path = DATA_DIR / f"temp_{uploaded_file.name}"
                    with open(temp_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # 根据类型导入
                    dm = get_data_manager()
                    
                    if import_type == "订单数据":
                        result = dm.import_orders_from_csv(str(temp_path))
                    elif import_type == "用户数据":
                        result = dm.import_users_from_csv(str(temp_path))
                    else:
                        result = dm.import_products_from_csv(str(temp_path))
                    
                    # 删除临时文件
                    if temp_path.exists():
                        temp_path.unlink()
                    
                    # 显示结果
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                        st.info(f"导入数量: {result['imported_count']} 条")
                        # 清除缓存并刷新
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
                        if result['errors']:
                            with st.expander("错误详情"):
                                for error in result['errors']:
                                    st.text(error)
            
            st.markdown("""
            **CSV文件格式要求:**
            
            - **订单数据**: 必需字段 `order_id`, `user_id`, `product_id`, `quantity`, `order_date`, `status`, `price`
            - **用户数据**: 必需字段 `user_id`
            - **商品数据**: 必需字段 `product_id`, `price`
            
            其他字段为可选，系统会自动填充默认值。
            """)
        
        st.markdown("---")
        
        # 操作按钮
        if st.button("🔄 刷新数据", width='stretch'):
            st.cache_data.clear()
            st.rerun()
        
        if st.button("📥 重新生成数据", width='stretch'):
            generate_data()
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown("*Powered by Jarvis AI*")
    
    # ==========================================
    # 主内容区
    # ==========================================
    
    # 标题
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: 30px;'>
            ⚡ Jarvis 电商数据中控
        </h1>
    """, unsafe_allow_html=True)
    
    # 更新分析器使用筛选后的数据
    analyzer = EcommerceAnalyzer(filtered_df)
    
    # ==========================================
    # 第一部分：核心KPI
    # ==========================================
    st.markdown("### 📈 核心指标")
    
    kpi = analyzer.get_kpi()
    trend = analyzer.get_kpi_trend(7)
    render_kpi_cards(kpi, trend)
    
    st.divider()
    
    # ==========================================
    # 第二部分：图表区域
    # ==========================================
    
    # 第一行：RFM + 漏斗
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("### 🤖 AI 用户分层 (RFM Clustering)")
        rfm_data, rfm_summary = analyzer.perform_rfm_clustering()
        fig_rfm = render_rfm_3d_chart(rfm_data)
        st.plotly_chart(fig_rfm, width='stretch')
    
    with col2:
        st.markdown("### 📊 转化漏斗")
        funnel_data = analyzer.get_funnel_analysis()
        fig_funnel = render_funnel_chart(funnel_data)
        st.plotly_chart(fig_funnel, width='stretch')
        
        # RFM 策略建议
        st.markdown("#### 💡 运营策略")
        for label, info in rfm_summary.items():
            with st.expander(f"{label} ({info['占比']})"):
                from config import RFM_CONFIG
                st.write(RFM_CONFIG['strategies'].get(label, ''))
    
    st.divider()
    
    # 第二行：销售趋势 + 维度分析
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 销售趋势与预测")
        forecast_data = analyzer.forecast_sales(7)
        fig_trend = render_sales_trend_chart(forecast_data)
        st.plotly_chart(fig_trend, width='stretch')
    
    with col2:
        tab1, tab2 = st.tabs(["🏷️ 品类分布", "📢 渠道分布"])
        
        with tab1:
            fig_category = render_category_chart(filtered_df)
            st.plotly_chart(fig_category, width='stretch')
        
        with tab2:
            fig_channel = render_channel_chart(filtered_df)
            st.plotly_chart(fig_channel, width='stretch')
    
    st.divider()
    
    # ==========================================
    # 第三部分：AI 对话
    # ==========================================
    st.markdown("### 💬 Jarvis 对话式分析")
    st.caption("用自然语言提问，让AI帮你分析数据")
    
    # 快捷问题
    quick_questions = [
        "找出消费金额最高的前10名用户",
        "分析各城市的退货率",
        "最近7天的销售趋势如何",
        "哪个渠道的转化效果最好"
    ]
    
    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]
    
    for i, q in enumerate(quick_questions):
        with cols[i]:
            if st.button(q[:10] + "...", key=f"quick_{i}", width='stretch'):
                st.session_state['user_question'] = q
    
    # 用户输入
    user_question = st.text_input(
        "请输入您的问题",
        value=st.session_state.get('user_question', ''),
        placeholder="例如：找出消费最高的10个用户",
        key="chat_input"
    )
    
    if user_question:
        with st.spinner("🤖 Jarvis 正在分析..."):
            result = jarvis.chat(user_question)
        
        # 显示结果
        st.markdown("#### 📊 分析结果")
        
        if result.get('error'):
            st.error(result['error'])
        else:
            # 显示SQL
            with st.expander("🔧 生成的SQL", expanded=False):
                st.code(result['sql'], language='sql')
            
            # 显示数据
            if result.get('data') is not None and len(result['data']) > 0:
                st.dataframe(
                    result['data'],
                    width='stretch',
                    height=min(400, len(result['data']) * 35 + 38)
                )
            
            # 显示洞察
            if result.get('insight'):
                st.markdown("#### 💡 AI 洞察")
                st.info(result['insight'])
    
    st.divider()
    
    # ==========================================
    # 第四部分：数据表格
    # ==========================================
    st.markdown("### 📋 详细数据")
    
    tab1, tab2, tab3 = st.tabs(["🏆 Top用户", "📦 Top商品", "📊 原始数据"])
    
    with tab1:
        top_users = analyzer.get_top_users(10)
        st.dataframe(top_users, width='stretch')
    
    with tab2:
        top_products = analyzer.get_top_products(10)
        if len(top_products) > 0:
            st.dataframe(top_products, width='stretch')
        else:
            st.info("暂无商品数据")
    
    with tab3:
        st.dataframe(
            filtered_df.head(100),
            width='stretch',
            height=400
        )
    
    # ==========================================
    # 页脚
    # ==========================================
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>⚡ Jarvis 电商数据中控 v1.0</p>
            <p>Powered by Streamlit + DuckDB + LangChain</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
