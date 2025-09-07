"""
Quick connectivity test with timeouts
"""
import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def quick_connectivity_test():
    """Quick test with proper timeouts"""
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"API key present: {bool(api_key)}")
    
    # Test basic internet connectivity
    print("Testing internet connectivity...")
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get("https://httpbin.org/get") as response:
                if response.status == 200:
                    print("✅ Internet connectivity OK")
                else:
                    print(f"⚠️ HTTP status: {response.status}")
    except Exception as e:
        print(f"❌ Internet connectivity failed: {e}")
        return False
    
    # Test OpenAI API endpoint
    print("Testing OpenAI API endpoint...")
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 5
        }
        
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post("https://api.openai.com/v1/chat/completions", 
                                   headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ OpenAI API accessible")
                    print(f"Response: {result['choices'][0]['message']['content']}")
                elif response.status == 401:
                    print("❌ Invalid API key")
                    return False
                elif response.status == 429:
                    print("❌ Rate limited")
                    return False
                else:
                    text = await response.text()
                    print(f"❌ API error {response.status}: {text}")
                    return False
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False
    
    # Test Realtime API WebSocket endpoint
    print("Testing Realtime API WebSocket...")
    try:
        import websockets
        import json
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        uri = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
        
        # Very short timeout for this test
        async with websockets.connect(uri, additional_headers=headers, 
                                    ping_timeout=3, close_timeout=2, 
                                    open_timeout=5) as websocket:
            print("✅ Realtime API WebSocket connection established")
            
            # Try to send a simple message
            session_config = {
                "type": "session.update",
                "session": {
                    "modalities": ["text"],
                    "instructions": "You are a helpful assistant."
                }
            }
            
            await websocket.send(json.dumps(session_config))
            
            # Wait for response with short timeout
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=3)
                response_data = json.loads(response)
                print(f"✅ Realtime API responded: {response_data.get('type', 'unknown')}")
                return True
            except asyncio.TimeoutError:
                print("⚠️ Realtime API connection established but no response received")
                return True  # Connection worked, just slow response
                
    except websockets.exceptions.InvalidStatusCode as e:
        if e.status_code == 401:
            print("❌ Realtime API: Invalid API key")
        elif e.status_code == 403:
            print("❌ Realtime API: Access forbidden (may not be available in your region)")
        else:
            print(f"❌ Realtime API: HTTP {e.status_code}")
        return False
    except Exception as e:
        print(f"❌ Realtime API WebSocket failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(quick_connectivity_test())
    print(f"\nResult: {'✅ PASS' if result else '❌ FAIL'}")
