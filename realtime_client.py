"""
Realtime Client for OpenAI GPT-4o-realtime API - Clean Version
Handles microphone input/output and streaming session management
"""

import asyncio
import json
import logging
import websockets
import pyaudio
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
        self.client = None
        
        # Audio configuration
        self.sample_rate = 24000
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
        self._audio_output_active = False
        self._suppress_input_during_output = True
        
        # State tracking - CRITICAL: Only one of each
        self._response_in_progress = False
        self._response_start_time = None
        self._response_timeout = 30.0  # 30 second timeout
        self._function_call_in_progress = False
        self._listener_task = None
        self._loop = None
        
    async def initialize_session(self, tools: list = None):
        """Initialize the realtime session with OpenAI - ONLY CALL ONCE"""
        try:
            # Store event loop reference
            self._loop = asyncio.get_running_loop()
            
            # Lazy import to avoid hanging
            from openai import AsyncOpenAI
            if self.client is None:
                self.client = AsyncOpenAI(api_key=self.api_key)
                
            # WebSocket headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            logger.info(f"Connecting to OpenAI Realtime API: {self.url}")
            
            # CRITICAL: Only create one WebSocket connection
            if self.websocket is not None:
                logger.warning("Session already initialized, skipping")
                return
                
            self.websocket = await websockets.connect(
                self.url,
                additional_headers=headers,
                ping_interval=20,
                ping_timeout=10
            )
            
            self.is_connected = True
            logger.info("WebSocket connection established")
            
            # Session configuration
            session_config = {
                "type": "session.update",
                "session": {
                    "modalities": ["text", "audio"],
                    "instructions": """You are JARVIS, a helpful voice assistant. Be conversational and concise.""",
                    "voice": "alloy",
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16",
                    "input_audio_transcription": {"model": "whisper-1"},
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.6,
                        "prefix_padding_ms": 500,
                        "silence_duration_ms": 800
                    },
                    "tools": tools or []
                }
            }
            
            await self.websocket.send(json.dumps(session_config))
            logger.info("Session configuration sent")
            
            # CRITICAL: Only start ONE event listener
            if self._listener_task is None or self._listener_task.done():
                self._listener_task = asyncio.create_task(self._listen_for_events())
                logger.info("Event listener started")
            
        except Exception as e:
            logger.error(f"Failed to initialize session: {e}")
            self.is_connected = False
            raise
    
    def setup_audio(self):
        """Initialize PyAudio streams"""
        try:
            self.audio = pyaudio.PyAudio()
            
            # Input stream
            self.input_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_input_callback
            )
            
            # Output stream
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
    
    def _audio_input_callback(self, in_data, frame_count, time_info, status):
        """Audio input callback - CRITICAL: Prevent feedback"""
        # Only record if not outputting audio (prevents feedback loop)
        if (self.is_recording and self.is_connected and 
            not (self._suppress_input_during_output and self._audio_output_active)):
            try:
                if self._loop:
                    asyncio.run_coroutine_threadsafe(
                        self._send_audio_data(in_data), self._loop
                    )
            except Exception as e:
                logger.error(f"Audio input error: {e}")
        
        return (None, pyaudio.paContinue)
    
    async def _send_audio_data(self, audio_data: bytes):
        """Send audio to realtime API"""
        try:
            if not self.websocket or not self.is_connected:
                return
                
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            message = {
                "type": "input_audio_buffer.append",
                "audio": audio_base64
            }
            
            await self.websocket.send(json.dumps(message))
            
        except Exception as e:
            logger.error(f"Failed to send audio: {e}")
    
    async def _listen_for_events(self):
        """Event listener - CRITICAL: Only one instance"""
        try:
            async for message in self.websocket:
                try:
                    event = json.loads(message)
                    await self._handle_event(event)
                except Exception as e:
                    logger.error(f"Event handling error: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"Event listener error: {e}")
            self.is_connected = False
    
    async def _handle_event(self, event: Dict[str, Any]):
        """Handle events - CRITICAL: Prevent duplicate responses"""
        event_type = event.get("type", "")
        
        if event_type == "session.created":
            self.session_id = event.get("session", {}).get("id")
            logger.info(f"Session created: {self.session_id}")
            
        elif event_type == "session.updated":
            logger.info("Session updated")
            
        elif event_type == "input_audio_buffer.speech_started":
            logger.info("Speech started")
            if self._audio_output_active:
                logger.warning("FEEDBACK DETECTED: Speech while audio output active!")
            
        elif event_type == "input_audio_buffer.speech_stopped":
            logger.info("Speech stopped")
            # Check for timeout on existing response
            if (self._response_in_progress and self._response_start_time and 
                (asyncio.get_event_loop().time() - self._response_start_time) > self._response_timeout):
                logger.warning("Response timeout - resetting state")
                self._response_in_progress = False
                self._response_start_time = None
            
            # CRITICAL: Only create response if not already in progress
            if not self._response_in_progress:
                self._response_in_progress = True
                self._response_start_time = asyncio.get_event_loop().time()
                logger.info("Creating response for speech input...")
                await self._create_response()
            else:
                logger.warning("Speech stopped but response already in progress - skipping")
            
        elif event_type == "response.created":
            logger.info("Response created by API")
            
        elif event_type == "response.output_item.added":
            logger.info("Response output item added")
            
        elif event_type == "response.audio.delta":
            audio_data = event.get("delta", "")
            if audio_data:
                await self._handle_audio_delta(audio_data)
                
        elif event_type == "response.audio_transcript.delta":
            text = event.get("delta", "")
            if text and self.on_text_received:
                await self.on_text_received(text)
                
        elif event_type == "response.function_call_arguments.delta":
            # Function call arguments streaming
            logger.info("Function call arguments delta received")
            
        elif event_type == "response.function_call_arguments.done":
            # Function call complete - execute it
            logger.info("Function call arguments complete")
            self._function_call_in_progress = True
            await self._execute_function_call(event)
                
        elif event_type == "response.done":
            logger.info("Response completed")
            self._response_in_progress = False
            self._response_start_time = None
            self._function_call_in_progress = False
            
            # Re-enable microphone after delay
            if self._audio_output_active:
                await asyncio.sleep(0.3)
                self._audio_output_active = False
                logger.info("Microphone re-enabled")
            
            if self.on_response_done:
                await self.on_response_done()
                
        elif event_type == "error":
            error_details = event.get("error", {})
            error_code = error_details.get("code", "unknown")
            
            if error_code == "conversation_already_has_active_response":
                logger.warning("API rejected response creation - response already active")
                # If this happens during function call, reset the function call state
                if self._function_call_in_progress:
                    logger.info("Resetting function call state due to response conflict")
                    self._function_call_in_progress = False
            else:
                logger.error(f"API error: {event}")
                # Reset response state only on other errors
                self._response_in_progress = False
                self._function_call_in_progress = False
                self._audio_output_active = False
                logger.info("Response state reset due to error")
            
        else:
            logger.debug(f"Unhandled event type: {event_type}")
    
    async def _handle_audio_delta(self, audio_base64: str):
        """Handle audio response - CRITICAL: Immediate playback, no buffering"""
        try:
            audio_data = base64.b64decode(audio_base64)
            
            # Play immediately for smooth streaming
            if self.output_stream:
                if not self._audio_output_active:
                    self._audio_output_active = True
                    logger.info("Audio output started - microphone suppressed")
                
                # Direct playback for real-time streaming
                self.output_stream.write(audio_data)
                
            if self.on_audio_received:
                await self.on_audio_received(audio_data)
                
        except Exception as e:
            logger.error(f"Audio delta error: {e}")
            self._audio_output_active = False
    
    async def _execute_function_call(self, event: Dict[str, Any]):
        """Execute a completed function call"""
        try:
            call_id = event.get("call_id")
            name = event.get("name")
            arguments_str = event.get("arguments", "{}")
            
            logger.info(f"Executing function call: {name}")
            
            if self.on_function_call:
                # Parse arguments
                try:
                    arguments = json.loads(arguments_str)
                except json.JSONDecodeError:
                    arguments = {}
                
                # Execute function
                result = await self.on_function_call(name, arguments)
                
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
                logger.info(f"Function result sent: {result}")
                
                # CRITICAL: For function calls, we need to create a response
                # to have the assistant speak about the function result
                if self._function_call_in_progress:
                    # Wait a brief moment for any current response to settle
                    await asyncio.sleep(0.1)
                    
                    # Create response for function result
                    response_create = {
                        "type": "response.create",
                        "response": {
                            "modalities": ["text", "audio"]
                        }
                    }
                    
                    await self.websocket.send(json.dumps(response_create))
                    logger.info("Response created for function result")
                    self._function_call_in_progress = False
                
        except Exception as e:
            logger.error(f"Function execution error: {e}")
            # Reset response state on error
            self._response_in_progress = False
    
    async def _create_response(self):
        """Create response - CRITICAL: Protected by state flag"""
        try:
            response_message = {
                "type": "response.create",
                "response": {
                    "modalities": ["text", "audio"]
                }
            }
            
            await self.websocket.send(json.dumps(response_message))
            logger.info("Response created")
            
        except Exception as e:
            logger.error(f"Response creation error: {e}")
            self._response_in_progress = False
    
    async def start_conversation(self):
        """Start voice conversation"""
        print("Voice mode active - speak into microphone...")
        print("Press Ctrl+C to stop")
        
        try:
            self.is_recording = True
            if self.input_stream:
                self.input_stream.start_stream()
                print("Recording started")
            
            while self.is_connected:
                await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            print("Stopping conversation...")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources"""
        self.is_recording = False
        self.is_playing = False
        self.is_connected = False
        
        # Cancel tasks
        if self._listener_task and not self._listener_task.done():
            self._listener_task.cancel()
            
        # Close streams
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
        
        logger.info("Cleanup completed")

    def set_event_handlers(self, 
                          on_audio_received: Optional[Callable] = None,
                          on_text_received: Optional[Callable] = None,
                          on_function_call: Optional[Callable] = None,
                          on_response_done: Optional[Callable] = None):
        """Set event handlers"""
        self.on_audio_received = on_audio_received
        self.on_text_received = on_text_received
        self.on_function_call = on_function_call
        self.on_response_done = on_response_done
