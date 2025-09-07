"""
Minimal API key validation test
"""
import os
from dotenv import load_dotenv

load_dotenv()

def validate_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ No API key found in environment")
        return False
        
    print(f"API key length: {len(api_key)}")
    print(f"API key starts with: {api_key[:7]}...")
    
    # Basic format check
    if not api_key.startswith("sk-"):
        print("❌ API key doesn't start with 'sk-'")
        print("This might be an invalid API key format")
        return False
        
    # Check if it looks like the old format vs new format
    if len(api_key) < 50:
        print("⚠️ API key seems short - might be old format or invalid")
    elif len(api_key) > 200:
        print("⚠️ API key seems very long - might be invalid")
    else:
        print("✅ API key format looks reasonable")
    
    return True

def check_env_file():
    """Check if .env file exists and is readable"""
    if not os.path.exists(".env"):
        print("❌ .env file not found")
        return False
        
    print("✅ .env file exists")
    
    try:
        with open(".env", "r") as f:
            content = f.read()
            if "OPENAI_API_KEY" in content:
                print("✅ OPENAI_API_KEY found in .env file")
                # Check if it's set to placeholder
                lines = content.split('\n')
                for line in lines:
                    if line.startswith("OPENAI_API_KEY"):
                        if "your_openai_api_key_here" in line:
                            print("❌ API key is still set to placeholder")
                            return False
                        break
            else:
                print("❌ OPENAI_API_KEY not found in .env file")
                return False
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False
        
    return True

if __name__ == "__main__":
    print("🔍 API Key Validation Test")
    print("=" * 40)
    
    env_ok = check_env_file()
    key_ok = validate_api_key()
    
    if env_ok and key_ok:
        print("\n✅ API key configuration looks good!")
        print("\nIf you're still having issues, it might be:")
        print("• Network connectivity problems")
        print("• Firewall blocking OpenAI requests")  
        print("• Realtime API not available in your region")
        print("• API key doesn't have access to Realtime API")
    else:
        print("\n❌ API key configuration has issues")
        print("\nPlease:")
        print("1. Make sure you have a valid OpenAI API key")
        print("2. Set it properly in your .env file")
        print("3. Ensure your account has access to the Realtime API")
