"""
Debug script to find exactly where the voice agent import hangs
"""
import sys
import time
import os

def debug_import(module_name):
    """Debug import with timing"""
    print(f"🔄 Importing {module_name}...", end="", flush=True)
    start_time = time.time()
    try:
        if module_name == "agent":
            from agent import VoiceAgent
        elif module_name == "tools":
            import tools
        elif module_name == "realtime_client":
            from realtime_client import RealtimeClient
        elif module_name == "email_calendar_integration":
            from email_calendar_integration import EmailCalendarIntegration
        elif module_name == "openai":
            from openai import AsyncOpenAI
        elif module_name == "langchain":
            from langchain.agents import AgentExecutor
        
        elapsed = time.time() - start_time
        print(f" ✅ ({elapsed:.2f}s)")
        return True
    except Exception as e:
        elapsed = time.time() - start_time
        print(f" ❌ ({elapsed:.2f}s) - Error: {e}")
        return False

def main():
    print("🕵️ Debugging Voice Agent Import Chain")
    print("=" * 50)
    
    # Test individual imports in order
    imports_to_test = [
        "openai",
        "langchain", 
        "tools",
        "realtime_client",
        "email_calendar_integration",
        "agent"
    ]
    
    for module in imports_to_test:
        success = debug_import(module)
        if not success:
            print(f"❌ Failed at: {module}")
            return
        time.sleep(0.1)  # Small delay between imports
    
    print("\n✅ All imports successful!")
    
    # Now test actual VoiceAgent initialization
    print("\n🔄 Testing VoiceAgent initialization...")
    try:
        from agent import VoiceAgent
        agent = VoiceAgent(openai_api_key=os.getenv("OPENAI_API_KEY"))
        print("✅ VoiceAgent created successfully!")
    except Exception as e:
        print(f"❌ VoiceAgent creation failed: {e}")

if __name__ == "__main__":
    main()
