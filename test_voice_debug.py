#!/usr/bin/env python3
"""Test voice agent with debugging to identify repetition issues"""

import asyncio
import os
import logging
from dotenv import load_dotenv

# Set up detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

load_dotenv()

async def test_voice_with_debugging():
    """Test voice agent with detailed logging"""
    print("🔍 Testing Voice Agent with Debugging")
    print("=" * 50)
    
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
            
            print("🎤 Testing for 10 seconds - speak into microphone...")
            print("Say: 'Hello, can you hear me?'")
            client.is_recording = True
            
            if client.input_stream:
                client.input_stream.start_stream()
                print("🔴 Recording started")
                
                # Let it run for 10 seconds
                await asyncio.sleep(10)
                
                client.is_recording = False
                client.input_stream.stop_stream()
                print("🔴 Recording stopped")
            
            print("✅ Test completed!")
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
    asyncio.run(test_voice_with_debugging())
