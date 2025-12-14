"""
Flowist Frontend - Streamlit Debug Interface

A simple web interface for testing and experiencing the Flowist meditation agent.
Designed for non-technical users (PM, testers) to quickly validate the system.
"""

import streamlit as st
import requests
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Flowist - 冥想 Agent 调试界面",
    page_icon="🧘",
    layout="centered",
)

# API endpoint
API_BASE_URL = "http://localhost:8000"

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #4A90E2;
        padding: 20px 0;
    }
    .section-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 20px 0 10px 0;
    }
    .result-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4A90E2;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>🧘 Flowist 冥想 Agent</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>基于上下文感知与记忆增强的个性化冥想引导</p>", unsafe_allow_html=True)

st.divider()

# Section 1: User Feeling Input
st.markdown("<div class='section-header'>💬 告诉我你现在的感受</div>", unsafe_allow_html=True)

user_feeling = st.text_area(
    label="",
    placeholder="例如：今天工作压力很大，肩膀很紧，脑子停不下来...",
    height=100,
    key="feeling_input",
)

# Section 2: Context Settings
st.markdown("<div class='section-header'>🌍 设置环境上下文</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    current_time = st.time_input(
        "🕐 当前时间",
        value=datetime.now().time(),
    )

with col2:
    weather = st.selectbox(
        "☁️ 天气状况",
        ["晴天", "阴天", "小雨", "大雨", "雪天", "雾霾"],
    )

with col3:
    location = st.selectbox(
        "📍 所在地点",
        ["家中", "办公室", "户外", "咖啡馆", "其他"],
    )

# User ID (optional for testing)
with st.expander("🔧 高级设置（可选）"):
    user_id = st.text_input("用户 ID", value="demo_user_001")
    user_name = st.text_input("称呼", value="朋友")

st.divider()

# Generate Button
generate_button = st.button(
    "🧘 生成冥想引导",
    type="primary",
    use_container_width=True,
)

# Section 3: Results Display
if generate_button:
    if not user_feeling.strip():
        st.error("⚠️ 请先描述你现在的感受")
    else:
        st.markdown("<div class='section-header'>🎙️ 冥想引导脚本</div>", unsafe_allow_html=True)
        
        # Prepare payload
        payload = {
            "user_id": user_id,
            "current_context": {
                "local_time": current_time.strftime("%H:%M"),
                "weather": weather,
                "location": location,
            },
            "user_feeling_input": user_feeling,
        }
        
        # Display loading spinner
        with st.spinner("🌟 正在为你生成专属的冥想引导..."):
            try:
                # Call API
                response = requests.post(
                    f"{API_BASE_URL}/api/v1/meditation/session",
                    json=payload,
                    timeout=60,  # Increased from 30 to 60 seconds
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Check if generation was successful
                    if result.get("status") == "success" and "script" in result:
                        # Display the generated meditation script
                        st.markdown("<div class='result-box'>", unsafe_allow_html=True)
                        st.markdown(result["script"])
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.success("✅ 生成完成！")
                        
                        # Show raw response in expander
                        with st.expander("📋 查看完整响应"):
                            st.json(result)
                    else:
                        st.error("❌ 生成失败")
                        st.json(result)
                    
                else:
                    st.error(f"❌ API 调用失败：HTTP {response.status_code}")
                    st.code(response.text)
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ 无法连接到后端服务")
                st.info(f"请确保 FastAPI 服务正在运行：`uvicorn app.main:app --reload`")
                
            except Exception as e:
                st.error(f"❌ 发生错误：{str(e)}")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #999; padding: 20px;'>
    <p>💡 <strong>提示</strong>：尝试不同的场景，例如：</p>
    <ul style='list-style: none; padding: 0;'>
        <li>😰 焦虑场景：工作压力、deadline、人际冲突</li>
        <li>😴 失眠场景：躺在床上、思绪纷飞</li>
        <li>💪 疲劳场景：肩颈疼痛、全身酸痛</li>
    </ul>
</div>
""", unsafe_allow_html=True)
