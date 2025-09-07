#!/usr/bin/env python3
"""
Simple Diagnostic Script for Echo/Repetition Issues
"""

import asyncio
import os
import logging
import time
from datetime import datetime
from dotenv import load_dotenv

# Configure simple logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(message)s')

load_dotenv()

class SimpleDebugger:
    def __init__(self):
        self.events = []
        self.audio_deltas = 0
        self.responses = 0
        self.listeners = 0
        self.sessions = 0
        
    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.events.append(f"[{timestamp}] {msg}")
        print(f"[{timestamp}] {msg}")
        
    def summary(self):
        print("\n" + "="*50)
        print("DIAGNOSTIC SUMMARY")
        print("="*50)
        print(f"Total events logged: {len(self.events)}")
        print(f"Audio deltas: {self.audio_deltas}")
        print(f"Response creations: {self.responses}")
        print(f"Listener tasks: {self.listeners}")
        print(f"Session inits: {self.sessions}")
        
        # Check for suspicious patterns
        audio_events = [e for e in self.events if 'audio.delta' in e]
        response_events = [e for e in self.events if 'response.create' in e or 'Creating response' in e]
        
        print(f"\nAudio delta events: {len(audio_events)}")
        print(f"Response creation events: {len(response_events)}")
        
        if len(response_events) > 3:
            print("WARNING: Many response creations detected!")
        if len(audio_events) > 20:
            print("WARNING: Many audio deltas - possible repetition!")

debugger = SimpleDebugger()

async def test_realtime_basic():
    print("Starting Basic Realtime Test")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("No API key")
        return
        
    debugger.log("Importing RealtimeClient")
    from realtime_client import RealtimeClient
    
    # Create client
    debugger.log("Creating client")
    client = RealtimeClient(api_key)
    debugger.sessions += 1
    
    # Patch some methods for debugging
    original_handle_event = client._handle_event
    original_handle_audio_delta = client._handle_audio_delta
    original_create_response = client._create_response
    
    async def debug_handle_event(event):
        event_type = event.get("type", "unknown")
        debugger.log(f"Event: {event_type}")
        return await original_handle_event(event)
        
    async def debug_handle_audio_delta(audio_base64):
        debugger.audio_deltas += 1
        debugger.log(f"Audio delta #{debugger.audio_deltas} (length: {len(audio_base64)})")
        return await original_handle_audio_delta(audio_base64)
        
    async def debug_create_response():
        debugger.responses += 1
        debugger.log(f"Creating response #{debugger.responses}")
        return await original_create_response()
    
    client._handle_event = debug_handle_event
    client._handle_audio_delta = debug_handle_audio_delta  
    client._create_response = debug_create_response
    
    try:
        debugger.log("Initializing session")
        await client.initialize_session([])
        
        debugger.log("Setting up audio")
        client.setup_audio()
        
        if client.is_connected:
            debugger.log("Connected! Starting 5-second test")
            client.is_recording = True
            
            if client.input_stream:
                client.input_stream.start_stream()
                
            # Test for 5 seconds
            for i in range(10):  # 10 x 0.5s = 5s
                await asyncio.sleep(0.5)
                if i % 2 == 0:  # Every 1 second
                    debugger.log(f"Test progress: {(i+1)*0.5}s")
                    
            client.is_recording = False
            if client.input_stream:
                client.input_stream.stop_stream()
                
            debugger.log("Test completed")
        else:
            debugger.log("Failed to connect")
            
    except Exception as e:
        debugger.log(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.cleanup()
        debugger.log("Cleanup completed")
        
    debugger.summary()

if __name__ == "__main__":
    asyncio.run(test_realtime_basic())
