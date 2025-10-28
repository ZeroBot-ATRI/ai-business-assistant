# ui/dashboard.py - Day 3 监控看板
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 页面配置
st.set_page_config(
    page_title="AI助手监控看板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .alert-card {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# API配置
API_BASE_URL = "http://localhost:8000"

# 辅助函数
@st.cache_data(ttl=30)  # 缓存30秒
def get_metrics():
    """获取系统指标"""
    try:
        response = requests.get(f"{API_BASE_URL}/metrics", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def get_backend_status():
    """获取后端状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=3)
        if response.status_code == 200:
            return {"online": True, "data": response.json()}
    except:
        pass
    return {"online": False}

# ==================== 页面标题 ====================

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="main-title">📊 AI助手监控看板</div>', unsafe_allow_html=True)
    st.caption(f"实时更新 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 刷新按钮
col1, col2, col3 = st.columns([4, 1, 1])
with col2:
    if st.button("🔄 手动刷新", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
with col3:
    auto_refresh = st.checkbox("自动刷新", value=False)

if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()

st.divider()

# ==================== 后端状态 ====================

status = get_backend_status()
if status["online"]:
    st.success("✅ 后端服务运行正常")
    version_info = status["data"]
    st.caption(f"版本: {version_info.get('version')} | API: {version_info.get('api')} | LLM: {version_info.get('llm')}")
else:
    st.error("❌ 无法连接后端服务")
    st.info("请启动后端：uvicorn app.main:app --reload")
    st.stop()

st.divider()

# ==================== 核心指标 ====================

metrics = get_metrics()
if not metrics:
    st.error("❌ 无法获取系统指标")
    st.stop()

st.header("📈 核心指标")

metric_cols = st.columns(4)

with metric_cols[0]:
    today_total = metrics.get("today_total", 0)
    delta = metrics.get("today_delta", 0)
    st.metric(
        label="今日处理量",
        value=today_total,
        delta=f"{delta:+d} vs昨天" if delta != 0 else "首日数据"
    )

with metric_cols[1]:
    success_rate = metrics.get("success_rate", 0)
    delta = metrics.get("success_rate_delta", 0)
    st.metric(
        label="成功率",
        value=f"{success_rate:.1%}",
        delta=f"{delta:+.1%}" if delta != 0 else None
    )

with metric_cols[2]:
    avg_response = metrics.get("avg_response_ms", 0)
    delta = metrics.get("response_delta", 0)
    st.metric(
        label="平均响应时间",
        value=f"{avg_response:.0f}ms",
        delta=f"{delta:+.0f}ms" if delta != 0 else None,
        delta_color="inverse"  # 响应时间越低越好
    )

with metric_cols[3]:
    today_cost = metrics.get("today_cost", 0)
    delta = metrics.get("cost_delta", 0)
    st.metric(
        label="今日成本",
        value=f"${today_cost:.3f}",
        delta=f"${delta:+.3f}" if delta != 0 else None,
        delta_color="inverse"  # 成本越低越好
    )

st.divider()

# ==================== 实时告警 ====================

st.header("🚨 实时告警")

alerts = metrics.get("alerts", [])
if alerts:
    for alert in alerts:
        level = alert.get("level", "info")
        message = alert.get("message", "")

        if level == "critical":
            st.error(f"🔴 严重：{message}")
        elif level == "warning":
            st.warning(f"🟡 警告：{message}")
        else:
            st.info(f"🔵 提示：{message}")
else:
    st.success("✅ 系统运行正常，无告警")

st.divider()

# ==================== 趋势图表 ====================

st.header("📊 趋势分析")

chart_col1, chart_col2 = st.columns(2)

# 意图分布图
with chart_col1:
    st.subheader("🎯 意图分布（最近7天）")

    intent_data = metrics.get("intent_distribution", [])
    if intent_data and len(intent_data) > 0:
        df = pd.DataFrame(intent_data)

        fig = px.pie(
            df,
            values='count',
            names='intent',
            title='意图类型分布',
            hole=0.4,  # 环形图
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        fig.update_traces(
            textposition='inside',
            textinfo='percent+label'
        )

        fig.update_layout(
            showlegend=True,
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无数据")

# 处理量趋势（模拟数据）
with chart_col2:
    st.subheader("📈 处理量趋势（24小时）")

    # 生成模拟的24小时数据
    hours = list(range(24))
    counts = [today_total // 24 if today_total > 0 else 0] * 24

    if today_total > 0:
        # 添加一些随机波动
        import random
        for i in range(len(counts)):
            counts[i] = max(0, counts[i] + random.randint(-2, 5))

    df_hourly = pd.DataFrame({
        'hour': [f"{h:02d}:00" for h in hours],
        'count': counts
    })

    fig = px.line(
        df_hourly,
        x='hour',
        y='count',
        title='每小时处理量',
        markers=True
    )

    fig.update_traces(
        line=dict(color='#667eea', width=2),
        marker=dict(size=6)
    )

    fig.update_layout(
        xaxis_title="时间",
        yaxis_title="处理量",
        hovermode='x unified',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==================== 最近决策日志 ====================

st.header("📝 最近决策日志")

recent_logs = metrics.get("recent_logs", [])
if recent_logs:
    # 转换为DataFrame
    df_logs = pd.DataFrame(recent_logs)

    # 添加状态列
    if 'success' in df_logs.columns:
        df_logs['状态'] = df_logs['success'].apply(lambda x: '✅ 成功' if x else '❌ 失败')
    else:
        df_logs['状态'] = '✅ 成功'  # 默认成功

    # 重命名列
    column_mapping = {
        'user_input': '用户输入',
        'intent': '意图',
        'result': '执行动作',
        'timestamp': '时间戳'
    }

    df_display = df_logs.rename(columns=column_mapping)

    # 只显示需要的列
    display_columns = []
    for col in ['用户输入', '意图', '执行动作', '状态', '时间戳']:
        if col in df_display.columns:
            display_columns.append(col)

    if display_columns:
        st.dataframe(
            df_display[display_columns],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.dataframe(df_display, use_container_width=True, hide_index=True)
else:
    st.info("暂无决策记录")

st.divider()

# ==================== SOP统计 ====================

st.header("📋 SOP执行统计")

sop_stats = metrics.get("sop_stats", [])
if sop_stats:
    df_sop = pd.DataFrame(sop_stats)

    st.dataframe(
        df_sop,
        column_config={
            "sop_name": "SOP名称",
            "total": st.column_config.NumberColumn("执行次数", format="%d"),
            "success": st.column_config.NumberColumn("成功次数", format="%d"),
            "success_rate": st.column_config.ProgressColumn(
                "成功率",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
            "avg_time": st.column_config.NumberColumn("平均耗时(ms)", format="%.0f")
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.info("暂无SOP执行记录（Day 16-17 将实现）")

st.divider()

# ==================== 页脚 ====================

footer_cols = st.columns(3)
with footer_cols[0]:
    st.caption("📊 AI助手监控看板 v0.3.0")
with footer_cols[1]:
    st.caption(f"💾 数据库记录: {today_total} 条")
with footer_cols[2]:
    if auto_refresh:
        st.caption("🔄 自动刷新: 已启用 (30秒)")
    else:
        st.caption("🔄 自动刷新: 未启用")

# 运行：streamlit run ui/dashboard.py --server.port 8502
