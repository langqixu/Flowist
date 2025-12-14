#!/bin/bash

echo "🚀 启动 Flowist 后端服务..."
echo ""
echo "后端将在 http://localhost:8000 启动"
echo "API 文档：http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo "================================"
echo ""

cd "$(dirname "$0")"
uvicorn app.main:app --reload
