"""
Complete Installation Script for JARVIS Voice AI Agent
Handles all setup including Python environment, dependencies, and configuration
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🤖 {title}")
    print("="*60)

def check_system_requirements():
    """Check system requirements"""
    print_header("Checking System Requirements")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required. Current: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]}")
    
    # Check OS
    os_name = platform.system()
    print(f"✅ Operating System: {os_name}")
    
    # Check if pip is available
    try:
        import pip
        print("✅ pip available")
    except ImportError:
        print("❌ pip not available")
        return False
    
    return True

def install_dependencies():
    """Install all required dependencies"""
    print_header("Installing Dependencies")
    
    try:
        # Upgrade pip
        print("📦 Upgrading pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Install basic requirements
        print("📦 Installing core dependencies...")
        basic_packages = [
            "openai>=1.40.0",
            "langchain>=0.2.0", 
            "langchain-openai>=0.1.0",
            "langchain-community>=0.2.0",
            "requests>=2.31.0",
            "python-dotenv>=1.0.0",
            "python-dateutil>=2.8.0",
            "pytz>=2023.3"
        ]
        
        for package in basic_packages:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                              check=True, capture_output=True)
                print(f"   ✅ {package.split('>=')[0]}")
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️ Failed to install {package}: {e}")
        
        # Install audio dependencies (may fail on some systems)
        print("\n📦 Installing audio dependencies...")
        audio_packages = ["pyaudio>=0.2.11", "websockets>=12.0", "numpy>=1.24.0"]
        
        for package in audio_packages:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                              check=True, capture_output=True)
                print(f"   ✅ {package.split('>=')[0]}")
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️ {package.split('>=')[0]} failed - voice mode may not work")
        
        # Install Google API dependencies (optional)
        print("\n📦 Installing Google API dependencies...")
        google_packages = [
            "google-auth",
            "google-auth-oauthlib", 
            "google-auth-httplib2",
            "google-api-python-client"
        ]
        
        for package in google_packages:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                              check=True, capture_output=True)
                print(f"   ✅ {package}")
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️ {package} failed - Gmail/Calendar may not work")
        
        # Install memory/vector dependencies
        print("\n📦 Installing memory dependencies...")
        memory_packages = ["chromadb>=0.4.0", "tiktoken>=0.5.0"]
        
        for package in memory_packages:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                              check=True, capture_output=True)
                print(f"   ✅ {package.split('>=')[0]}")
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️ {package.split('>=')[0]} failed - advanced memory may not work")
        
        print("\n✅ Dependency installation complete!")
        return True
        
    except Exception as e:
        print(f"❌ Dependency installation failed: {e}")
        return False

def create_configuration():
    """Create initial configuration files"""
    print_header("Creating Configuration")
    
    # Create .env file
    if not os.path.exists(".env"):
        env_content = """# OpenAI API Key (Required)
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# OpenWeatherMap API Key (Optional)
# Get from: https://openweathermap.org/api
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Google API Credentials (Optional)
GOOGLE_CREDENTIALS_FILE=credentials.json

# Application Settings
VOICE_MODE=true
DEBUG_MODE=false

# Audio Settings
SAMPLE_RATE=24000
CHANNELS=1
CHUNK_SIZE=1024

# Agent Settings
MAX_ITERATIONS=3
TEMPERATURE=0.7
"""
        
        with open(".env", "w") as f:
            f.write(env_content)
        
        print("✅ Created .env file")
    else:
        print("✅ .env file already exists")
    
    # Create directories
    directories = ["logs", "data", "temp"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created {directory}/ directory")
    
    return True

def test_audio_system():
    """Test if audio system is working"""
    print_header("Testing Audio System")
    
    try:
        import pyaudio
        
        print("🎵 Initializing audio system...")
        audio = pyaudio.PyAudio()
        
        # List audio devices
        print("\n🎤 Available audio devices:")
        input_devices = []
        output_devices = []
        
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            
            if device_info['maxInputChannels'] > 0:
                input_devices.append(device_info['name'])
                print(f"   🎤 Input: {device_info['name']}")
            
            if device_info['maxOutputChannels'] > 0:
                output_devices.append(device_info['name'])
                print(f"   🔊 Output: {device_info['name']}")
        
        audio.terminate()
        
        if input_devices and output_devices:
            print(f"\n✅ Audio system ready ({len(input_devices)} input, {len(output_devices)} output devices)")
            return True
        else:
            print("\n⚠️ No audio devices detected. Voice mode may not work.")
            return False
            
    except ImportError:
        print("❌ PyAudio not installed. Voice mode will not work.")
        print("Install manually: pip install pyaudio")
        return False
    except Exception as e:
        print(f"⚠️ Audio system test failed: {e}")
        return False

def run_initial_test():
    """Run a basic test to verify installation"""
    print_header("Running Initial Test")
    
    try:
        # Test imports
        print("🧪 Testing imports...")
        
        test_imports = [
            ("OpenAI", "openai"),
            ("LangChain", "langchain"),
            ("Requests", "requests"),
            ("Python-dotenv", "dotenv"),
            ("Pytz", "pytz")
        ]
        
        for name, module in test_imports:
            try:
                __import__(module)
                print(f"   ✅ {name}")
            except ImportError:
                print(f"   ❌ {name} - install failed")
        
        # Test basic functionality
        print("\n🧪 Testing basic tools...")
        
        # Import and test a simple tool
        sys.path.append(os.getcwd())
        from tools import TimeTool, PythonREPLTool
        
        # Test time tool
        time_tool = TimeTool()
        time_result = time_tool._run()
        print(f"   ✅ Time Tool: {time_result[:50]}...")
        
        # Test Python REPL
        python_tool = PythonREPLTool()
        python_result = python_tool._run("print('Installation test successful!')")
        print(f"   ✅ Python REPL: {python_result}")
        
        print("\n✅ Initial test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Initial test failed: {e}")
        return False

def show_next_steps():
    """Show next steps after installation"""
    print_header("Next Steps")
    
    print("🎯 To complete JARVIS setup:")
    print()
    print("1️⃣ Configure OpenAI API:")
    print("   • Get API key: https://platform.openai.com/api-keys")
    print("   • Edit .env file and set OPENAI_API_KEY")
    print()
    print("2️⃣ Optional - Weather API:")
    print("   • Get free key: https://openweathermap.org/api")
    print("   • Set OPENWEATHER_API_KEY in .env")
    print()
    print("3️⃣ Optional - Google APIs (Gmail/Calendar):")
    print("   • Run: python google_oauth_setup.py")
    print("   • Follow the OAuth setup wizard")
    print()
    print("4️⃣ Test your setup:")
    print("   • Run: python test.py")
    print("   • Or: python realtime_test.py")
    print()
    print("5️⃣ Start JARVIS:")
    print("   • Run: python main.py")
    print()
    print("📚 Documentation:")
    print("   • See README.md for detailed instructions")
    print("   • Check logs/ directory if issues occur")

def main():
    """Main installation function"""
    print_header("JARVIS Voice AI Agent - Complete Installation")
    
    success = True
    
    # Check system requirements
    if not check_system_requirements():
        success = False
        print("\n❌ System requirements not met")
        return
    
    # Install dependencies
    if not install_dependencies():
        success = False
        print("\n⚠️ Some dependencies failed to install")
    
    # Create configuration
    if not create_configuration():
        success = False
    
    # Test audio system
    audio_works = test_audio_system()
    
    # Run initial test
    if not run_initial_test():
        success = False
    
    # Show results
    if success:
        print_header("Installation Complete! 🎉")
        print("✅ JARVIS is ready for configuration")
        
        if audio_works:
            print("🎤 Voice mode will be available once configured")
        else:
            print("💬 Text mode ready (voice mode may have issues)")
        
        show_next_steps()
    else:
        print_header("Installation Issues Detected ⚠️")
        print("Some components failed to install properly.")
        print("You can still use JARVIS in text mode with working components.")
        print("Check the error messages above for troubleshooting.")

if __name__ == "__main__":
    main()
