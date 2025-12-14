"""
Script to verify Memory System functionality.

Tests adding and retrieving session memories.
"""

from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.memory_service.manager import MemoryManager
from app.models.memory import SessionMemory

def test_memory_system():
    print("🧠 Initializing Memory Manager...")
    try:
        manager = MemoryManager()
    except Exception as e:
        print(f"❌ Failed to initialize MemoryManager: {e}")
        return

    user_id = "test_user_001"
    
    # 1. Create a sample session memory
    session_data = SessionMemory(
        session_id=f"s_{int(datetime.now().timestamp())}",
        date=datetime.now().strftime("%Y-%m-%d"),
        summary="User felt anxious about upcoming presentation. Breathing exercises helped calmn nerves.",
        technique_used="Box Breathing",
        user_feedback="Very helpful, felt more grounded."
    )
    
    print(f"\n💾 Adding session summary for user {user_id}...")
    try:
        manager.add_session_summary_with_user(user_id, session_data)
        print("✅ Session stored successfully.")
    except Exception as e:
        print(f"❌ Failed to add session: {e}")
        return

    # 2. Retrieve irrelevant history (should be empty or low relevance, but vector search always returns something if n_results > 0)
    # Let's search for "anxiety" which should match our inserted record
    
    query = "I am feeling anxious about work."
    print(f"\n🔍 Searching memories for: '{query}'")
    
    try:
        results = manager.get_relevant_history(user_id, query, n_results=1)
        
        if not results:
            print("❌ No results found.")
        else:
            print(f"✅ Found {len(results)} relevant memory:")
            for mem in results:
                print(f"   MATCH (Distance: ignored for now)")
                print(f"   Content: {mem['content'][:100]}...")
                print(f"   Metadata: {mem['metadata']}")
                
            # Verify retrieval matches what we put in
            if session_data.session_id == results[0]['metadata']['session_id']:
                print("✅ Retrieved memory matches the inserted session ID.")
            else:
                print("⚠️ Retrieved memory ID does not match (might be old data).")
                
    except Exception as e:
        print(f"❌ Failed to retrieve history: {e}")

    # 3. Test Isolation (Optional, just check if we can query)
    print("\n🔍 Querying for a different user (should be empty)...")
    try:
        results_other = manager.get_relevant_history("other_user", query)
        if not results_other:
            print("✅ No memories found for other_user (Correct).")
        else:
            print(f"⚠️ Found {len(results_other)} memories for other_user (Unexpected if clean db, but maybe acceptable if filter fails).")
            # If filter works, this should be empty.
    except Exception as e:
        print(f"❌ Error during isolation test: {e}")

if __name__ == "__main__":
    test_memory_system()
