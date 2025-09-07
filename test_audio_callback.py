#!/usr/bin/env python3
"""Test the fixed audio callback without full agent import"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_audio_callback_fix():
    """Test if the audio callback fix resolves the event loop issue"""
    print("🔍 Testing Audio Callback Fix")
    print("=" * 40)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return
    
    print(f"✅ API key found")
    
    try:
        print("🔄 Importing RealtimeClient...")
        from realtime_client import RealtimeClient
        print("✅ RealtimeClient imported")
        
        print("🔄 Creating RealtimeClient...")
        client = RealtimeClient(api_key)
        
        print("🔄 Initializing session...")
        await client.initialize_session(tools=[])  # No tools for simple test
        print(f"✅ Session initialized, connected: {client.is_connected}")
        
        if client.is_connected:
            print("🔄 Setting up audio...")
            client.setup_audio()
            print("✅ Audio setup completed")
            
            print("🎤 Testing for 5 seconds - speak into microphone...")
            client.is_recording = True
            
            if client.input_stream:
                client.input_stream.start_stream()
                print("🔴 Recording started")
                
                # Let it run for 5 seconds
                await asyncio.sleep(5)
                
                client.is_recording = False
                client.input_stream.stop_stream()
                print("🔴 Recording stopped")
            
            print("✅ Test completed successfully!")
        else:
            print("❌ Not connected")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'client' in locals():
            await client.cleanup()

if __name__ == "__main__":
    asyncio.run(test_audio_callback_fix())
