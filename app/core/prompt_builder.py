"""
Prompt Builder Module

Assembles the complete prompt for LLM generation.
Combines System Prompt + Context + Memory + RAG results.

Implements PRD Section 5 (Core Prompt Design).
"""

from typing import Optional

from app.models.context import ContextPayload
from app.models.user import UserProfile


SYSTEM_PROMPT_TEMPLATE = """# Role
你是一位拥有15年经验的资深正念冥想导师。你的声音温暖、沉稳、充满包容性。你不仅拥有专业的引导技巧（来自知识库），还拥有极强的记忆力（来自记忆库），像一位老朋友一样了解用户。

# Data Sources (CRITICAL)
你必须严格基于以下两类信息进行生成：
1.  **User Memory (长期记忆)**:
    <User_Memory>
    {retrieved_memory_summary}
    </User_Memory>
    *指令*: 利用这些信息建立连贯性。例如，如果用户上次提到失眠，这次可以问候睡眠改善情况。

2.  **Reference Material (专业知识库)**:
    <Reference_Material>
    {retrieved_knowledge_snippets}
    </Reference_Material>
    *指令*: 你的引导词结构、使用的隐喻和呼吸技巧，必须参考上述材料。不要编造不存在的冥想技巧。

# Current Context
- User Name: {user_name}
- Time: {current_time}
- Weather: {weather}
- User Input: {user_input}

# Task
请生成一段冥想引导脚本。
1.  **Connect (连接)**: 利用环境(天气/时间)和记忆建立共情。
2.  **Guide (核心)**: 根据用户 Input，从知识库中选择最合适的技术（如：焦虑->呼吸法；疲劳->身体扫描）。
3.  **Integration (整合)**: 温柔结束。

# Constraints
* **Tone**: 慢速，像在耳边低语。使用短句。
* **Format**: 必须在句子之间标注停顿时间，格式为 `[2s]`, `[5s]`, `[10s]`。这是 TTS 引擎所必需的。
* **Safety**: 如果用户表达极度绝望或自残倾向，停止冥想，给出寻求专业帮助的建议。
"""


class PromptBuilder:
    """
    Builds complete prompts for meditation script generation.
    
    Assembles:
    - System prompt (PRD Section 5)
    - User context (time, weather, location)
    - User memory (retrieved session history)
    - RAG knowledge snippets
    """
    
    def __init__(self):
        self.system_prompt_template = SYSTEM_PROMPT_TEMPLATE
    
    def build_prompt(
        self,
        context_payload: ContextPayload,
        user_profile: Optional[UserProfile] = None,
        memory_summary: str = "No previous sessions found.",
        knowledge_snippets: str = "No specific knowledge retrieved.",
    ) -> str:
        """
        Build the complete prompt for LLM.
        
        Args:
            context_payload: User's current context and feeling input
            user_profile: Optional user profile for personalization
            memory_summary: Retrieved memory from previous sessions
            knowledge_snippets: Retrieved knowledge from RAG
            
        Returns:
            Complete formatted prompt string
        """
        user_name = user_profile.name if user_profile else "朋友"
        
        prompt = self.system_prompt_template.format(
            retrieved_memory_summary=memory_summary,
            retrieved_knowledge_snippets=knowledge_snippets,
            user_name=user_name,
            current_time=context_payload.current_context.local_time,
            weather=context_payload.current_context.weather,
            user_input=context_payload.user_feeling_input,
        )
        
        return prompt
