# **Project Specification: Flowist \- Context-Aware & Memory-Enhanced Meditation Agent**

## **1\. 项目概述 (Project Overview)**

**Flowist** 是一个基于生成式 AI 的智能冥想 Agent。与传统播放预录音频的 App 不同，它通过主动询问了解用户当下的身心状态，结合环境上下文（时间、天气）、用户长期记忆（Memory）以及专业知识库（RAG），实时生成并流式播放一段完全定制化的冥想引导语音。  
**核心价值主张：**

* **Hyper-Personalization**: 此时此刻，只为你生成。  
* **Context-Awareness**: 感知你的疲惫、感知窗外的雨声。  
* **Continuity**: 像老朋友一样记得你的历史状态。  
* **Professionalism**: 基于私有知识库，确保引导词的专业度。

## **2\. 系统架构 (System Architecture)**

### **2.1 逻辑流程图 (Logic Flow)**

1. **Client Init**: App 获取设备上下文 (Time, Weather, Location)。  
2. **Check-in**: Agent 主动提问 (e.g., "昨晚睡得好吗？") \-\> 用户语音/文字回答。  
3. **Backend Processing**:  
   * **Retrieval (RAG)**: 根据用户回答，在向量数据库中检索相关的冥想技巧/脚本片段。  
   * **Memory Lookup**: 检索用户画像及最近 5 次会话摘要 (Summary)。  
   * **Prompt Assembly**: 组装 Context \+ Memory \+ Knowledge \+ System Prompt。  
4. **Generation**: 调用 LLM (GPT-4o/Claude 3.5) 生成带时间戳的脚本。  
5. **TTS & Audio**: 将脚本实时转为语音流，并与背景白噪音 (Ambience) 混音。  
6. **Post-Session**: 总结本次会话，更新 Long-term Memory。

### **2.2 技术栈推荐 (Tech Stack Recommendation)**

* **Backend**: Python (FastAPI)  
* **LLM**: OpenAI GPT-4o (or Claude 3.5 Sonnet for better creative writing)  
* **Vector DB**: Pinecone / ChromaDB (用于知识库和长期记忆)  
* **TTS**: OpenAI TTS (HD model) / ElevenLabs (推荐，支持情感控制)  
* **Orchestration**: LangChain / LangGraph

## **3\. 功能需求 (Functional Requirements)**

### **3.1 上下文感知与输入 (Context Module)**

* **环境参数**: local\_time (e.g., "22:30"), weather (e.g., "Rainy"), location\_type (e.g., "Office/Home").  
* **用户输入**: 捕捉用户对当前状态的描述 (e.g., "肩膀痛", "很焦虑", "刚吵完架")。

### **3.2 记忆系统 (Memory System)**

* **User Profile**: 基础信息 (称呼, 职业, 冥想经验等级)。  
* **Session History**: 存储每次冥想的摘要。  
  * *Input*: 用户当时的痛点。  
  * *Solution*: 采用的冥想技术。  
  * *Feedback*: 用户反馈的效果。  
* **Recall Mechanism**: 在生成新脚本时，必须提取与当前 User Input 语义相关的历史记录 (e.g., 用户说“头痛”，检索过去关于“头痛”的记录)。

### **3.3 知识库检索 (RAG Module)**

* **Content Library**: 系统需加载私有的 .md / .txt 文档，包含：  
  * 引导词模板 (Scripts)  
  * 呼吸法技巧 (Techniques, e.g., Box Breathing, 4-7-8)  
  * 哲学隐喻 (Metaphors, e.g., "Leaves on a stream")  
* **Retrieval**: 根据 User Input 的关键词（如“焦虑”、“失眠”）检索 Top-3 相关片段。

### **3.4 脚本生成与音频 (Generation Engine)**

* **Output Format**: 纯文本，但包含停顿控制标记 \[5s\]。  
* **Audio Mixing**: 前端根据后端返回的 bg\_music\_tag (e.g., rain, forest) 播放本地白噪音循环，TTS 语音流覆盖在其上。

## **4\. 数据模型设计 (Data Models)**

### **4.1 输入 Payload (Frontend \-\> Backend)**

{  
  "user\_id": "u12345",  
  "current\_context": {  
    "local\_time": "23:15",  
    "weather": "Heavy Rain",  
    "location": "Home"  
  },  
  "user\_feeling\_input": "今天工作压力很大，脑子停不下来，肩膀很紧。"  
}

### **4.2 记忆结构 (Stored in VectorDB)**

{  
  "session\_id": "s\_9876",  
  "date": "2023-10-27",  
  "summary": "User reported high anxiety due to deadline. Shoulders were tense.",  
  "technique\_used": "Body Scan",  
  "user\_feedback": "Felt better but still distracted."  
}

### **4.3 LLM 生成结构 (Backend Internal)**

虽然 LLM 输出是文本流，但 Prompt 中应要求包含元数据：  
\[META\]  
background\_sound: rain\_heavy  
technique: body\_scan\_shoulders  
\[/META\]

\[Intro\]  
...Script content...

## **5\. 核心 Prompt 设计 (System Prompt)**

**这是本项目的核心资产，请在代码中完整实现此 Prompt 逻辑。**  
\# Role  
你是一位拥有15年经验的资深正念冥想导师。你的声音温暖、沉稳、充满包容性。你不仅拥有专业的引导技巧（来自知识库），还拥有极强的记忆力（来自记忆库），像一位老朋友一样了解用户。

\# Data Sources (CRITICAL)  
你必须严格基于以下两类信息进行生成：  
1\.  \*\*User Memory (长期记忆)\*\*:  
    \<User\_Memory\>  
    {retrieved\_memory\_summary}  
    \</User\_Memory\>  
    \*指令\*: 利用这些信息建立连贯性。例如，如果用户上次提到失眠，这次可以问候睡眠改善情况。

2\.  \*\*Reference Material (专业知识库)\*\*:  
    \<Reference\_Material\>  
    {retrieved\_knowledge\_snippets}  
    \</Reference\_Material\>  
    \*指令\*: 你的引导词结构、使用的隐喻和呼吸技巧，必须参考上述材料。不要编造不存在的冥想技巧。

\# Current Context  
\- User Name: {user\_name}  
\- Time: {current\_time}  
\- Weather: {weather}  
\- User Input: {user\_input}

\# Task  
请生成一段冥想引导脚本。  
1\.  \*\*Connect (连接)\*\*: 利用环境(天气/时间)和记忆建立共情。  
2\.  \*\*Guide (核心)\*\*: 根据用户 Input，从知识库中选择最合适的技术（如：焦虑-\>呼吸法；疲劳-\>身体扫描）。  
3\.  \*\*Integration (整合)\*\*: 温柔结束。

\# Constraints  
\* \*\*Tone\*\*: 慢速，像在耳边低语。使用短句。  
\* \*\*Format\*\*: 必须在句子之间标注停顿时间，格式为 \`\[2s\]\`, \`\[5s\]\`, \`\[10s\]\`。这是 TTS 引擎所必需的。  
\* \*\*Safety\*\*: 如果用户表达极度绝望或自残倾向，停止冥想，给出寻求专业帮助的建议。

\# Example Output  
\[Intro\]  
{user\_name}，晚上好。\[2s\] 听着窗外的大雨，很高兴你能在这个时刻选择照顾自己。\[3s\]  
我记得上次你说肩膀一直很痛，今天感觉怎么样？\[3s\]

\[Body\]  
让我们先找一个舒服的姿势。\[5s\]  
正如我们在练习中所说的，把注意力带到呼吸上... (此处结合 Knowledge Base 内容) ... \[10s\]

## **6\. 开发实施步骤 (Implementation Guide for AI)**

请按照以下步骤生成代码：

### **Phase 1: 基础架构与 RAG**

1. 设置 FastAPI 项目结构。  
2. 配置 OpenAI API 连接。  
3. 实现 **Vector Store (ChromaDB/Pinecone)** 的初始化代码：  
   * 编写一个脚本 ingest\_knowledge.py，用于读取本地 .txt 知识库文件，切片(Chunking)，嵌入(Embedding)并存入数据库。  
   * 实现 retrieve\_knowledge(query) 函数。

### **Phase 2: 记忆模块**

1. 设计 MemoryManager 类。  
2. 实现 add\_session\_summary(user\_id, summary)：每次结束后调用 LLM 总结并存储。  
3. 实现 get\_relevant\_history(user\_id, query)：根据当前用户输入，检索相关的历史状态。

### **Phase 3: Agent 核心逻辑**

1. 编写 meditation\_service.py。  
2. 实现 Prompt 组装逻辑：System Prompt \+ Context \+ RAG Result \+ Memory Result。  
3. 调用 LLM (Stream mode) 并处理返回的文本流。

### **Phase 4: 音频处理 (Optional Placeholder)**

1. 创建一个 Mock 的 TTS 接口，或者接入 OpenAI Audio API (speech)。  
2. 确保能解析文本中的 \[5s\] 标记，在发送给 TTS 之前将其分离，用于前端控制播放器暂停，或者生成对应的静音音频段。

### **Phase 5: Web 前端体验界面 (PM 调试专用)**

为了让产品经理和测试人员能够**直观体验** Flowist Agent，需要构建一个**零门槛的网页界面**。这个界面就像一个"模拟 App"，让你通过浏览器快速测试 Agent 的效果。

#### **界面布局示意**

想象一个简洁的单页面应用，从上到下分为三个区域：

**📝 区域 1: 输入你的当前状态 (顶部)**  
```
┌─────────────────────────────────────────┐
│ 💬 告诉我你现在的感受                    │
│ ┌─────────────────────────────────────┐ │
│ │ 例如："肩膀很紧，今天工作压力很大     │ │
│ │       脑子停不下来..."              │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**🌍 区域 2: 设置环境上下文 (中部)**  
```
┌────────────────────────────────────────┐
│  🕐 当前时间:  [ 23:15 ▼ ]            │
│  ☁️ 天气状况:  [ 大雨 ▼ ]             │
│  📍 所在地点:  [ 家中 ▼ ]             │
│                                        │
│     [ 🧘 生成冥想引导 ]  (大按钮)       │
└────────────────────────────────────────┘
```

**✨ 区域 3: 查看生成结果 (底部)**  
```
┌─────────────────────────────────────────┐
│ 🎙️ 冥想引导脚本                         │
│ ┌─────────────────────────────────────┐ │
│ │ {user_name}，晚上好。[2s]            │ │
│ │ 听着窗外的大雨，很高兴你能在这个时刻  │ │
│ │ 选择照顾自己...[3s]                  │ │
│ │ (脚本会像打字机一样逐字显示)          │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 🔊 [▶️ 播放语音] (如果已接入 TTS)        │
└─────────────────────────────────────────┘
```

#### **使用流程 (非技术人员也能轻松操作)**

1. **打开浏览器**，访问 `http://localhost:8501`（开发人员会帮你启动服务）  
2. **填写表单**：
   * 在文本框中输入你现在的感受（就像和朋友聊天一样）
   * 选择当前时间、天气、地点
3. **点击"生成冥想引导"按钮**，等待 1-2 秒  
4. **观看结果**：
   * 冥想脚本会**实时逐字显示**（就像 ChatGPT 打字效果）
   * 如果已接入 TTS，可以点击播放按钮**听到语音**
5. **调整测试**：可以修改输入，再次点击生成，测试不同场景

#### **设计原则**

* **极简主义**: 整个界面只有一个页面，所有操作一目了然。  
* **零培训成本**: 不需要阅读说明书，看到界面就知道如何操作。  
* **快速迭代验证**: PM 可以快速测试不同的用户输入，验证 Agent 的响应质量。  
* **技术实现透明**: 使用 Streamlit/Gradio，开发人员 1 小时内即可搭建完成。

#### **验收标准**

当这个界面完成后，你（PM）应该能够：
- [ ] 不需要任何帮助，独立打开界面并成功生成一段冥想脚本。  
- [ ] 测试至少 3 种不同的场景（如：焦虑场景、失眠场景、疲劳场景）。  
- [ ] 清晰看到 Agent 是否根据你的输入生成了个性化的内容。

## **7\. 关键注意事项 (Critical Notes)**

* **Latency Control**: RAG 和 LLM 生成需要时间。建议使用 **Streaming Response**，让用户在 1-2 秒内听到第一句话，而不是等待生成完毕。  
* **Privacy**: 用户的心理健康数据非常敏感。在存储到向量数据库时，确保数据是匿名化处理的，或者遵循严格的数据隐私标准。  
* **Fallback**: 如果 RAG 检索失败（没有相关知识），应回退到通用的、安全的"观呼吸"引导模式。