"""
Final API Access Test - Regular vs Realtime API
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_regular_api():
    """Test regular OpenAI API"""
    print("🔍 Testing Regular OpenAI API...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Test models endpoint first (simpler)
        response = requests.get("https://api.openai.com/v1/models", 
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            models = response.json()
            print("✅ Regular API accessible")
            
            # Check for realtime models
            realtime_models = [model for model in models['data'] 
                             if 'realtime' in model['id']]
            
            if realtime_models:
                print(f"✅ Found {len(realtime_models)} realtime model(s):")
                for model in realtime_models[:3]:  # Show first 3
                    print(f"  • {model['id']}")
                return True, True  # API works, has realtime
            else:
                print("⚠️ No realtime models found in your account")
                return True, False  # API works, no realtime
                
        elif response.status_code == 401:
            print("❌ Invalid API key")
            return False, False
        elif response.status_code == 429:
            print("❌ Rate limited")
            return False, False
        else:
            print(f"❌ API error {response.status_code}: {response.text[:200]}")
            return False, False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False, False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False, False

def test_realtime_api_models():
    """Test if realtime API models are accessible"""
    print("🔍 Testing Realtime API Model Access...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "realtime=v1"  # Required header for realtime
        }
        
        # Try to access realtime-specific endpoint or model
        response = requests.get("https://api.openai.com/v1/models/gpt-4o-realtime-preview-2024-10-01", 
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Realtime API model accessible")
            return True
        elif response.status_code == 401:
            print("❌ Unauthorized - API key may not have realtime access")
            return False
        elif response.status_code == 403:
            print("❌ Forbidden - Realtime API not available for your account/region")
            return False
        elif response.status_code == 404:
            print("⚠️ Model not found - may be deprecated or renamed")
            return False
        else:
            print(f"❌ Error {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Realtime API test failed: {e}")
        return False

def main():
    print("🔍 API Access Test - Regular vs Realtime")
    print("=" * 50)
    
    # Test regular API
    regular_works, has_realtime_models = test_regular_api()
    print()
    
    # Test realtime API specifically  
    realtime_works = test_realtime_api_models()
    print()
    
    print("=" * 50)
    print("📊 FINAL DIAGNOSIS")
    print("=" * 50)
    
    if regular_works and has_realtime_models and realtime_works:
        print("✅ Everything looks good!")
        print("Your API key has access to both regular and Realtime APIs.")
        print("The hanging issue might be a different problem.")
        
    elif regular_works and not has_realtime_models:
        print("⚠️ Partial Access")
        print("Your API key works for regular OpenAI API but doesn't have realtime models.")
        print("You may need to:")
        print("• Upgrade your OpenAI account")
        print("• Request access to Realtime API")
        print("• Check if Realtime API is available in your region")
        
    elif regular_works and not realtime_works:
        print("⚠️ Limited Access") 
        print("Your API key works for regular API but not Realtime API.")
        print("This could be:")
        print("• Regional restrictions")
        print("• Account tier limitations")
        print("• Realtime API requires special access")
        
    elif not regular_works:
        print("❌ API Key Issues")
        print("Your API key doesn't work with the regular OpenAI API.")
        print("Please check:")
        print("• API key is correct")
        print("• Account has sufficient credits")
        print("• API key hasn't been revoked")
        
    else:
        print("❓ Unclear Status")
        print("Mixed results - please review the individual test outputs above.")

if __name__ == "__main__":
    main()
