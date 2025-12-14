# Flowist 前端启动指南

## 快速开始

### 1. 安装依赖（如果还未安装）
```bash
cd /Users/langqixu/Documents/Codelab/projects/Flowist
pip3 install -r requirements.txt
```

### 2. 启动后端服务

在一个终端窗口中运行：
```bash
uvicorn app.main:app --reload
```

后端服务将在 `http://localhost:8000` 启动。

### 3. 启动前端界面

在另一个终端窗口中运行：
```bash
streamlit run frontend/app.py
```

前端界面将自动在浏览器中打开（通常是 `http://localhost:8501`）。

---

## 使用方法

### 界面布局

界面分为三个主要区域：

1. **💬 告诉我你现在的感受**  
   输入你当前的状态、情绪或身体感受

2. **🌍 设置环境上下文**  
   选择当前时间、天气和所在地点

3. **🎙️ 冥想引导脚本**  
   点击"生成冥想引导"按钮后显示生成的脚本

### 测试场景示例

#### 焦虑场景
```
感受：明天有重要的演讲，心跳加速，手心出汗
时间：晚上 22:00
天气：阴天
地点：家中
```

#### 失眠场景
```
感受：躺在床上一个小时了，脑子里全是明天的待办事项
时间：凌晨 01:30
天气：晴天
地点：家中
```

#### 工作压力场景
```
感受：连续开了 5 个会，肩膀像石头一样硬，头很重
时间：下午 18:00
天气：雾霾
地点：办公室
```

---

## 故障排查

### 问题：无法连接到后端服务
**解决方案**：
- 确认后端服务正在运行（`uvicorn app.main:app --reload`）
- 检查后端是否在 `http://localhost:8000` 启动
- 查看后端终端是否有错误信息

### 问题：依赖安装失败
**解决方案**：
```bash
# 尝试使用 pip3 而不是 pip
pip3 install -r requirements.txt

# 或者使用虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 问题：Streamlit 无法启动
**解决方案**：
- 确认已安装 streamlit：`pip3 show streamlit`
- 检查端口 8501 是否被占用
- 尝试指定端口：`streamlit run frontend/app.py --server.port 8502`

---

## 下一步

界面启动成功后，你可以：
1. 尝试不同的输入场景
2. 观察 Agent 如何根据上下文生成个性化内容
3. 验证 RAG 知识库是否被正确检索和使用
