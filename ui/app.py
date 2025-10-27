# ui/app.py - 超简单聊天界面
import streamlit as st
import requests
import json

st.set_page_config(page_title="AI业务助手", page_icon="🤖")

st.title("🤖 企业AI业务助手")
st.caption("15天极速版 v0.1")

# 初始化会话
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入
if prompt := st.chat_input("输入您的需求..."):
    # 显示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 调用后端API
    with st.chat_message("assistant"):
        with st.spinner("AI正在思考..."):
            try:
                response = requests.post(
                    "http://localhost:8000/chat",
                    params={"user_input": prompt},
                    timeout=30
                )
                data = response.json()

                if data["success"]:
                    st.markdown(data["message"])

                    # 显示调试信息
                    with st.expander("🔍 查看执行详情"):
                        st.json(data["debug"])

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data["message"]
                    })
                else:
                    st.error(f"错误：{data['error']}")
            except Exception as e:
                st.error(f"连接失败：{e}")
                st.info("请确保后端服务已启动：uvicorn app.main:app --reload")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 系统状态")

    # 检查后端状态
    try:
        health = requests.get("http://localhost:8000/", timeout=3)
        if health.status_code == 200:
            st.success("✅ 后端运行正常")
            version_info = health.json()
            st.caption(f"版本: {version_info.get('version', 'unknown')}")
        else:
            st.error("❌ 后端异常")
    except:
        st.error("❌ 后端未连接")
        st.info("启动命令：uvicorn app.main:app --reload")

    st.divider()

    # 快捷测试
    st.header("🚀 快速测试")
    if st.button("查询订单12345"):
        st.session_state.messages.append({
            "role": "user",
            "content": "查询订单12345的状态"
        })
        st.rerun()

    if st.button("查询产品A库存"):
        st.session_state.messages.append({
            "role": "user",
            "content": "产品A还有多少库存？"
        })
        st.rerun()

    if st.button("清空对话"):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # API密钥配置提示
    st.header("📝 配置说明")
    st.info("""
    **首次使用请配置：**
    1. 复制 .env.example 为 .env
    2. 填入 CLAUDE_API_KEY
    3. 重启后端服务
    """)

# 运行：streamlit run ui/app.py
