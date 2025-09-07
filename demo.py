"""
Demo Script for Email-Calendar Integration
Showcases the intelligent email parsing and calendar creation flow
"""

import asyncio
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

class EmailCalendarDemo:
    """Demo for email-calendar integration features"""
    
    def __init__(self):
        self.agent = None
    
    async def setup(self):
        """Setup the demo environment"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY not configured")
            return False
        
        try:
            from agent import VoiceAgent
            self.agent = VoiceAgent(api_key)
            await self.agent.initialize()
            return True
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    async def demo_email_parsing(self):
        """Demo intelligent email parsing"""
        print("📧 Demo: Intelligent Email Parsing")
        print("-" * 50)
        
        # Simulate parsing different types of emails
        demo_emails = [
            {
                "subject": "Physics Exam - Room 204, Monday 3PM",
                "sender": "professor@university.edu",
                "body": "Reminder: Physics midterm exam on Monday, September 15th at 3:00 PM in Room 204. Please bring your calculator and ID."
            },
            {
                "subject": "Team Meeting Tomorrow",
                "sender": "manager@company.com", 
                "body": "Hi team, we have our weekly standup tomorrow (Tuesday) at 10 AM in the conference room. We'll discuss the Q3 roadmap."
            },
            {
                "subject": "Doctor Appointment Confirmation",
                "sender": "clinic@healthcare.com",
                "body": "Your appointment with Dr. Smith is confirmed for Wednesday, September 17th at 2:30 PM at our downtown location."
            }
        ]
        
        print("🔍 Parsing sample emails for events...")
        
        gmail_tool = self.agent.tool_instances.get("smart_gmail")
        if not gmail_tool:
            print("❌ Gmail tool not available")
            return
        
        for i, email in enumerate(demo_emails, 1):
            print(f"\n📨 Email {i}: {email['subject']}")
            
            # Simulate the parsing (would normally come from actual emails)
            event_info = gmail_tool._parse_email_for_events(email)
            
            if event_info and event_info.get("has_event"):
                print(f"   ✅ Event detected:")
                print(f"      Title: {event_info['title']}")
                print(f"      Date: {event_info.get('date', 'TBD')}")
                print(f"      Time: {event_info.get('time', 'TBD')}")
                print(f"      Type: {event_info['type']}")
                print(f"      Confidence: {event_info['confidence']:.2f}")
                
                # Ask if user wants to add to calendar
                add_to_cal = input(f"   Add '{event_info['title']}' to calendar? (y/n): ").lower()
                
                if add_to_cal == 'y':
                    calendar_tool = self.agent.tool_instances.get("smart_google_calendar")
                    if calendar_tool:
                        result = calendar_tool._run(
                            "create_from_email",
                            event_data=event_info
                        )
                        print(f"   {result}")
                    else:
                        print("   ❌ Calendar tool not available")
                else:
                    print("   ⏭️ Skipped")
            else:
                print("   ➖ No event detected")
    
    async def demo_voice_commands(self):
        """Demo voice commands for email-calendar integration"""
        print("\n🎤 Demo: Voice Commands")
        print("-" * 50)
        
        # Test commands that would work with voice
        test_commands = [
            "Summarize today's emails and look for any meetings or appointments",
            "Check my calendar for tomorrow",
            "Parse my recent emails for any tests or exams I need to remember",
            "What meetings do I have this week?",
            "Add a study session for physics to my calendar tomorrow at 7 PM"
        ]
        
        print("🗣️ Testing email-calendar voice commands:")
        
        for i, command in enumerate(test_commands, 1):
            print(f"\n{i}. Command: {command}")
            
            try:
                response = await self.agent.text_conversation(command)
                print(f"   🤖 Response: {response[:200]}...")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    async def demo_natural_flow(self):
        """Demo the natural conversation flow"""
        print("\n💬 Demo: Natural Conversation Flow")
        print("-" * 50)
        
        print("This demonstrates how a user might naturally interact with JARVIS:")
        
        conversation_flow = [
            "Hello JARVIS, what's on my schedule today?",
            "Can you check my emails for any important meetings or deadlines?",
            "I think I saw an email about a physics test - can you find it and add it to my calendar?",
            "What's the weather like for my commute tomorrow?",
            "Remind me that I need to study for the physics test"
        ]
        
        for i, message in enumerate(conversation_flow, 1):
            print(f"\n👤 User: {message}")
            
            try:
                response = await self.agent.text_conversation(message)
                print(f"🤖 JARVIS: {response}")
                
                # Pause for effect
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def run_full_demo(self):
        """Run the complete demo"""
        print("🎭 JARVIS Email-Calendar Integration Demo")
        print("=" * 60)
        
        if not await self.setup():
            return
        
        try:
            # Run different demo sections
            await self.demo_email_parsing()
            
            input("\nPress Enter to continue to voice commands demo...")
            await self.demo_voice_commands()
            
            input("\nPress Enter to continue to natural flow demo...")
            await self.demo_natural_flow()
            
            print("\n🎉 Demo complete!")
            print("Ready to use JARVIS with voice commands like:")
            print("• 'Summarize my emails and add any events to my calendar'")
            print("• 'What meetings do I have today?'")
            print("• 'Check for any test dates in my recent emails'")
            
        except KeyboardInterrupt:
            print("\n👋 Demo interrupted")
        finally:
            if self.agent:
                await self.agent.cleanup()

async def run_quick_email_demo():
    """Quick demo focusing just on email features"""
    print("📧 Quick Email Demo")
    print("-" * 30)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ API key not configured")
        return
    
    try:
        from agent import VoiceAgent
        
        agent = VoiceAgent(api_key)
        await agent.initialize()
        
        commands = [
            "Summarize my recent emails",
            "Look for any meetings or appointments in my emails",
            "Check my calendar for today"
        ]
        
        for cmd in commands:
            print(f"\n🗣️ {cmd}")
            response = await agent.text_conversation(cmd)
            print(f"🤖 {response[:300]}...")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    finally:
        if 'agent' in locals():
            await agent.cleanup()

def main():
    """Main demo function"""
    print("🎭 JARVIS Email-Calendar Demo")
    print("=" * 40)
    
    print("Choose demo mode:")
    print("1. 🎭 Full Interactive Demo")
    print("2. 📧 Quick Email Demo")
    print("3. 🔧 Component Test")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        demo = EmailCalendarDemo()
        asyncio.run(demo.run_full_demo())
    elif choice == "2":
        asyncio.run(run_quick_email_demo())
    elif choice == "3":
        # Run component tests
        os.system("python test.py")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
