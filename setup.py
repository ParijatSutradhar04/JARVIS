"""
Setup script for JARVIS Voice AI Agent
Handles dependency installation, configuration, and initial setup
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def create_virtual_environment():
    """Create a virtual environment if it doesn't exist"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    try:
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    try:
        print("📦 Installing dependencies...")
        
        # Use the virtual environment's pip if available
        pip_cmd = [sys.executable, "-m", "pip"]
        
        # Upgrade pip first
        subprocess.run(pip_cmd + ["install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run(pip_cmd + ["install", "-r", "requirements.txt"], check=True)
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("Try running manually: pip install -r requirements.txt")
        return False

def create_config_files():
    """Create configuration files"""
    # Create .env file from example
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file from example")
        else:
            print("⚠️  .env.example not found")
    else:
        print("✅ .env file already exists")
    
    # Create directories for logs and data
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    print("✅ Configuration directories created")

def check_audio_setup():
    """Check if audio system is working"""
    try:
        import pyaudio
        
        # Test PyAudio initialization
        audio = pyaudio.PyAudio()
        
        # Check for input devices
        input_devices = []
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                input_devices.append(device_info['name'])
        
        # Check for output devices
        output_devices = []
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            if device_info['maxOutputChannels'] > 0:
                output_devices.append(device_info['name'])
        
        audio.terminate()
        
        if input_devices and output_devices:
            print("✅ Audio system detected")
            print(f"   Input devices: {len(input_devices)}")
            print(f"   Output devices: {len(output_devices)}")
        else:
            print("⚠️  Audio devices not detected. Voice mode may not work.")
        
        return True
        
    except ImportError:
        print("❌ PyAudio not installed. Voice mode will not work.")
        print("Install with: pip install pyaudio")
        return False
    except Exception as e:
        print(f"⚠️  Audio setup issue: {e}")
        return False

def print_next_steps():
    """Print instructions for next steps"""
    print("\n" + "="*60)
    print("🎉 JARVIS Setup Complete!")
    print("="*60)
    
    print("\n📝 Next Steps:")
    print("1. Update .env file with your API keys:")
    print("   - OPENAI_API_KEY (required)")
    print("   - OPENWEATHER_API_KEY (optional)")
    
    print("\n2. For Google integration (Gmail/Calendar):")
    print("   - Go to Google Cloud Console")
    print("   - Enable Gmail and Calendar APIs")
    print("   - Create OAuth2 credentials")
    print("   - Download as credentials.json")
    
    print("\n3. Run JARVIS:")
    print("   python main.py")
    
    print("\n🔧 Test Mode:")
    print("   Run 'python main.py' and choose Test Mode to verify tools")
    
    print("\n📚 Documentation:")
    print("   See README.md for detailed setup instructions")

def main():
    """Main setup function"""
    print("🤖 JARVIS Voice AI Agent Setup")
    print("="*40)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Create virtual environment (optional)
    create_virtual_environment()
    
    # Install dependencies
    if not install_dependencies():
        success = False
    
    # Create config files
    create_config_files()
    
    # Check audio setup
    check_audio_setup()
    
    if success:
        print_next_steps()
    else:
        print("\n❌ Setup completed with some issues. Please resolve them before running JARVIS.")

if __name__ == "__main__":
    main()
