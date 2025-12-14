#!/usr/bin/env python3
"""
快速诊断 Flowist 超时问题
"""
import asyncio
import time
from app.rag_service.retriever import KnowledgeRetriever
from app.core.llm_client import LLMClient
from app.models.context import ContextPayload, CurrentContext

async def test_components():
    """逐个测试各组件响应时间"""
    
    # 1. 测试 RAG 检索
    print("1️⃣  测试 RAG 检索...")
    start = time.time()
    try:
        retriever = KnowledgeRetriever()
        result = retriever.retrieve_knowledge("压力大", n_results=2)
        print(f"   ✅ RAG 用时: {time.time() - start:.2f}s")
        print(f"   检索结果长度: {len(result)} 字符")
    except Exception as e:
        print(f"   ❌ RAG 失败: {e}")
        return
    
    # 2. 测试 LLM 调用（简短prompt）
    print("\n2️⃣  测试 LLM 快速调用...")
    start = time.time()
    try:
        client = LLMClient()
        response = await client.generate("说一句话介绍冥想")
        print(f"   ✅ LLM 用时: {time.time() - start:.2f}s")
        print(f"   响应: {response[:50]}...")
    except Exception as e:
        print(f"   ❌ LLM 失败: {e}")
        return
    
    # 3. 测试完整流程（简化的prompt）
    print("\n3️⃣  测试完整生成流程...")
    start = time.time()
    try:
        from app.core.meditation_service import MeditationService
        service = MeditationService()
        
        payload = ContextPayload(
            user_id="test",
            current_context=CurrentContext(
                local_time="22:00",
                weather="大雨",
                location="家中"
            ),
            user_feeling_input="压力大"
        )
        
        script = await service.generate_meditation(payload)
        elapsed = time.time() - start
        print(f"   ✅ 完整流程用时: {elapsed:.2f}s")
        print(f"   生成脚本长度: {len(script)} 字符")
        
        if elapsed > 25:
            print(f"   ⚠️  警告: 耗时过长 ({elapsed:.2f}s)，可能会超时")
        
    except Exception as e:
        print(f"   ❌ 完整流程失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_components())
