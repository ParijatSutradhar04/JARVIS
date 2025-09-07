"""
Test script to check OpenAI API connectivity and Realtime API availability
"""
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_openai_connectivity():
    """Test basic OpenAI API connectivity"""
    print("🔍 Testing OpenAI API Connectivity")
    print("=" * 50)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return False
    
    print(f"✅ API key found (length: {len(api_key)})")
    
    try:
        # Test basic OpenAI import
        print("🔄 Testing OpenAI import...")
        from openai import AsyncOpenAI
        print("✅ OpenAI library imported successfully")
        
        # Test client initialization
        print("🔄 Testing client initialization...")
        client = AsyncOpenAI(api_key=api_key)
        print("✅ AsyncOpenAI client created")
        
        # Test basic API call
        print("🔄 Testing basic API call...")
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, this is a test."}],
            max_tokens=10
        )
        print("✅ Basic API call successful")
        print(f"Response: {response.choices[0].message.content}")
        
        # Test Realtime API availability
        print("🔄 Testing Realtime API access...")
        try:
            # Try to create a realtime session (this will fail if not available)
            import websockets
            import json
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            # Test WebSocket connection (timeout quickly)
            uri = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
            
            try:
                async with websockets.connect(uri, additional_headers=headers, ping_timeout=5, close_timeout=5) as websocket:
                    # Send session configuration
                    session_config = {
                        "type": "session.update",
                        "session": {
                            "modalities": ["text", "audio"],
                            "instructions": "You are a helpful assistant.",
                            "voice": "alloy",
                            "input_audio_format": "pcm16",
                            "output_audio_format": "pcm16",
                            "input_audio_transcription": {
                                "model": "whisper-1"
                            }
                        }
                    }
                    
                    await websocket.send(json.dumps(session_config))
                    
                    # Wait for response with timeout
                    response = await asyncio.wait_for(websocket.recv(), timeout=10)
                    response_data = json.loads(response)
                    
                    if response_data.get("type") == "session.updated":
                        print("✅ Realtime API is accessible and working!")
                        return True
                    else:
                        print(f"⚠️ Unexpected response: {response_data}")
                        return False
                        
            except asyncio.TimeoutError:
                print("❌ Realtime API connection timed out")
                return False
            except websockets.exceptions.WebSocketException as e:
                print(f"❌ WebSocket error: {e}")
                return False
            except Exception as e:
                print(f"❌ Realtime API error: {e}")
                return False
                
        except ImportError as e:
            print(f"❌ Missing dependency: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_openai_connectivity())
    if result:
        print("\n🎉 All tests passed! OpenAI and Realtime API are working.")
    else:
        print("\n💥 Some tests failed. Check the errors above.")
