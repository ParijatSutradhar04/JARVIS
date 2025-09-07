"""
Realtime Client for OpenAI GPT-4o-realtime API
Handles microphone input/output and streaming session management
"""

import asyncio
import json
import logging
import websockets
import pyaudio
import wave
import threading
import base64
import numpy as np
from typing import Optional, Callable, Dict, Any
import os

logger = logging.getLogger(__name__)

class RealtimeClient:
    """
    Manages real-time audio communication with OpenAI's GPT-4o-realtime API
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o-realtime-preview-2024-10-01"):
        self.api_key = api_key
        self.model = model
        self.client = None  # Will be initialized lazily
        
        # Audio configuration
        self.sample_rate = 24000  # OpenAI Realtime API expects 24kHz
        self.channels = 1
        self.chunk_size = 1024
        
        # Audio streams
        self.audio = None
        self.input_stream = None
        self.output_stream = None
        
        # WebSocket connection
        self.websocket = None
        self.session_id = None
        self.url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
        
        # Event handlers
        self.on_audio_received: Optional[Callable] = None
        self.on_text_received: Optional[Callable] = None
        self.on_function_call: Optional[Callable] = None
        self.on_response_done: Optional[Callable] = None
        
        # Control flags
        self.is_recording = False
        self.is_playing = False
        self.is_connected = False
        
        # Audio buffer for streaming
        self.audio_buffer = asyncio.Queue()
        self._audio_response_buffer = b''
        
        # Response state tracking
        self._response_in_progress = False
        
    async def initialize_session(self, tools: list = None):
        """Initialize the realtime session with OpenAI"""
        try:
            # Store reference to current event loop for audio callback
            self._loop = asyncio.get_running_loop()
            
            # Lazy import AsyncOpenAI to avoid hanging during module import
            from openai import AsyncOpenAI
            if self.client is None:
                self.client = AsyncOpenAI(api_key=self.api_key)
                
            # WebSocket headers for authentication
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            logger.info(f"Connecting to OpenAI Realtime API: {self.url}")
            
            # Connect to WebSocket
            self.websocket = await websockets.connect(
                self.url,
                additional_headers=headers,
                ping_interval=20,
                ping_timeout=10
            )
            
            self.is_connected = True
            print("Websocket connection established")
            logger.info("WebSocket connection established")
            
            # Create session configuration
            session_config = {
                "type": "session.update",
                "session": {
                    "modalities": ["text", "audio"],
                    "instructions": """You are JARVIS, a helpful voice assistant. You can:
                    - Read and send emails via Gmail
                    - Check and create calendar events  
                    - Execute Python code for calculations
                    - Get weather information
                    - Tell time in any timezone
                    - Remember information across conversations
                    
                    Be conversational and helpful. Always confirm before taking important actions like sending emails or creating calendar events.""",
                    "voice": "alloy",
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16",
                    "input_audio_transcription": {"model": "whisper-1"},
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 200
                    },
                    "tools": tools or []
                }
            }
            
            # Send session configuration
            await self.websocket.send(json.dumps(session_config))
            logger.info("Session configuration sent")
            
            # Start listening for events
            asyncio.create_task(self._listen_for_events())
            
        except Exception as e:
            logger.error(f"Failed to initialize session: {e}")
            print("Failed to initialize session")
            self.is_connected = False
            raise
    
    def setup_audio(self):
        """Initialize PyAudio for microphone input and speaker output"""
        try:
            self.audio = pyaudio.PyAudio()
            
            # Input stream (microphone)
            self.input_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_input_callback
            )
            
            # Output stream (speakers)
            self.output_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size
            )
            
            logger.info("Audio streams initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup audio: {e}")
            print("Audio setup failed. Falling back to text mode.")
    
    def _audio_input_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio input from microphone"""
        if self.is_recording and self.is_connected:
            # Use thread-safe approach to schedule async task
            try:
                if hasattr(self, '_loop') and self._loop:
                    asyncio.run_coroutine_threadsafe(
                        self._send_audio_data(in_data), self._loop
                    )
            except Exception as e:
                logger.error(f"Audio input callback error: {e}")
        
        return (None, pyaudio.paContinue)
    
    async def _send_audio_data(self, audio_data: bytes):
        """Send audio data to the realtime API"""
        try:
            if not self.websocket or not self.is_connected:
                return
                
            # Convert PCM16 audio to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            message = {
                "type": "input_audio_buffer.append",
                "audio": audio_base64
            }
            
            await self.websocket.send(json.dumps(message))
            
        except Exception as e:
            logger.error(f"Failed to send audio data: {e}")
    
    async def _listen_for_events(self):
        """Listen for events from the realtime API"""
        try:
            async for message in self.websocket:
                try:
                    event = json.loads(message)
                    await self._handle_event(event)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse message: {e}")
                except Exception as e:
                    logger.error(f"Error handling event: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            print("WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"Error in event listener: {e}")
            print("Error in event listener")
            self.is_connected = False
    
    async def _handle_event(self, event: Dict[str, Any]):
        """Handle different types of events from the API"""
        event_type = event.get("type", "")
        
        if event_type == "session.created":
            self.session_id = event.get("session", {}).get("id")
            logger.info(f"Session created: {self.session_id}")
            
        elif event_type == "session.updated":
            logger.info("Session updated")
            
        elif event_type == "input_audio_buffer.speech_started":
            logger.info("Speech started")
            
        elif event_type == "input_audio_buffer.speech_stopped":
            logger.info("Speech stopped")
            # Only trigger response if not already in progress
            if not self._response_in_progress:
                self._response_in_progress = True
                await self._create_response()
            
        elif event_type == "response.audio.delta":
            # Handle streaming audio response
            audio_data = event.get("delta", "")
            if audio_data:
                await self._handle_audio_delta(audio_data)
                
        elif event_type == "response.audio_transcript.delta":
            # Handle text transcription of audio response
            text = event.get("delta", "")
            if text and self.on_text_received:
                await self.on_text_received(text)
                
        elif event_type == "response.function_call_arguments.delta":
            # Handle function call streaming
            await self._handle_function_call_delta(event)
            
        elif event_type == "response.function_call_arguments.done":
            # Function call complete, execute it
            await self._execute_function_call(event)
            
        elif event_type == "response.done":
            # Reset response state
            self._response_in_progress = False
            if self.on_response_done:
                await self.on_response_done()
                
        elif event_type == "error":
            logger.error(f"API error: {event}")
            self._response_in_progress = False  # Reset on error
            
        else:
            logger.debug(f"Unhandled event type: {event_type}")
    
    async def _handle_audio_delta(self, audio_base64: str):
        """Handle streaming audio response"""
        try:
            # Decode base64 audio data
            audio_data = base64.b64decode(audio_base64)
            
            # Buffer audio data for smooth playback
            self._audio_response_buffer += audio_data
            
            # Play buffered audio in chunks to prevent overlapping
            if self.output_stream and not self.is_playing and len(self._audio_response_buffer) >= self.chunk_size:
                self.is_playing = True
                try:
                    # Play chunk and keep remainder in buffer
                    chunk_to_play = self._audio_response_buffer[:self.chunk_size]
                    self._audio_response_buffer = self._audio_response_buffer[self.chunk_size:]
                    self.output_stream.write(chunk_to_play)
                finally:
                    self.is_playing = False
                
            if self.on_audio_received:
                await self.on_audio_received(audio_data)
                
        except Exception as e:
            logger.error(f"Failed to handle audio delta: {e}")
            self.is_playing = False
    
    async def _handle_function_call_delta(self, event: Dict[str, Any]):
        """Handle streaming function call arguments"""
        # For now, we'll collect the full arguments and execute when done
        pass
    
    async def _execute_function_call(self, event: Dict[str, Any]):
        """Execute a completed function call"""
        try:
            call_id = event.get("call_id")
            name = event.get("name")
            arguments = event.get("arguments", "{}")
            
            if self.on_function_call:
                result = await self.on_function_call(name, json.loads(arguments))
                
                # Send function result back to API
                function_result = {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": str(result)
                    }
                }
                
                await self.websocket.send(json.dumps(function_result))
                
                # Create response after function execution
                if not self._response_in_progress:
                    self._response_in_progress = True
                    await self._create_response()
                
        except Exception as e:
            logger.error(f"Failed to execute function call: {e}")
    
    async def _create_response(self):
        """Trigger response generation"""
        try:
            response_message = {
                "type": "response.create",
                "response": {
                    "modalities": ["text", "audio"],
                    "instructions": "Please respond naturally and conversationally."
                }
            }
            
            await self.websocket.send(json.dumps(response_message))
            
        except Exception as e:
            logger.error(f"Failed to create response: {e}")
            self._response_in_progress = False
    
    async def start_conversation(self):
        """Start the conversation loop"""
        print("🎤 Voice mode active - speak into your microphone...")
        print("Press Ctrl+C to stop")
        
        try:
            # Start recording
            self.is_recording = True
            if self.input_stream:
                self.input_stream.start_stream()
                print("🔴 Recording started")
            
            # Keep the conversation alive
            while self.is_connected:
                await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping conversation...")
        finally:
            await self.cleanup()
    
    async def send_text_message(self, text: str):
        """Send a text message (fallback for voice)"""
        try:
            if not self.websocket or not self.is_connected:
                raise Exception("Not connected to Realtime API")
            
            # Create conversation item
            message = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": text}]
                }
            }
            
            await self.websocket.send(json.dumps(message))
            logger.info(f"Sent text message: {text}")
            
            # Trigger response generation
            if not self._response_in_progress:
                self._response_in_progress = True
                await self._create_response()
            
        except Exception as e:
            logger.error(f"Failed to send text message: {e}")
            raise
    
    def play_audio(self, audio_data: bytes):
        """Play audio through speakers"""
        try:
            if self.output_stream and not self.is_playing:
                self.is_playing = True
                try:
                    self.output_stream.write(audio_data)
                finally:
                    self.is_playing = False
        except Exception as e:
            logger.error(f"Failed to play audio: {e}")
    
    async def cleanup(self):
        """Clean up resources"""
        self.is_recording = False
        self.is_playing = False
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
        
        logger.info("Realtime client cleaned up")

    def set_event_handlers(self, 
                          on_audio_received: Optional[Callable] = None,
                          on_text_received: Optional[Callable] = None,
                          on_function_call: Optional[Callable] = None,
                          on_response_done: Optional[Callable] = None):
        """Set event handlers for different types of responses"""
        self.on_audio_received = on_audio_received
        self.on_text_received = on_text_received
        self.on_function_call = on_function_call
        self.on_response_done = on_response_done
