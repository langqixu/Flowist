# Flowist 多模型 API 配置指南

Flowist 现在支持多种 LLM 提供商，包括 OpenAI、DeepSeek、通义千问、本地模型等。

---

## 🔧 已更新的代码

### 1. 配置模块 ([`app/config.py`](file:///Users/langqixu/Documents/Codelab/projects/Flowist/app/config.py))
新增 `openai_base_url` 配置项，支持自定义 API 端点。

### 2. LLM 客户端 ([`app/core/llm_client.py`](file:///Users/langqixu/Documents/Codelab/projects/Flowist/app/core/llm_client.py))
自动检测并使用 `base_url`，兼容所有 OpenAI API 格式的服务。

### 3. 环境变量模板 ([`.env.example`](file:///Users/langqixu/Documents/Codelab/projects/Flowist/.env.example))
包含 5 种常用提供商的配置示例。

---

## 🌐 支持的 LLM 提供商

### ✅ Option 1: OpenAI（官方，默认）

**适用场景**：追求最佳质量，有国际支付方式。

```bash
# .env 配置
OPENAI_API_KEY=sk-proj-你的OpenAI_Key
OPENAI_MODEL=gpt-4o
# OPENAI_BASE_URL= # 留空即可
```

**模型推荐**：
- `gpt-4o` - 最新多模态模型（推荐）
- `gpt-4-turbo` - 更快的 GPT-4
- `gpt-3.5-turbo` - 经济型选择

---

### ✅ Option 2: DeepSeek（国内推荐）

**适用场景**：国内用户，性价比高，质量接近 GPT-4。

```bash
# .env 配置
OPENAI_API_KEY=sk-你的DeepSeek_Key
OPENAI_MODEL=deepseek-chat
OPENAI_BASE_URL=https://api.deepseek.com
```

**获取 API Key**：https://platform.deepseek.com/

**优势**：
- 🇨🇳 国内可直接访问
- 💰 价格便宜（¥1/百万 tokens）
- 🚀 速度快，延迟低
- ✅ 完全兼容 OpenAI API 格式

---

### ✅ Option 3: 阿里通义千问（Qwen）

**适用场景**：已有阿里云账号，或需要中文优化的模型。

```bash
# .env 配置
OPENAI_API_KEY=sk-你的通义千问Key
OPENAI_MODEL=qwen-plus
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

**获取 API Key**：https://dashscope.console.aliyun.com/

**可用模型**：
- `qwen-plus` - 通用模型（推荐）
- `qwen-turbo` - 快速响应
- `qwen-max` - 最强能力

---

### ✅ Option 4: 本地模型 Ollama（免费）

**适用场景**：数据隐私要求高，或想完全离线使用。

#### 步骤 1：安装 Ollama
```bash
# macOS
brew install ollama

# 或访问：https://ollama.com/download
```

#### 步骤 2：下载模型
```bash
ollama pull llama3
# 或
ollama pull qwen:7b
ollama pull mistral
```

#### 步骤 3：启动 Ollama 服务
```bash
ollama serve
```

#### 步骤 4：配置 Flowist
```bash
# .env 配置
OPENAI_API_KEY=ollama  # 任意值即可
OPENAI_MODEL=llama3     # 你下载的模型名
OPENAI_BASE_URL=http://localhost:11434/v1
```

**注意**：本地模型质量可能不如云端模型，建议用于测试。

---

### ✅ Option 5: Azure OpenAI

**适用场景**：企业用户，已有 Azure 订阅。

```bash
# .env 配置
OPENAI_API_KEY=你的Azure_Key
OPENAI_MODEL=gpt-4  # 你的部署名称
OPENAI_BASE_URL=https://你的资源名.openai.azure.com/openai/deployments/你的部署名
```

**获取**：https://portal.azure.com/

---

## 🚀 快速切换指南

### 场景 1：从 OpenAI 切换到 DeepSeek

1. 编辑 `.env` 文件：
```bash
# 注释掉 OpenAI 配置
# OPENAI_API_KEY=sk-proj-xxx
# OPENAI_MODEL=gpt-4o

# 启用 DeepSeek 配置
OPENAI_API_KEY=sk-你的DeepSeek_Key
OPENAI_MODEL=deepseek-chat
OPENAI_BASE_URL=https://api.deepseek.com
```

2. 重启后端服务（Ctrl+C 停止，再运行 `./start_backend.sh`）

3. 完成！无需修改代码

---

### 场景 2：测试本地模型

```bash
# 终端 1：启动 Ollama
ollama serve

# 终端 2：拉取模型（仅首次）
ollama pull llama3

# 修改 .env
OPENAI_API_KEY=ollama
OPENAI_MODEL=llama3
OPENAI_BASE_URL=http://localhost:11434/v1

# 终端 3：启动 Flowist 后端
./start_backend.sh

# 终端 4：启动前端
./start_frontend.sh
```

---

## 🧪 验证配置

### 方法 1：启动后端查看日志
```bash
./start_backend.sh
```

如果配置正确，服务会正常启动。如果 API Key 错误，会在调用时报错。

### 方法 2：在前端测试
1. 启动前端界面
2. 输入简单的测试内容："我很焦虑"
3. 点击生成
4. 如果返回结果，说明配置成功

---

## ❓ 常见问题

### Q: 我应该选择哪个提供商？

| 提供商 | 推荐场景 | 优势 | 劣势 |
|--------|---------|------|------|
| OpenAI | 追求最佳质量 | 质量最好 | 需要国际支付，国内访问慢 |
| DeepSeek | 国内用户 | 便宜、快速、质量好 | 稍逊于 GPT-4o |
| 通义千问 | 阿里云用户 | 中文优化 | 创意性稍弱 |
| Ollama | 隐私/离线 | 完全免费，数据本地 | 质量较低，需要本地算力 |
| Azure | 企业用户 | 合规性好 | 配置复杂，价格高 |

**个人推荐**：
- 🥇 国内用户 → **DeepSeek**（性价比最高）
- 🥈 追求质量 → **OpenAI GPT-4o**
- 🥉 预算有限 → **Ollama 本地模型**

### Q: 切换提供商后生成质量明显下降？

不同模型的能力差异：
- **GPT-4o / GPT-4** - 创意性和共情能力强
- **DeepSeek** - 逻辑性强，创意性稍弱
- **本地模型** - 可能无法理解复杂的 Prompt

**解决方案**：
1. 调整 `app/core/prompt_builder.py` 中的 System Prompt
2. 简化 Prompt 结构，减少复杂指令
3. 增加示例（Few-shot learning）

### Q: 如何同时配置多个提供商？

当前架构一次只能使用一个提供商。如果需要多个，可以：
1. 创建多个 `.env` 文件（`.env.openai`, `.env.deepseek`）
2. 启动时指定：`ENV_FILE=.env.deepseek uvicorn app.main:app`

---

## 📝 配置模板速查

直接复制到你的 `.env` 文件：

```bash
# ===========================================
# Flowist LLM 配置（选择其中一个）
# ===========================================

# 🔹 DeepSeek（国内推荐）
OPENAI_API_KEY=sk-
OPENAI_MODEL=deepseek-chat
OPENAI_BASE_URL=https://api.deepseek.com

# 🔹 OpenAI（官方）
# OPENAI_API_KEY=sk-proj-
# OPENAI_MODEL=gpt-4o
# OPENAI_BASE_URL=

# 🔹 通义千问
# OPENAI_API_KEY=sk-
# OPENAI_MODEL=qwen-plus
# OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# ===========================================
# 其他配置（保持不变）
# ===========================================
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=flowist_knowledge
```

---

**现在你可以自由选择最适合你的 LLM 提供商了！** 🎉
