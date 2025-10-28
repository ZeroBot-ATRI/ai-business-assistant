# ui/app_enhanced.py - Day 3 增强版聊天界面
import streamlit as st
import requests
import json
from datetime import datetime
import time

# 页面配置
st.set_page_config(
    page_title="AI业务助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .stat-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-badge {
        background-color: #28a745;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
    }
    .error-badge {
        background-color: #dc3545;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# API配置
API_BASE_URL = "http://localhost:8000"

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []

if "stats" not in st.session_state:
    st.session_state.stats = {
        "total_queries": 0,
        "successful_queries": 0,
        "total_time": 0
    }

# 辅助函数
def call_chat_api(user_input: str) -> dict:
    """调用聊天API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            params={"user_input": user_input},
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_backend_status() -> dict:
    """获取后端状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=3)
        if response.status_code == 200:
            return {"online": True, "data": response.json()}
    except:
        pass
    return {"online": False}

def get_metrics() -> dict:
    """获取系统指标"""
    try:
        response = requests.get(f"{API_BASE_URL}/metrics", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        return {}

# ==================== 主界面 ====================

# 标题区域
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="main-header">🤖 企业AI业务助手</div>', unsafe_allow_html=True)
    st.caption("Day 3 增强版 v0.3.0 | 基于 Claude Sonnet 4")

st.divider()

# 主要内容区域
main_col, stats_col = st.columns([3, 1])

with main_col:
    # 显示历史消息
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # 如果有调试信息，显示详情按钮
            if message.get("debug"):
                with st.expander("🔍 查看执行详情", expanded=False):
                    debug_info = message["debug"]

                    # 显示关键信息
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("意图", debug_info.get("intent", "未知"))
                    with col2:
                        st.metric("技能", debug_info.get("skill", "未知"))
                    with col3:
                        exec_time = debug_info.get("execution_time_ms", 0)
                        st.metric("执行时间", f"{exec_time:.0f}ms")

                    # 显示完整JSON
                    st.json(debug_info)

    # 用户输入
    if prompt := st.chat_input("💬 输入您的需求（例如：查询订单12345的状态）..."):
        # 显示用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 调用后端API
        with st.chat_message("assistant"):
            with st.spinner("🤔 AI正在分析您的请求..."):
                start_time = time.time()
                data = call_chat_api(prompt)
                elapsed_time = (time.time() - start_time) * 1000

                # 更新统计
                st.session_state.stats["total_queries"] += 1
                st.session_state.stats["total_time"] += elapsed_time

                if data.get("success"):
                    st.session_state.stats["successful_queries"] += 1
                    st.markdown(data["message"])

                    # 保存消息（包含调试信息）
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data["message"],
                        "debug": data.get("debug")
                    })

                    # 显示成功提示
                    st.success(f"✅ 处理成功 | 耗时: {elapsed_time:.0f}ms")
                else:
                    error_msg = data.get("error", "未知错误")
                    st.error(f"❌ 处理失败：{error_msg}")

                    # 显示详细错误信息
                    if data.get("debug"):
                        with st.expander("🔧 错误详情"):
                            st.json(data["debug"])

                    st.info("💡 提示：请检查输入格式或联系管理员")

# 右侧统计面板
with stats_col:
    st.subheader("📊 会话统计")

    # 本次会话统计
    total = st.session_state.stats["total_queries"]
    success = st.session_state.stats["successful_queries"]
    success_rate = (success / total * 100) if total > 0 else 0
    avg_time = (st.session_state.stats["total_time"] / total) if total > 0 else 0

    st.metric("总请求数", total)
    st.metric("成功数", success)
    st.metric("成功率", f"{success_rate:.1f}%")
    st.metric("平均耗时", f"{avg_time:.0f}ms")

    st.divider()

    # 获取系统指标
    st.subheader("🔧 系统指标")
    if st.button("🔄 刷新指标", use_container_width=True):
        st.rerun()

    metrics = get_metrics()
    if metrics:
        st.metric("今日总数", metrics.get("today_total", 0))
        st.metric("系统成功率", f"{metrics.get('success_rate', 0):.1%}")

        # 显示告警
        alerts = metrics.get("alerts", [])
        if alerts:
            st.warning(f"⚠️ {len(alerts)} 个告警")
            for alert in alerts[:3]:  # 只显示前3个
                st.caption(f"• {alert.get('message', '')}")

# ==================== 侧边栏 ====================

with st.sidebar:
    st.header("⚙️ 系统状态")

    # 后端状态检查
    status = get_backend_status()
    if status["online"]:
        st.success("✅ 后端运行正常")
        version_info = status["data"]
        st.caption(f"版本: {version_info.get('version', 'unknown')}")
        st.caption(f"API: {version_info.get('api', 'unknown')}")
        st.caption(f"LLM: {version_info.get('llm', 'unknown')}")
    else:
        st.error("❌ 后端未连接")
        st.info("启动命令：\n```bash\nuvicorn app.main:app --reload\n```")

    st.divider()

    # 快速测试场景
    st.header("🚀 快速测试")

    st.subheader("订单场景")
    if st.button("📦 查询正常订单", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "查询订单12345的状态"
        })
        st.rerun()

    if st.button("⏰ 查询延迟订单", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "查询订单999的状态"
        })
        st.rerun()

    if st.button("📋 查询待发货订单", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "查询订单888的状态"
        })
        st.rerun()

    st.subheader("库存场景")
    if st.button("✅ 查询正常库存", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "产品A还有多少库存？"
        })
        st.rerun()

    if st.button("⚠️ 查询库存不足", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "产品B的库存情况"
        })
        st.rerun()

    if st.button("❌ 查询缺货产品", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "产品C还有多少库存？"
        })
        st.rerun()

    st.divider()

    # 工具按钮
    st.header("🛠️ 工具")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ 清空对话", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    with col2:
        if st.button("📊 查看看板", use_container_width=True):
            st.info("监控看板开发中...")

    st.divider()

    # 使用说明
    st.header("📖 使用说明")
    with st.expander("快速上手"):
        st.markdown("""
        **基本用法：**
        1. 在输入框输入您的需求
        2. AI会自动识别意图并执行
        3. 点击"查看执行详情"了解处理过程

        **示例查询：**
        - "查询订单12345的状态"
        - "产品A还有多少库存？"
        - "发送邮件给customer@example.com"
        """)

    with st.expander("测试场景"):
        st.markdown("""
        **订单测试：**
        - 订单12345：已发货（正常）
        - 订单999：配送延迟
        - 订单888：待发货

        **库存测试：**
        - 产品A：库存充足（100件）
        - 产品B：库存不足（15件）
        - 产品C：缺货（0件）
        """)

# 页脚
st.divider()
footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col1:
    st.caption("🚀 AI业务助手 v0.3.0")
with footer_col2:
    st.caption(f"💬 已处理 {st.session_state.stats['total_queries']} 个请求")
with footer_col3:
    st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 运行：streamlit run ui/app_enhanced.py
