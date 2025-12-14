"""
TTS Pipeline Verification Script

Tests the complete TTS pipeline:
1. ScriptParser sentence/pause extraction
2. OpenAI TTS provider (if API key available)
3. AudioService orchestration
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())


def test_script_parser():
    """Test ScriptParser functionality."""
    print("\n1️⃣  Testing ScriptParser...")
    
    from app.audio_service.script_parser import ScriptParser, SegmentType
    
    parser = ScriptParser()
    
    # Test script with pauses
    test_script = """你好，欢迎来到冥想时间。[3s]
现在请闭上眼睛。[5s]
深呼吸。感受空气进入你的身体。[10s]
很好。"""
    
    segments = parser.parse(test_script)
    
    print(f"   解析出 {len(segments)} 个片段:")
    
    text_count = 0
    pause_count = 0
    
    for i, seg in enumerate(segments):
        if seg.type == SegmentType.TEXT:
            text_count += 1
            print(f"   [{i}] TEXT: \"{seg.content[:30]}...\"" if len(seg.content) > 30 else f"   [{i}] TEXT: \"{seg.content}\"")
        else:
            pause_count += 1
            print(f"   [{i}] PAUSE: {seg.duration}s")
    
    print(f"   ✅ 文本片段: {text_count}, 停顿片段: {pause_count}")
    
    # Test streaming parser
    print("\n   测试流式解析...")
    buffer = ""
    chunks = ["你好，", "欢迎来到冥想", "时间。", "[3s]", "现在请", "闭上眼睛。"]
    total_segments = 0
    
    for chunk in chunks:
        segs, buffer = parser.parse_streaming(chunk, buffer)
        if segs:
            total_segments += len(segs)
            print(f"   Chunk \"{chunk}\" -> {len(segs)} segment(s)")
    
    print(f"   ✅ 流式解析完成，共 {total_segments} 个完整片段")
    return True


async def test_tts_provider(provider_type="openai"):
    """Test TTS provider (requires API key)."""
    print(f"\n2️⃣  Testing {provider_type.upper()} TTS Provider...")
    
    from app.config import get_settings
    settings = get_settings()
    
    provider = None
    
    try:
        if provider_type == "openai":
            if not settings.openai_api_key:
                print("   ⚠️ OPENAI_API_KEY 未配置，跳过 TTS 测试")
                return False
            from app.audio_service.providers.openai import OpenAITTSProvider
            provider = OpenAITTSProvider()
            
        elif provider_type == "minimax":
            if not settings.minimax_api_key or not settings.minimax_group_id:
                print("   ⚠️ MINIMAX_API_KEY/GROUP_ID 未配置，跳过 TTS 测试")
                return False
            from app.audio_service.providers.minimax import MiniMaxTTSProvider
            provider = MiniMaxTTSProvider()
            
        print(f"   Provider 初始化成功")
        print(f"   支持的声音: {provider.supported_voices}")
        print(f"   默认声音: {provider.default_voice}")
        
        # Generate a short audio
        test_text = "你好，这是一个测试。"
        print(f"   生成测试音频: \"{test_text}\"")
        
        audio_data = b""
        async for chunk in provider.generate_audio_stream(test_text):
            audio_data += chunk
        
        print(f"   ✅ 生成音频大小: {len(audio_data)} bytes")
        
        # Save test audio
        test_audio_path = f"test_tts_{provider_type}.mp3"
        with open(test_audio_path, "wb") as f:
            f.write(audio_data)
        print(f"   ✅ 已保存到 {test_audio_path}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ TTS 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_audio_service():
    """Test AudioService orchestration."""
    print("\n3️⃣  Testing AudioService...")
    
    from app.config import get_settings
    
    settings = get_settings()
    
    if not settings.openai_api_key:
        print("   ⚠️ OPENAI_API_KEY 未配置，跳过 AudioService 测试")
        return False
    
    from app.audio_service.audio_service import AudioService, AudioChunkType
    
    try:
        service = AudioService()
        print("   AudioService 初始化成功")
        
        # Test with a short script
        test_script = "请放松。[2s]深呼吸。"
        print(f"   处理脚本: \"{test_script}\"")
        
        chunk_count = 0
        total_audio = 0
        
        async for chunk in service.generate_audio_from_text(test_script):
            chunk_count += 1
            if chunk.type == AudioChunkType.AUDIO:
                total_audio += len(chunk.data)
                print(f"   [Chunk {chunk_count}] AUDIO: {len(chunk.data)} bytes")
            elif chunk.type == AudioChunkType.SILENCE:
                print(f"   [Chunk {chunk_count}] SILENCE: {chunk.duration}s")
        
        print(f"   ✅ 生成 {chunk_count} 个音频块，总大小 {total_audio} bytes")
        return True
        
    except Exception as e:
        print(f"   ❌ AudioService 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("=" * 60)
    print("🔊 Phase 4: TTS Pipeline Verification")
    print("=" * 60)
    
    # Check for arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="minimax", help="TTS provider to test (openai/minimax)")
    parser.add_argument("--key", help="API Key for the provider")
    parser.add_argument("--group-id", help="Group ID for Minimax")
    args = parser.parse_args()
    
    # Inject env vars if provided
    if args.key:
        if args.provider == "minimax":
            os.environ["MINIMAX_API_KEY"] = args.key
        elif args.provider == "openai":
            os.environ["OPENAI_API_KEY"] = args.key
            
    if args.group_id and args.provider == "minimax":
        os.environ["MINIMAX_GROUP_ID"] = args.group_id
        
    # Also set the provider in config (hacky for test)
    os.environ["TTS_PROVIDER"] = args.provider
    
    # Test 1: ScriptParser (no API needed)
    parser_ok = test_script_parser()
    
    # Test 2: TTS Provider (needs API key)
    tts_ok = await test_tts_provider(args.provider)
    
    # Test 3: AudioService (needs API key)
    # Note: AudioService will pick up TTS_PROVIDER from env
    service_ok = await test_audio_service()
    
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print(f"   ScriptParser: {'✅' if parser_ok else '❌'}")
    print(f"   TTS Provider ({args.provider}): {'✅' if tts_ok else '⚠️'}")
    print(f"   AudioService: {'✅' if service_ok else '⚠️'}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
