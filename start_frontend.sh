#!/bin/bash

echo "🎨 启动 Flowist 前端界面..."
echo ""
echo "前端将在浏览器中自动打开"
echo "默认地址：http://localhost:8501"
echo ""
echo "按 Ctrl+C 停止服务"
echo "================================"
echo ""

cd "$(dirname "$0")"
streamlit run frontend/app.py
