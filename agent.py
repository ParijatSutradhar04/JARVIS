"""
LangChain Agent setup with OpenAI Realtime integration
Orchestrates the AI agent with tools and memory
"""

import asyncio
import datetime
import logging
from typing import Dict, Any, List, Optional, Callable
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import BaseMessage, HumanMessage, AIMessage

from tools import get_all_tools, get_tools_for_realtime
from realtime_client import RealtimeClient
from email_calendar_integration import EmailCalendarIntegration

logger = logging.getLogger(__name__)

class VoiceAgent:
    """
    Main agent class that combines LangChain with OpenAI Realtime API
    """
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        
        # Initialize components
        self.realtime_client = None
        self.langchain_agent = None
        self.memory = None
        self.tools = None
        
        # Agent state
        self.is_running = False
        self.conversation_history = []
        
        # Tool execution mapping
        self.tool_instances = {}
        
        # Email-Calendar integration
        self.email_calendar = None
        
    async def initialize(self):
        """Initialize the agent with all components"""
        try:
            # Setup memory
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                input_key="input",
                output_key="output"
            )
            
            # Setup tools
            self.tools = get_all_tools()
            self.tool_instances = {tool.name: tool for tool in self.tools}
            
            # Setup LangChain agent (for fallback text mode)
            await self._setup_langchain_agent()
            print("LangChain agent setup complete")
            
            # Setup realtime client
            await self._setup_realtime_client()
            print("Realtime client setup complete")

            # Setup email-calendar integration
            self.email_calendar = EmailCalendarIntegration(self)
            
            logger.info("Voice agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise
    
    async def _setup_langchain_agent(self):
        """Setup the LangChain agent for text-based interactions"""
        try:
            # Create OpenAI LLM (for text fallback)
            llm = ChatOpenAI(
                model="gpt-4",
                api_key=self.openai_api_key,
                temperature=0.7
            )
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are JARVIS, a helpful voice assistant. You can:
                - Read and send emails via Gmail
                - Check and create calendar events
                - Execute Python code for calculations
                - Get weather information
                - Tell time in any timezone
                - Remember information across conversations
                
                Be conversational and helpful. When users ask for help, explain what you can do.
                Always confirm before taking actions like sending emails or creating calendar events.
                """),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])
            
            # Create agent
            agent = create_openai_tools_agent(llm, self.tools, prompt)
            
            # Create executor
            self.langchain_agent = AgentExecutor(
                agent=agent,
                tools=self.tools,
                memory=self.memory,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=3
            )
            
            logger.info("LangChain agent setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup LangChain agent: {e}")
            raise
    
    async def _setup_realtime_client(self):
        """Setup the OpenAI Realtime client"""
        try:
            self.realtime_client = RealtimeClient(self.openai_api_key)
            print("Realtime client created")

            # Set event handlers
            self.realtime_client.set_event_handlers(
                on_audio_received=self._handle_audio_response,
                on_text_received=self._handle_text_response,
                on_function_call=self._handle_function_call
            )
            
            # Initialize session with tools
            realtime_tools = get_tools_for_realtime()
            print("Initializing realtime session with tools...")
            await self.realtime_client.initialize_session(tools=realtime_tools)
            print("✅ Realtime session initialized")

            # Setup audio
            self.realtime_client.setup_audio()
            
            logger.info("Realtime client setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup realtime client: {e}")
            # Continue without realtime - fallback to text mode
            print("Realtime setup failed. Falling back to text mode.")
    
    async def _handle_audio_response(self, audio_data: bytes):
        """Handle audio response from the realtime API"""
        try:
            # Audio is already being played in realtime_client._handle_audio_delta
            # This handler is for additional processing if needed
            pass
        except Exception as e:
            logger.error(f"Failed to handle audio response: {e}")
    
    async def _handle_text_response(self, text: str):
        """Handle text response from the realtime API"""
        try:
            print(f"Assistant: {text}")
            
            # Store in conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": text,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to handle text response: {e}")
    
    async def _handle_function_call(self, function_name: str, function_args: Dict[str, Any]):
        """Handle function calls from the realtime API"""
        try:
            print(f"🔧 Executing tool: {function_name} with args: {function_args}")
            
            # Map realtime function names to tool instances
            tool_mapping = {
                "smart_gmail": "smart_gmail",
                "smart_google_calendar": "smart_google_calendar", 
                "python_repl": "python_repl",
                "get_weather": "get_weather",
                "get_time": "get_time",
                "memory": "memory"
            }
            
            mapped_name = tool_mapping.get(function_name, function_name)
            
            # Execute the tool
            if mapped_name in self.tool_instances:
                tool = self.tool_instances[mapped_name]
                result = tool._run(**function_args)
                
                print(f"✅ Tool result: {result}")
                
                # Special handling for email event parsing
                if function_name == "smart_gmail" and function_args.get("action") == "parse_events":
                    await self._handle_email_events_interactive(result)
                
                return result
            else:
                error_msg = f"Unknown tool: {function_name}"
                print(f"❌ {error_msg}")
                return error_msg
                
        except Exception as e:
            error_msg = f"Tool execution error: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return error_msg
    
    async def _handle_response_done(self):
        """Handle when a response is complete"""
        try:
            print("🎯 Response complete")
        except Exception as e:
            logger.error(f"Error handling response done: {e}")
    
    async def _handle_email_events_interactive(self, events_text: str):
        """Handle interactive event creation from email parsing"""
        try:
            # Check if events were found
            if "Found 0 potential calendar events" in events_text or "No events" in events_text:
                return
            
            # For now, just log that we found events
            # In a full implementation, this would trigger an interactive flow
            print("🗓️ Found potential calendar events in emails!")
            print("Interactive event creation would be triggered here.")
            
            # TODO: Implement interactive calendar event creation
            # This could involve:
            # 1. Presenting events to user
            # 2. Asking for confirmation
            # 3. Creating calendar events
            
        except Exception as e:
            logger.error(f"Error handling email events: {e}")
    
    async def start_voice_conversation(self):
        """Start the voice conversation loop"""
        try:
            if not self.realtime_client:
                print("Realtime client not available. Use text mode instead.")
                return
            
            print("Starting voice conversation...")
            print("Speak into your microphone. The assistant will respond in real-time.")
            print("Press Ctrl+C to stop.")
            
            self.is_running = True
            await self.realtime_client.start_conversation()
            
        except Exception as e:
            logger.error(f"Voice conversation error: {e}")
        finally:
            self.is_running = False
    
    async def text_conversation(self, user_input: str) -> str:
        """Handle text-based conversation (fallback mode)"""
        try:
            if not self.langchain_agent:
                return "Agent not properly initialized."
            
            # Store user input in history
            self.conversation_history.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            # Check if this is an email-calendar command
            if self.email_calendar:
                email_calendar_response = await self.email_calendar.handle_voice_command(user_input)
                if "Command not recognized" not in email_calendar_response:
                    # Store response in history
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": email_calendar_response,
                        "timestamp": datetime.datetime.now().isoformat()
                    })
                    return email_calendar_response
            
            # Execute via LangChain agent for other commands
            result = await asyncio.to_thread(
                self.langchain_agent.invoke,
                {"input": user_input}
            )
            
            response = result.get("output", "No response generated.")
            
            # Store response in history
            self.conversation_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            error_msg = f"Text conversation error: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    async def interactive_text_mode(self):
        """Run interactive text conversation mode"""
        print("\n=== JARVIS Text Mode ===")
        print("Type 'quit', 'exit', or 'bye' to stop.")
        print("Type 'voice' to switch to voice mode (if available).")
        print("Type 'emails' to quickly summarize and parse emails.")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("Goodbye!")
                    break
                elif user_input.lower() == 'voice':
                    if self.realtime_client and self.realtime_client.is_connected:
                        await self.start_voice_conversation()
                    else:
                        print("❌ Voice mode not available. Realtime client not connected.")
                    continue
                elif user_input.lower() == 'emails':
                    # Quick command for email summary
                    if self.email_calendar:
                        response = await self.email_calendar.summarize_and_suggest_events()
                        print(f"Assistant: {response}")
                    else:
                        print("Assistant: Email integration not available")
                    continue
                elif not user_input:
                    continue
                
                print("Assistant: ", end="", flush=True)
                response = await self.text_conversation(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    async def cleanup(self):
        """Clean up resources"""
        self.is_running = False
        if self.realtime_client:
            await self.realtime_client.cleanup()
        logger.info("Agent cleanup complete")

# Utility function for testing individual tools
async def test_tools():
    """Test individual tools"""
    print("Testing tools...")
    
    tools = get_all_tools()
    
    # Test Python REPL
    python_tool = next((t for t in tools if t.name == "python_repl"), None)
    if python_tool:
        result = python_tool._run("print('Hello from Python REPL!')")
        print(f"Python REPL test: {result}")
    
    # Test Time tool
    time_tool = next((t for t in tools if t.name == "get_time"), None)
    if time_tool:
        result = time_tool._run()
        print(f"Time tool test: {result}")
    
    # Test Memory tool
    memory_tool = next((t for t in tools if t.name == "memory"), None)
    if memory_tool:
        memory_tool._run("store", "test_key", "test_value")
        result = memory_tool._run("retrieve", "test_key")
        print(f"Memory tool test: {result}")

if __name__ == "__main__":
    asyncio.run(test_tools())
