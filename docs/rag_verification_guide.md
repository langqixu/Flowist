# RAG 模块验证指南

## 前置准备

### 1. 安装依赖
```bash
cd /Users/langqixu/Documents/Codelab/projects/Flowist
pip3 install -r requirements.txt
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 并在 .env 中填入你的 OpenAI API Key
```

---

## 验证步骤

### 步骤 1: 导入知识库

运行知识库导入脚本，将 6 个 markdown 文档导入向量数据库：

```bash
python3 -m app.rag_service.ingest_knowledge
```

**预期结果**：
```
🚀 Starting knowledge base ingestion...
🗑️  Resetting collection...
✅ Successfully ingested XX document chunks
📊 Total documents in collection: XX
```

---

### 步骤 2: 测试检索功能

创建一个临时测试脚本 `test_rag.py`：

```python
from app.rag_service.retriever import KnowledgeRetriever

# 初始化检索器
retriever = KnowledgeRetriever()

# 测试场景 1: 焦虑
print("=" * 50)
print("测试查询: 焦虑")
print("=" * 50)
result = retriever.retrieve_knowledge("我很焦虑，压力很大", n_results=2)
print(result)

# 测试场景 2: 失眠
print("\n" + "=" * 50)
print("测试查询: 失眠")
print("=" * 50)
result = retriever.retrieve_knowledge("睡不着，脑子停不下来", n_results=2)
print(result)

# 测试场景 3: 肩颈疼痛
print("\n" + "=" * 50)
print("测试查询: 身体紧张")
print("=" * 50)
result = retriever.retrieve_knowledge("肩膀很紧，脖子疼", n_results=2)
print(result)
```

运行测试：
```bash
python3 test_rag.py
```

**预期结果**：每个查询应返回相关的知识片段。

---

### 步骤 3: 启动 FastAPI 服务

```bash
uvicorn app.main:app --reload
```

访问 `http://127.0.0.1:8000/docs` 查看 API 文档。

---

### 步骤 4: 测试完整生成流程

在 Swagger UI 或使用 curl 调用 API：

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/meditation/session" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_001",
    "current_context": {
      "local_time": "23:00",
      "weather": "Heavy Rain",
      "location": "Home"
    },
    "user_feeling_input": "今天工作压力很大，肩膀很紧，脑子停不下来"
  }'
```

**预期结果**：
- 后端检索到工作压力相关的知识（盒式呼吸、肩颈放松）
- LLM 基于检索到的知识生成个性化的冥想脚本
- 返回包含 `[2s]`、`[5s]` 等停顿标记的脚本

---

## 验收标准

- [ ] 知识库成功导入，向量数据库包含 10+ 文档块
- [ ] 检索"焦虑"能返回呼吸法相关内容
- [ ] 检索"失眠"能返回睡眠引导相关内容
- [ ] API 调用成功生成基于知识库的冥想脚本
- [ ] 生成的脚本包含停顿标记和具体技巧（非通用内容）
