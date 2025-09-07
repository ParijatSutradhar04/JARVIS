"""
Simple Realtime Voice Test - Direct OpenAI Connection
Tests basic voice conversation without tools or complex setup
"""

import asyncio
import os
import json
import base64
import websockets
import pyaudio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleVoiceTest:
    """Simple voice test with OpenAI Realtime API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.websocket = None
        self.is_connected = False
        
        # Audio setup
        self.sample_rate = 24000
        self.chunk_size = 1024
        self.audio = None
        self.input_stream = None
        self.output_stream = None
        
    async def connect(self):
        """Connect to OpenAI Realtime API"""
        try:
            url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            print("🔌 Connecting to OpenAI Realtime API...")
            self.websocket = await websockets.connect(
                url, 
                additional_headers=headers,
                ping_interval=20,
                ping_timeout=10
            )
            self.is_connected = True
            print("✅ Connected successfully!")
            
            # Send session configuration
            await self.configure_session()
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def configure_session(self):
        """Configure the session parameters"""
        config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "voice": "alloy",
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 200
                }
            }
        }
        
        await self.websocket.send(json.dumps(config))
        print("📡 Session configured for voice interaction")
    
    def setup_audio(self):
        """Initialize PyAudio for recording and playback"""
        try:
            self.audio = pyaudio.PyAudio()
            
            # Input stream (microphone)
            self.input_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            # Output stream (speakers)
            self.output_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size
            )
            
            print("🎤 Audio system initialized")
            return True
            
        except Exception as e:
            print(f"❌ Audio setup failed: {e}")
            return False
    
    async def listen_for_messages(self):
        """Listen for messages from OpenAI"""
        try:
            while self.is_connected and self.websocket:
                message = await self.websocket.recv()
                data = json.loads(message)
                
                message_type = data.get("type", "")
                
                if message_type == "session.created":
                    print("🎉 Session created successfully!")
                    
                elif message_type == "response.text.delta":
                    # Print text responses
                    text = data.get("delta", "")
                    print(f"🤖: {text}", end="", flush=True)
                    
                elif message_type == "response.audio.delta":
                    # Play audio responses
                    if self.output_stream:
                        audio_data = base64.b64decode(data.get("delta", ""))
                        self.output_stream.write(audio_data)
                
                elif message_type == "response.done":
                    print("\n")  # New line after response
                    
                elif message_type == "error":
                    print(f"❌ Error: {data.get('error', {}).get('message', 'Unknown error')}")
                    
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connection closed")
        except Exception as e:
            print(f"❌ Message handling error: {e}")
    
    async def send_audio(self):
        """Send audio from microphone to OpenAI"""
        try:
            while self.is_connected and self.input_stream:
                # Read audio chunk
                audio_data = self.input_stream.read(self.chunk_size, exception_on_overflow=False)
                
                # Encode as base64
                audio_b64 = base64.b64encode(audio_data).decode('utf-8')
                
                # Send to OpenAI
                message = {
                    "type": "input_audio_buffer.append",
                    "audio": audio_b64
                }
                
                await self.websocket.send(json.dumps(message))
                await asyncio.sleep(0.01)  # Small delay to prevent overwhelming
                
        except Exception as e:
            if self.is_connected:  # Only log if not intentionally disconnected
                print(f"❌ Audio sending error: {e}")
    
    async def start_conversation(self):
        """Start the voice conversation"""
        if not await self.connect():
            return False
        
        if not self.setup_audio():
            return False
        
        print("\n🎤 Voice conversation started!")
        print("🗣️ Start speaking... (Press Ctrl+C to stop)")
        print("📝 You can say things like:")
        print("   • 'Hello, how are you?'")
        print("   • 'What's the weather like?'")
        print("   • 'Tell me a joke'")
        print("   • 'Calculate 15 times 7'")
        
        try:
            # Start listening and sending tasks concurrently
            await asyncio.gather(
                self.listen_for_messages(),
                self.send_audio()
            )
        except KeyboardInterrupt:
            print("\n👋 Stopping conversation...")
        finally:
            await self.cleanup()
        
        return True
    
    async def cleanup(self):
        """Cleanup resources"""
        self.is_connected = False
        
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
        
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
        
        if self.audio:
            self.audio.terminate()
        
        if self.websocket:
            await self.websocket.close()
        
        print("🧹 Cleanup complete")

async def main():
    """Main function"""
    print("🎤 Simple OpenAI Realtime Voice Test")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found")
        print("Please set OPENAI_API_KEY in your .env file")
        return
    
    print("✅ API key found")
    
    # Create and run voice test
    voice_test = SimpleVoiceTest(api_key)
    
    try:
        success = await voice_test.start_conversation()
        if success:
            print("🎉 Voice test completed successfully!")
        else:
            print("❌ Voice test failed")
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n📝 If this worked, your realtime setup is correct!")
    print("📝 You can now use the full JARVIS agent with tools")

if __name__ == "__main__":
    asyncio.run(main())
