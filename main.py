"""
Main entry point for JARVIS Voice AI Agent
Simplified launcher focusing on core voice functionality
"""

import asyncio
import os
import sys
import signal
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global agent instance for graceful shutdown
global_agent = None
shutdown_event = asyncio.Event()

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\n🛑 Received signal {signum}. Initiating graceful shutdown...")
    shutdown_event.set()

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    try:
        # Handle Ctrl+C (SIGINT) and termination (SIGTERM)
        signal.signal(signal.SIGINT, signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)
        logger.info("Signal handlers registered")
    except Exception as e:
        logger.warning(f"Could not setup signal handlers: {e}")

async def graceful_shutdown(timeout: float = 5.0):
    """Perform graceful shutdown of the agent with timeout"""
    global global_agent
    
    print("\n🔄 Shutting down JARVIS...")
    
    try:
        if global_agent:
            print("🛑 Cleaning up agent resources...")
            
            # Perform cleanup with timeout
            try:
                await asyncio.wait_for(global_agent.cleanup(), timeout=timeout)
                print("✅ Agent cleanup complete")
            except asyncio.TimeoutError:
                print(f"⚠️  Agent cleanup timed out after {timeout}s - forcing shutdown")
            except Exception as e:
                logger.error(f"Agent cleanup error: {e}")
                print(f"⚠️  Agent cleanup error: {e}")
        else:
            print("ℹ️  No agent to cleanup")
            
        # Give a moment for any final operations
        await asyncio.sleep(0.3)
        
        print("👋 JARVIS shutdown complete. Goodbye!")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
        print(f"⚠️  Warning: Shutdown error: {e}")
    
    finally:
        # Ensure we exit
        logger.info("Shutdown process completed")

async def main():
    """Main entry point - starts voice mode directly"""
    global global_agent
    
    # Setup signal handlers
    setup_signal_handlers()
    
    print("🤖 JARVIS Voice AI Agent")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ OpenAI API key not configured")
        print("Please set OPENAI_API_KEY in your .env file")
        return
    
    print("✅ API key found")
    
    try:
        # Import and initialize agent
        print("🔄 Initializing JARVIS...")
        from agent import VoiceAgent
        
        agent = VoiceAgent(openai_api_key=api_key)
        global_agent = agent  # Store for cleanup
        
        await agent.initialize()
        print("✅ JARVIS initialized successfully")
        
        # Check realtime client
        if not agent.realtime_client or not agent.realtime_client.is_connected:
            print("❌ Voice mode not available. Falling back to text mode...")
            
            # Create shutdown monitoring task for text mode
            shutdown_task = asyncio.create_task(monitor_shutdown())
            text_task = asyncio.create_task(agent.interactive_text_mode())
            
            # Wait for either text mode to finish or shutdown signal
            done, pending = await asyncio.wait(
                [text_task, shutdown_task], 
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel remaining tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            return
        
        print("✅ Voice mode ready")
        print("\n🎤 Starting voice conversation...")
        print("🗣️ Try saying:")
        print("   • 'Hello JARVIS, what time is it?'")
        print("   • 'Get weather for London'")
        print("   • 'Read my recent emails'")
        print("   • 'Create a meeting for tomorrow at 2 PM'")
        print("\nPress Ctrl+C to stop")
        
        # Create shutdown monitoring task
        shutdown_task = asyncio.create_task(monitor_shutdown())
        voice_task = asyncio.create_task(agent.start_voice_conversation())
        
        # Wait for either voice conversation to finish or shutdown signal
        done, pending = await asyncio.wait(
            [voice_task, shutdown_task], 
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel remaining tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
    except KeyboardInterrupt:
        print("\n� Keyboard interrupt received")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Some dependencies might be missing.")
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
    finally:
        # Always perform graceful shutdown
        await graceful_shutdown()

async def monitor_shutdown():
    """Monitor for shutdown signals"""
    await shutdown_event.wait()
    logger.info("Shutdown event received")

def create_env_file():
    """Create a sample .env file if it doesn't exist"""
    env_file_path = ".env"
    
    if not os.path.exists(env_file_path):
        env_content = """# OpenAI API Key (Required)
OPENAI_API_KEY=your_openai_api_key_here

# OpenWeatherMap API Key (Optional - for weather functionality)  
OPENWEATHER_API_KEY=your_openweather_api_key_here
"""
        
        with open(env_file_path, 'w') as f:
            f.write(env_content)
        
        print(f"📝 Created sample {env_file_path} file. Please update with your API keys.")
        return False
    
    return True

if __name__ == "__main__":
    # Create .env file if needed
    if not create_env_file():
        print("Please update the .env file with your API keys and run again.")
        sys.exit(1)
    
    # Run the application with proper cleanup
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"💥 Fatal error: {e}")
        sys.exit(1)
    finally:
        print("🔚 Application terminated")
