"""
Main orchestration script for JARVIS Voice AI Agent
Handles initialization, configuration, and main execution loop
"""

import asyncio
import os
import datetime
import logging
from typing import Optional
from dotenv import load_dotenv

from agent import VoiceAgent
from realtime_client import RealtimeClient

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JARVISApp:
    """
    Main application class for JARVIS Voice AI Agent
    """
    
    def __init__(self):
        self.agent: Optional[VoiceAgent] = None
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from environment variables"""
        config = {
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "openweather_api_key": os.getenv("OPENWEATHER_API_KEY"),
            "google_credentials_file": os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json"),
            "voice_mode": os.getenv("VOICE_MODE", "true").lower() == "true",
            "debug_mode": os.getenv("DEBUG_MODE", "false").lower() == "true"
        }
        
        return config
    
    def _validate_config(self) -> bool:
        """Validate required configuration"""
        missing_keys = []
        
        if not self.config["openai_api_key"]:
            missing_keys.append("OPENAI_API_KEY")
        
        if missing_keys:
            print("❌ Missing required environment variables:")
            for key in missing_keys:
                print(f"   - {key}")
            print("\nPlease create a .env file with the required variables.")
            return False
        
        # Warn about optional keys
        if not self.config["openweather_api_key"]:
            print("⚠️  OPENWEATHER_API_KEY not set. Weather functionality will be limited.")
        
        return True
    
    async def initialize(self) -> bool:
        """Initialize the application"""
        try:
            print("🚀 Initializing JARVIS...")
            
            # Validate configuration
            if not self._validate_config():
                return False
            
            # Create and initialize agent
            self.agent = VoiceAgent(self.config["openai_api_key"])
            await self.agent.initialize()
            
            print("✅ JARVIS initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            print(f"❌ Initialization failed: {e}")
            return False
    
    async def run(self):
        """Run the main application loop"""
        if not await self.initialize():
            return
        
        try:
            # Show welcome message
            self._show_welcome()
            
            # Choose mode
            mode = await self._choose_mode()
            
            if mode == "voice":
                await self._run_voice_mode()
            elif mode == "text":
                await self._run_text_mode()
            elif mode == "email":
                await self._run_email_mode()
            elif mode == "test":
                await self._run_test_mode()
            elif mode == "exit":
                return
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        except Exception as e:
            logger.error(f"Runtime error: {e}")
            print(f"❌ Error: {e}")
        finally:
            await self._cleanup()
    
    def _show_welcome(self):
        """Display welcome message"""
        print("\n" + "="*60)
        print("🤖 Welcome to JARVIS - Your Voice AI Assistant")
        print("="*60)
        print("\n🎯 Available capabilities:")
        print("   📧 Gmail - Read and send emails")
        print("   📅 Calendar - Manage your schedule")
        print("   🐍 Python - Execute code snippets")
        print("   🌤️  Weather - Get weather information")
        print("   🕐 Time - Check time in any timezone")
        print("   🧠 Memory - Remember conversation context")
        print("")
    
    async def _choose_mode(self) -> str:
        """Let user choose interaction mode"""
        print("Choose interaction mode:")
        print("1. 🎤 Voice Mode (Real-time audio with OpenAI)")
        print("2. 💬 Text Mode (Terminal chat)")
        print("3. 🧪 Test Mode (Test individual tools)")
        print("4. 📧 Email Mode (Parse emails and manage calendar)")
        
        while True:
            try:
                choice = input("\nEnter choice (1/2/3/4): ").strip()
                
                if choice == "1":
                    return "voice"
                elif choice == "2":
                    return "text"
                elif choice == "3":
                    return "test"
                elif choice == "4":
                    return "email"
                else:
                    print("Please enter 1, 2, 3, or 4")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                return "exit"
    
    async def _run_voice_mode(self):
        """Run in voice interaction mode"""
        print("\n🎤 Starting Voice Mode...")
        
        if not self.agent.realtime_client:
            print("❌ Voice mode not available. Realtime client not initialized.")
            print("Falling back to text mode...")
            await self._run_text_mode()
            return
        
        if not self.agent.realtime_client.is_connected:
            print("❌ Voice mode not available. Not connected to Realtime API.")
            print("Check your OpenAI API key and internet connection.")
            print("Falling back to text mode...")
            await self._run_text_mode()
            return
        
        print("🔴 Voice mode active!")
        print("🗣️ Try saying:")
        print("   • 'What time is it?'")
        print("   • 'Summarize today's emails'")
        print("   • 'Get weather for New York'")
        print("   • 'Execute Python code to calculate 25 times 4'")
        print("   • 'Add a meeting to my calendar'")
        
        await self.agent.start_voice_conversation()
    
    async def _run_text_mode(self):
        """Run in text interaction mode"""
        print("\n💬 Starting Text Mode...")
        await self.agent.interactive_text_mode()
    
    async def _run_email_mode(self):
        """Run email parsing and calendar management mode"""
        print("\n📧 Starting Email-Calendar Mode...")
        
        if not self.agent.email_calendar:
            print("❌ Email-Calendar integration not available")
            return
        
        print("📋 Email-Calendar Management")
        print("-" * 40)
        print("Commands:")
        print("• 'summary' - Get email summary")
        print("• 'parse' - Parse emails for events")
        print("• 'calendar' - View today's calendar")
        print("• 'quit' - Return to main menu")
        
        while True:
            try:
                command = input("\nEmail-Calendar> ").strip().lower()
                
                if command in ['quit', 'exit', 'back']:
                    break
                elif command == 'summary':
                    result = await self.agent.email_calendar.summarize_and_suggest_events()
                    print(f"\n📧 {result}")
                elif command == 'parse':
                    result = await self.agent.email_calendar.summarize_and_suggest_events(days_back=14)
                    print(f"\n🔍 {result}")
                elif command == 'calendar':
                    today = datetime.datetime.now().strftime("%Y-%m-%d")
                    calendar_tool = self.agent.tool_instances.get("smart_google_calendar")
                    if calendar_tool:
                        result = calendar_tool._run("read", date=today)
                        print(f"\n📅 {result}")
                    else:
                        print("❌ Calendar tool not available")
                elif command == 'help':
                    print("Available commands: summary, parse, calendar, quit")
                else:
                    # Try as natural language command
                    result = await self.agent.email_calendar.handle_voice_command(command)
                    print(f"\n🤖 {result}")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def _run_test_mode(self):
        """Run tool testing mode"""
        print("\n🧪 Testing Tools...")
        
        from agent import test_tools
        await test_tools()
        
        # Additional interactive testing
        print("\nInteractive tool testing:")
        print("Available tools: gmail, google_calendar, python_repl, get_weather, get_time, memory")
        
        while True:
            try:
                tool_name = input("\nEnter tool name to test (or 'back' to return): ").strip()
                
                if tool_name.lower() in ['back', 'exit']:
                    break
                
                if tool_name in self.agent.tool_instances:
                    await self._test_individual_tool(tool_name)
                else:
                    print(f"Unknown tool: {tool_name}")
                    
            except KeyboardInterrupt:
                break
    
    async def _test_individual_tool(self, tool_name: str):
        """Test an individual tool interactively"""
        tool = self.agent.tool_instances[tool_name]
        
        print(f"\n🔧 Testing {tool_name}:")
        print(f"Description: {tool.description}")
        
        if tool_name == "python_repl":
            code = input("Enter Python code: ")
            result = tool._run(code)
            print(f"Result: {result}")
            
        elif tool_name == "get_weather":
            location = input("Enter location: ")
            result = tool._run(location)
            print(f"Result: {result}")
            
        elif tool_name == "get_time":
            timezone = input("Enter timezone (or press Enter for local): ").strip() or "local"
            result = tool._run(timezone)
            print(f"Result: {result}")
            
        elif tool_name == "memory":
            action = input("Enter action (store/retrieve/search/list): ")
            if action == "store":
                key = input("Enter key: ")
                value = input("Enter value: ")
                result = tool._run(action, key, value)
            elif action == "retrieve":
                key = input("Enter key: ")
                result = tool._run(action, key)
            elif action == "search":
                query = input("Enter search query: ")
                result = tool._run(action, query=query)
            else:
                result = tool._run(action)
            print(f"Result: {result}")
            
        else:
            # For Gmail and Calendar, just show stub message
            print("Tool testing not fully implemented yet - requires OAuth setup.")
    
    async def _cleanup(self):
        """Clean up application resources"""
        if self.agent:
            await self.agent.cleanup()
        logger.info("Application cleanup complete")

def create_env_file():
    """Create a sample .env file if it doesn't exist"""
    env_file_path = ".env"
    
    if not os.path.exists(env_file_path):
        env_content = """# OpenAI API Key (Required)
OPENAI_API_KEY=your_openai_api_key_here

# OpenWeatherMap API Key (Optional - for weather functionality)
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Google API Credentials (Optional - for Gmail/Calendar)
GOOGLE_CREDENTIALS_FILE=credentials.json

# Application Settings
VOICE_MODE=true
DEBUG_MODE=false
"""
        
        with open(env_file_path, 'w') as f:
            f.write(env_content)
        
        print(f"📝 Created sample {env_file_path} file. Please update with your API keys.")
        return False
    
    return True

async def main():
    """Main entry point"""
    print("🤖 Starting JARVIS Voice AI Agent...")
    
    # Create .env file if needed
    if not create_env_file():
        print("Please update the .env file with your API keys and run again.")
        return
    
    # Create and run the application
    app = JARVISApp()
    await app.run()

if __name__ == "__main__":
    asyncio.run(main())
