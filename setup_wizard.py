"""
Interactive setup wizard for JARVIS
Helps users configure API keys and settings
"""

import os
import getpass
import webbrowser
from pathlib import Path

def welcome():
    """Display welcome message"""
    print("🤖 Welcome to JARVIS Setup Wizard!")
    print("="*50)
    print("This wizard will help you configure JARVIS with your API keys.")
    print("")

def setup_openai_api():
    """Help user set up OpenAI API key"""
    print("🔑 OpenAI API Key Setup")
    print("-" * 30)
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key and api_key != "your_openai_api_key_here":
        print("✅ OpenAI API key already configured")
        return api_key
    
    print("You need an OpenAI API key to use JARVIS.")
    print("1. Go to: https://platform.openai.com/api-keys")
    print("2. Create an account or sign in")
    print("3. Create a new API key")
    print("4. Copy the key and paste it below")
    
    open_browser = input("\nOpen OpenAI website in browser? (y/n): ").lower().strip()
    if open_browser == 'y':
        webbrowser.open("https://platform.openai.com/api-keys")
    
    while True:
        api_key = getpass.getpass("\nPaste your OpenAI API key (input hidden): ").strip()
        
        if not api_key:
            print("❌ API key cannot be empty")
            continue
        
        if len(api_key) < 20:
            print("❌ API key seems too short. Please check and try again.")
            continue
        
        if api_key.startswith("sk-"):
            break
        else:
            print("❌ OpenAI API keys typically start with 'sk-'. Please verify.")
            retry = input("Use this key anyway? (y/n): ").lower().strip()
            if retry == 'y':
                break
    
    return api_key

def setup_weather_api():
    """Help user set up weather API key"""
    print("\n🌤️ Weather API Setup (Optional)")
    print("-" * 35)
    
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    if api_key and api_key != "your_openweather_api_key_here":
        print("✅ Weather API key already configured")
        return api_key
    
    setup_weather = input("Set up weather functionality? (y/n): ").lower().strip()
    
    if setup_weather != 'y':
        print("⏭️  Skipping weather setup")
        return ""
    
    print("Weather functionality uses OpenWeatherMap:")
    print("1. Go to: https://openweathermap.org/api")
    print("2. Sign up for a free account")
    print("3. Get your API key")
    
    open_browser = input("\nOpen OpenWeatherMap website? (y/n): ").lower().strip()
    if open_browser == 'y':
        webbrowser.open("https://openweathermap.org/api")
    
    api_key = input("\nEnter your OpenWeatherMap API key (or press Enter to skip): ").strip()
    
    if api_key:
        print("✅ Weather API key configured")
    else:
        print("⏭️  Weather setup skipped")
    
    return api_key

def update_env_file(openai_key: str, weather_key: str = ""):
    """Update the .env file with API keys"""
    print("\n💾 Updating .env file...")
    
    env_content = f"""# OpenAI API Key (Required)
OPENAI_API_KEY={openai_key}

# OpenWeatherMap API Key (Optional - for weather functionality)
OPENWEATHER_API_KEY={weather_key}

# Google API Credentials (Optional - for Gmail/Calendar)
GOOGLE_CREDENTIALS_FILE=credentials.json

# Application Settings
VOICE_MODE=true
DEBUG_MODE=false
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ .env file updated")

def setup_google_apis():
    """Help user set up Google APIs"""
    print("\n📧 Google APIs Setup (Optional)")
    print("-" * 35)
    
    if os.path.exists("credentials.json"):
        print("✅ Google credentials file found")
        return True
    
    setup_google = input("Set up Gmail and Calendar integration? (y/n): ").lower().strip()
    
    if setup_google != 'y':
        print("⏭️  Skipping Google APIs setup")
        return False
    
    print("\nTo enable Gmail and Calendar features:")
    print("1. Go to Google Cloud Console: https://console.cloud.google.com")
    print("2. Create a new project or select existing")
    print("3. Enable Gmail API and Calendar API")
    print("4. Create OAuth 2.0 credentials (Desktop application)")
    print("5. Download the credentials JSON file")
    print("6. Save it as 'credentials.json' in this folder")
    
    open_browser = input("\nOpen Google Cloud Console? (y/n): ").lower().strip()
    if open_browser == 'y':
        webbrowser.open("https://console.cloud.google.com")
    
    input("\nPress Enter when you've downloaded credentials.json...")
    
    if os.path.exists("credentials.json"):
        print("✅ Google credentials file found")
        return True
    else:
        print("⚠️  credentials.json not found. Gmail/Calendar features will be disabled.")
        return False

def final_instructions():
    """Show final instructions"""
    print("\n" + "="*60)
    print("🎉 JARVIS Configuration Complete!")
    print("="*60)
    
    print("\n🚀 Ready to run JARVIS:")
    print("   python main.py")
    
    print("\n🧪 Test your setup:")
    print("   python test.py")
    
    print("\n📚 Need help?")
    print("   - Check README.md for detailed documentation")
    print("   - Review logs in jarvis.log if issues occur")
    
    print("\n💡 Tips:")
    print("   - Start with Text Mode to test tools")
    print("   - Voice Mode requires microphone permissions")
    print("   - Use Test Mode to verify individual tools")

def main():
    """Main setup wizard"""
    welcome()
    
    try:
        # Setup OpenAI API
        openai_key = setup_openai_api()
        
        # Setup Weather API
        weather_key = setup_weather_api()
        
        # Update .env file
        update_env_file(openai_key, weather_key)
        
        # Setup Google APIs
        setup_google_apis()
        
        # Final instructions
        final_instructions()
        
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")

if __name__ == "__main__":
    main()
