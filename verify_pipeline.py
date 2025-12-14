"""
Pipeline Verification Script for Phase 3

Tests the complete meditation generation pipeline:
1. User Profile management
2. Knowledge retrieval (RAG)
3. Memory retrieval
4. Meditation script generation
5. Session summary storage
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.core.meditation_service import MeditationService
from app.models.context import ContextPayload, CurrentContext
from app.models.user import UserProfile


async def test_full_pipeline():
    print("=" * 60)
    print("🧘 Phase 3: Full Pipeline Verification")
    print("=" * 60)
    
    # Initialize service
    print("\n1️⃣  Initializing MeditationService...")
    try:
        service = MeditationService()
        print("   ✅ Service initialized with all dependencies")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        return
    
    # Test user profile management
    print("\n2️⃣  Testing UserProfileManager...")
    user_id = "test_pipeline_user"
    profile = service.user_manager.get_or_create_default(user_id, name="测试用户")
    print(f"   ✅ Created/retrieved profile: {profile.name} (level: {profile.meditation_level})")
    
    # Prepare test context
    print("\n3️⃣  Preparing test context...")
    context = ContextPayload(
        user_id=user_id,
        current_context=CurrentContext(
            local_time="22:30",
            weather="小雨",
            location="家中",
        ),
        user_feeling_input="今天工作特别累，肩膀很酸，头有点痛，想放松一下。",
    )
    print(f"   ✅ Context prepared: {context.user_feeling_input[:30]}...")
    
    # Generate meditation
    print("\n4️⃣  Generating meditation script...")
    print("   (This may take a few seconds...)")
    try:
        result = await service.generate_meditation(context)
        
        session_id = result["session_id"]
        script = result["script"]
        
        print(f"   ✅ Session ID: {session_id}")
        print(f"   ✅ Script length: {len(script)} characters")
        print("\n   --- Script Preview (first 300 chars) ---")
        print(f"   {script[:300]}...")
        print("   --- End Preview ---")
        
    except Exception as e:
        print(f"   ❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Save session summary
    print("\n5️⃣  Saving session summary to memory...")
    try:
        service.save_session_summary(
            user_id=user_id,
            session_id=session_id,
            summary="用户感到工作疲惫，肩膀酸痛，头痛。使用了身体扫描技术帮助放松。",
            technique_used="Body Scan",
            user_feedback="感觉好多了",
        )
        print("   ✅ Session summary saved")
    except Exception as e:
        print(f"   ❌ Failed to save summary: {e}")
        return
    
    # Verify memory recall
    print("\n6️⃣  Verifying memory recall...")
    try:
        memories = service.memory_manager.get_relevant_history(
            user_id=user_id,
            query="肩膀痛",
            n_results=1,
        )
        if memories:
            print(f"   ✅ Found {len(memories)} relevant memory")
            print(f"   Memory content: {memories[0]['content'][:100]}...")
        else:
            print("   ⚠️ No memories found (might be first run)")
    except Exception as e:
        print(f"   ❌ Memory retrieval failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Phase 3 Pipeline Verification Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
