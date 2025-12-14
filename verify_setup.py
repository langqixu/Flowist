
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.rag_service.retriever import KnowledgeRetriever
from app.core.llm_client import LLMClient
from app.config import get_settings

async def test_full_flow():
    print("🚀 开始 Flowist 系统自检...")
    print("-" * 50)

    # 1. 验证配置
    print("1️⃣  检查配置...")
    settings = get_settings()
    print(f"   LLM Model: {settings.openai_model}")
    print(f"   Base URL: {settings.openai_base_url}")
    if not settings.openai_api_key:
        print("   ❌ Error: OPENAI_API_KEY 未设置")
        return
    print("   ✅ 配置读取成功")

    # 2. 验证 RAG
    print("\n2️⃣  验证 RAG 知识检索...")
    try:
        retriever = KnowledgeRetriever()
        query = "我最近压力很大，失眠"
        results = retriever.retrieve_knowledge(query, n_results=2)
        if "No relevant knowledge found" in results or not results:
            print("   ⚠️ Warning: 未检索到知识 (可能是知识库为空)")
        else:
            print(f"   ✅ 检索成功。Query: '{query}'")
            print("   --- 检索片段预览 ---")
            print(results[:200] + "...")
            print("   ------------------")
    except Exception as e:
        print(f"   ❌ RAG Error: {str(e)}")
        return

    # 3. 验证 LLM 连接
    print("\n3️⃣  验证 LLM 生成 (DeepSeek)...")
    try:
        client = LLMClient()
        prompt = "你好，请用一句话介绍冥想的好处。"
        print(f"   发送 Prompt: '{prompt}'")
        response = await client.generate(prompt)
        print(f"   ✅ LLM 响应成功: {response}")
    except Exception as e:
        print(f"   ❌ LLM Error: {str(e)}")
        return

    print("\n" + "=" * 50)
    print("🎉 系统自检通过！一切准备就绪。")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_full_flow())
