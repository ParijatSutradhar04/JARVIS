"""
Simple sync connectivity test
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_connectivity():
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"API key present: {bool(api_key)}")
    
    # Test internet
    print("Testing internet...")
    try:
        response = requests.get("https://httpbin.org/get", timeout=5)
        if response.status_code == 200:
            print("✅ Internet OK")
        else:
            print(f"⚠️ Internet status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Internet failed: {e}")
        return False
    
    # Test OpenAI API
    print("Testing OpenAI API...")
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 5
        }
        
        response = requests.post("https://api.openai.com/v1/chat/completions", 
                               headers=headers, json=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ OpenAI API OK")
            print(f"Response: {result['choices'][0]['message']['content']}")
            return True
        elif response.status_code == 401:
            print("❌ Invalid API key")
        elif response.status_code == 429:
            print("❌ Rate limited")
        elif response.status_code == 403:
            print("❌ Access forbidden")
        else:
            print(f"❌ API error {response.status_code}: {response.text}")
        
        return False
        
    except Exception as e:
        print(f"❌ OpenAI API failed: {e}")
        return False

if __name__ == "__main__":
    result = test_connectivity()
    print(f"\nResult: {'✅ PASS' if result else '❌ FAIL'}")
    
    if not result:
        print("\nPossible issues:")
        print("• Invalid API key")
        print("• Network connectivity problems") 
        print("• Firewall blocking requests")
        print("• OpenAI API down or rate limited")
        print("• Realtime API not available in your region")
