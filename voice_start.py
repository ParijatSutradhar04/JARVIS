"""
Quick Start Script for JARVIS Voice Mode
Fast path to testing realtime voice interaction
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def quick_voice_start():
    """Quick start for voice mode testing"""
    print("🎤 JARVIS Quick Voice Start")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ OpenAI API key not configured")
        print("Please set OPENAI_API_KEY in your .env file")
        return
    
    print("✅ API key found")
    
    try:
        # Import and initialize
        print("🔄 Importing agent...")
        from agent import VoiceAgent
        
        print("🤖 Initializing JARVIS...")
        agent = VoiceAgent(openai_api_key=api_key)
        print("🔄 Calling agent.initialize()...")
        await agent.initialize()
        print("✅ Agent initialized successfully")
        
        if not agent.realtime_client:
            print("❌ Realtime client failed to initialize")
            # print("Falling back to text mode...")
            # await agent.interactive_text_mode()
            return
        
        if not agent.realtime_client.is_connected:
            print("❌ Failed to connect to OpenAI Realtime API")
            print("This might be because:")
            print("• Invalid API key")
            print("• Network connectivity issues")
            print("• Realtime API not available in your region")
            # print("\nFalling back to text mode...")
            # await agent.interactive_text_mode()
            return
        
        print("✅ Connected to OpenAI Realtime API")
        print("✅ Audio system ready")
        
        print("\n🎤 Starting voice conversation...")
        print("🗣️ Try saying:")
        print("   • 'Hello JARVIS, what time is it?'")
        print("   • 'Execute Python code to calculate 12 times 8'")
        print("   • 'What's the weather in Paris?'")
        print("   • 'Summarize my emails from today'")
        print("   • 'Remember that I have a dentist appointment next week'")
        print("\nPress Ctrl+C to stop")
        
        # Start voice conversation
        await agent.start_voice_conversation()
        
    except KeyboardInterrupt:
        print("\n👋 Voice session ended")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Run 'python install.py' to install dependencies")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check your configuration and try again")
    finally:
        if 'agent' in locals():
            await agent.cleanup()

async def test_realtime_connection():
    """Test just the realtime connection without full agent"""
    print("🔌 Testing Realtime API Connection")
    print("-" * 40)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No API key")
        return False
    
    try:
        print("🔄 Importing RealtimeClient...")
        from realtime_client import RealtimeClient
        
        print("🔄 Creating client...")
        client = RealtimeClient(api_key)
        
        print("🔄 Attempting connection...")
        await client.initialize_session()
        print("✅ Connection attempt completed")
        
        if client.is_connected:
            print("✅ Successfully connected to OpenAI Realtime API")
            await client.cleanup()
            return True
        else:
            print("❌ Failed to connect")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

async def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            success = await test_realtime_connection()
            if success:
                print("\n🎉 Connection successful! Run without 'test' to start voice mode.")
        elif sys.argv[1] == "help":
            print("🤖 JARVIS Quick Start")
            print("python voice_start.py        - Start voice mode")
            print("python voice_start.py test   - Test connection only") 
            print("python voice_start.py help   - Show this help")
        else:
            await quick_voice_start()
    else:
        await quick_voice_start()

if __name__ == "__main__":
    asyncio.run(main())
