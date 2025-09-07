#!/usr/bin/env python3
"""
Simple voice test to verify function call response fixes
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_voice_simple():
    """Simple voice test focusing on function calls"""
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return
    
    print("✅ API key found")
    
    try:
        # Import realtime client directly
        from realtime_client import RealtimeClient
        print("✅ RealtimeClient imported")
        
        # Create simple tools for testing
        tools = [
            {
                "type": "function",
                "name": "get_time",
                "description": "Get the current time",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "type": "function", 
                "name": "get_weather",
                "description": "Get weather information for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to get weather for"
                        }
                    },
                    "required": ["location"]
                }
            }
        ]
        
        # Create realtime client
        client = RealtimeClient(api_key)
        print("✅ RealtimeClient created")
        
        # Define function handler
        async def handle_function_call(name: str, args: dict):
            """Simple function call handler"""
            print(f"🔧 Function call: {name} with args: {args}")
            
            if name == "get_time":
                from datetime import datetime
                result = f"Current time: {datetime.now().strftime('%I:%M %p')}"
            elif name == "get_weather":
                location = args.get("location", "unknown")
                result = f"🌤️ Weather in {location}: 25°C, partly cloudy"
            else:
                result = f"Function {name} executed successfully"
            
            print(f"✅ Function result: {result}")
            return result
        
        # Set handlers
        client.set_event_handlers(
            on_function_call=handle_function_call
        )
        
        # Initialize session
        print("🔄 Initializing session...")
        await client.initialize_session(tools=tools)
        print("✅ Session initialized")
        
        # Setup audio
        print("🔄 Setting up audio...")
        client.setup_audio()
        print("✅ Audio setup complete")
        
        # Start conversation
        print("\n" + "="*50)
        print("🎤 VOICE MODE ACTIVE")
        print("Try saying: 'What time is it?' or 'What's the weather in London?'")
        print("Press Ctrl+C to stop")
        print("="*50)
        
        await client.start_conversation()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'client' in locals():
            await client.cleanup()

if __name__ == "__main__":
    asyncio.run(test_voice_simple())
