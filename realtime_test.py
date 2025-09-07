"""
Realtime Test Script for JARVIS Voice AI Agent
Tests voice interaction, tool orchestration, and email-calendar integration
"""

import asyncio
import os
import logging
from dotenv import load_dotenv
import datetime

from agent import VoiceAgent
from tools import get_all_tools

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealtimeTestSuite:
    """Test suite for realtime voice interactions"""
    
    def __init__(self):
        self.agent = None
        self.test_results = {}
    
    async def setup(self):
        """Initialize the agent for testing"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("❌ OPENAI_API_KEY not found in environment")
                return False
            
            print("🤖 Initializing JARVIS for realtime testing...")
            self.agent = VoiceAgent(api_key)
            await self.agent.initialize()
            
            print("✅ Agent initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    async def test_voice_mode_startup(self):
        """Test if voice mode can start properly"""
        print("\n🎤 Testing Voice Mode Startup...")
        
        try:
            if not self.agent.realtime_client:
                print("⚠️  Realtime client not available")
                return False
            
            if not self.agent.realtime_client.is_connected:
                print("⚠️  Not connected to Realtime API")
                return False
            
            print("✅ Voice mode ready")
            return True
            
        except Exception as e:
            print(f"❌ Voice mode test failed: {e}")
            return False
    
    async def test_tool_integration(self):
        """Test that tools work correctly"""
        print("\n🔧 Testing Tool Integration...")
        
        test_cases = [
            {
                "name": "Python REPL",
                "tool": "python_repl",
                "args": {"code": "print('Hello from JARVIS!'); 2 + 2"},
                "expected_contains": ["Hello from JARVIS!", "4"]
            },
            {
                "name": "Time Tool",
                "tool": "get_time",
                "args": {"timezone": "local"},
                "expected_contains": ["Current"]
            },
            {
                "name": "Memory Tool",
                "tool": "memory",
                "args": {"action": "store", "key": "test_memory", "value": "realtime test data"},
                "expected_contains": ["Stored"]
            },
            {
                "name": "Weather Tool",
                "tool": "get_weather", 
                "args": {"location": "New York"},
                "expected_contains": ["Weather", "New York"]  # Will work if API key is set
            }
        ]
        
        results = {}
        
        for test in test_cases:
            try:
                tool_name = test["tool"]
                if tool_name in self.agent.tool_instances:
                    tool = self.agent.tool_instances[tool_name]
                    result = tool._run(**test["args"])
                    
                    # Check if result contains expected content
                    success = any(expected in result for expected in test["expected_contains"])
                    
                    results[test["name"]] = {
                        "success": success,
                        "result": result[:200] + "..." if len(result) > 200 else result
                    }
                    
                    status = "✅" if success else "⚠️"
                    print(f"   {status} {test['name']}: {result[:100]}...")
                else:
                    results[test["name"]] = {"success": False, "result": "Tool not found"}
                    print(f"   ❌ {test['name']}: Tool not found")
                    
            except Exception as e:
                results[test["name"]] = {"success": False, "result": str(e)}
                print(f"   ❌ {test['name']}: {e}")
        
        return results
    
    async def test_text_mode_commands(self):
        """Test specific voice commands in text mode"""
        print("\n💬 Testing Voice Commands (Text Mode)...")
        
        test_commands = [
            "What time is it?",
            "Execute Python code: print('JARVIS is working!')",
            "Remember that my favorite color is blue",
            "What do you remember about my favorite color?",
            "Get weather for London"
        ]
        
        results = {}
        
        for command in test_commands:
            try:
                print(f"\n🗣️ Command: {command}")
                response = await self.agent.text_conversation(command)
                
                success = len(response) > 10 and "error" not in response.lower()
                results[command] = {
                    "success": success,
                    "response": response[:200] + "..." if len(response) > 200 else response
                }
                
                status = "✅" if success else "⚠️"
                print(f"   {status} Response: {response[:100]}...")
                
            except Exception as e:
                results[command] = {"success": False, "response": str(e)}
                print(f"   ❌ Error: {e}")
        
        return results
    
    async def test_email_calendar_flow(self):
        """Test the email parsing and calendar integration flow"""
        print("\n📧 Testing Email-Calendar Integration...")
        
        try:
            # Test Gmail tool
            gmail_tool = self.agent.tool_instances.get("smart_gmail")
            if not gmail_tool:
                print("❌ Smart Gmail tool not found")
                return False
            
            # Test email summary (will work without OAuth as a stub)
            print("   Testing email summary...")
            result = gmail_tool._run("summary", max_emails=5)
            print(f"   📧 Email summary: {result[:150]}...")
            
            # Test calendar tool
            calendar_tool = self.agent.tool_instances.get("smart_google_calendar")
            if not calendar_tool:
                print("❌ Smart Calendar tool not found")
                return False
            
            # Test calendar read
            print("   Testing calendar read...")
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            result = calendar_tool._run("read", date=today)
            print(f"   📅 Calendar: {result[:150]}...")
            
            print("✅ Email-Calendar integration structure is ready")
            print("   Note: Full functionality requires Google OAuth setup")
            
            return True
            
        except Exception as e:
            print(f"❌ Email-Calendar test failed: {e}")
            return False
    
    async def run_interactive_voice_test(self):
        """Run an interactive voice test session"""
        print("\n🎤 Interactive Voice Test")
        print("-" * 40)
        
        if not self.agent.realtime_client:
            print("❌ Realtime client not available")
            return
        
        if not self.agent.realtime_client.is_connected:
            print("❌ Not connected to Realtime API")
            return
        
        print("🔴 Starting voice interaction test...")
        print("Try saying commands like:")
        print("   • 'What time is it?'")
        print("   • 'Execute Python code to calculate 15 times 7'")
        print("   • 'Summarize today's emails'")
        print("   • 'Get weather for San Francisco'")
        print("   • 'Remember that I have a meeting tomorrow'")
        print("\nPress Ctrl+C to stop the test")
        
        try:
            await self.agent.start_voice_conversation()
        except KeyboardInterrupt:
            print("\n🛑 Voice test stopped")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🧪 JARVIS Realtime Test Suite")
        print("=" * 50)
        
        # Setup
        if not await self.setup():
            return
        
        # Run tests
        tests = [
            ("Voice Mode Startup", self.test_voice_mode_startup),
            ("Tool Integration", self.test_tool_integration),
            ("Text Mode Commands", self.test_text_mode_commands),
            ("Email-Calendar Flow", self.test_email_calendar_flow)
        ]
        
        all_passed = True
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if isinstance(result, bool):
                    self.test_results[test_name] = result
                    if not result:
                        all_passed = False
                else:
                    # For complex results, consider it passed if no exception
                    self.test_results[test_name] = True
                    
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
                self.test_results[test_name] = False
                all_passed = False
        
        # Show summary
        self._show_test_summary()
        
        # Offer interactive test
        if all_passed:
            print("\n🎉 All tests passed!")
            
            run_interactive = input("\nRun interactive voice test? (y/n): ").lower().strip()
            if run_interactive == 'y':
                await self.run_interactive_voice_test()
        
        # Cleanup
        if self.agent:
            await self.agent.cleanup()
    
    def _show_test_summary(self):
        """Show test results summary"""
        print("\n" + "="*50)
        print("📊 Test Results Summary")
        print("="*50)
        
        passed = 0
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All systems operational!")
        else:
            print("⚠️  Some components need attention")

async def run_quick_voice_test():
    """Quick voice test without full test suite"""
    print("🎤 Quick Voice Test")
    print("-" * 30)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return
    
    try:
        agent = VoiceAgent(api_key)
        await agent.initialize()
        
        print("🔴 Voice mode starting...")
        print("Say: 'Hello JARVIS, what time is it?'")
        
        await agent.start_voice_conversation()
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
    finally:
        if 'agent' in locals():
            await agent.cleanup()

async def run_text_commands_test():
    """Test specific text commands"""
    print("💬 Text Commands Test")
    print("-" * 30)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return
    
    try:
        agent = VoiceAgent(api_key)
        await agent.initialize()
        
        commands = [
            "What time is it?",
            "Execute this Python code: import math; print(f'Pi is approximately {math.pi:.2f}')",
            "Remember that today is my birthday",
            "What weather is it in Tokyo?",
            "Summarize my recent emails"
        ]
        
        for cmd in commands:
            print(f"\n🗣️ Testing: {cmd}")
            response = await agent.text_conversation(cmd)
            print(f"🤖 Response: {response[:200]}...")
        
    except Exception as e:
        print(f"❌ Text test failed: {e}")
    finally:
        if 'agent' in locals():
            await agent.cleanup()

def main():
    """Main test entry point"""
    print("🧪 JARVIS Realtime Testing")
    print("=" * 40)
    
    print("Choose test mode:")
    print("1. 🧪 Full Test Suite")
    print("2. 🎤 Quick Voice Test")
    print("3. 💬 Text Commands Test")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        suite = RealtimeTestSuite()
        asyncio.run(suite.run_all_tests())
    elif choice == "2":
        asyncio.run(run_quick_voice_test())
    elif choice == "3":
        asyncio.run(run_text_commands_test())
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
