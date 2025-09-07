#!/usr/bin/env python3
"""Debug the realtime client initialization issue"""

import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

async def debug_realtime_initialization():
    """Debug what's failing in realtime client initialization"""
    print("🔍 Debugging Realtime Client Initialization")
    print("=" * 50)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return
    
    print(f"✅ API key found (length: {len(api_key)})")
    
    try:
        print("🔄 Importing RealtimeClient...")
        from realtime_client import RealtimeClient
        print("✅ RealtimeClient imported")
        
        print("🔄 Creating RealtimeClient instance...")
        client = RealtimeClient(api_key)
        print(f"✅ RealtimeClient created, is_connected: {client.is_connected}")
        
        print("🔄 Getting realtime tools...")
        from tools import get_tools_for_realtime
        realtime_tools = get_tools_for_realtime()
        print(f"✅ Got {len(realtime_tools)} realtime tools")
        
        print("🔄 Calling initialize_session...")
        await client.initialize_session(tools=realtime_tools)
        print(f"✅ initialize_session completed, is_connected: {client.is_connected}")
        
        if client.is_connected:
            print("🎉 Realtime client successfully connected!")
            
            print("🔄 Testing setup_audio...")
            client.setup_audio()
            print("✅ Audio setup completed")
            
        else:
            print("❌ Realtime client not connected after initialization")
            
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'client' in locals():
            await client.cleanup()

if __name__ == "__main__":
    asyncio.run(debug_realtime_initialization())
