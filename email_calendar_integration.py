"""
Interactive Calendar Event Creation
Handles the flow of parsing emails for events and creating calendar entries
"""

import asyncio
import json
import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class ParsedEvent:
    """Data class for parsed email events"""
    title: str
    date: Optional[str]
    time: Optional[str]
    location: Optional[str]
    event_type: str
    confidence: float
    email_subject: str
    email_sender: str
    raw_content: str

class EventCreationFlow:
    """Manages the interactive flow for creating calendar events from emails"""
    
    def __init__(self, agent):
        self.agent = agent
        self.pending_events: List[ParsedEvent] = []
    
    async def process_email_events(self, email_parse_result: str) -> str:
        """Process the result of email parsing and start interactive flow"""
        try:
            # Extract events from the parse result
            events = self._extract_events_from_result(email_parse_result)
            
            if not events:
                return "No events found in emails to process."
            
            self.pending_events = events
            
            # Start interactive flow
            return await self._start_interactive_flow()
            
        except Exception as e:
            return f"Error processing email events: {e}"
    
    def _extract_events_from_result(self, result: str) -> List[ParsedEvent]:
        """Extract event data from email parsing result"""
        events = []
        
        # This is a simplified parser - in a real implementation,
        # you might use regex or structured parsing
        
        # For now, return empty list as the full parsing would happen
        # in the smart_gmail tool
        return events
    
    async def _start_interactive_flow(self) -> str:
        """Start the interactive event creation flow"""
        try:
            if not self.pending_events:
                return "No pending events to process."
            
            print(f"\n🗓️ Found {len(self.pending_events)} potential calendar events!")
            
            for i, event in enumerate(self.pending_events, 1):
                print(f"\n📋 Event {i}:")
                print(f"   Title: {event.title}")
                print(f"   Date: {event.date or 'Not specified'}")
                print(f"   Time: {event.time or 'Not specified'}")
                print(f"   Type: {event.event_type}")
                print(f"   From: {event.email_sender}")
                print(f"   Confidence: {event.confidence:.2f}")
                
                # Ask user for confirmation
                response = await self._ask_user_confirmation(event)
                
                if response == "yes":
                    result = await self._create_calendar_event(event)
                    print(f"   {result}")
                elif response == "edit":
                    edited_event = await self._edit_event_details(event)
                    result = await self._create_calendar_event(edited_event)
                    print(f"   {result}")
                else:
                    print("   ⏭️ Skipped")
            
            return f"Processed {len(self.pending_events)} potential events."
            
        except Exception as e:
            return f"Error in interactive flow: {e}"
    
    async def _ask_user_confirmation(self, event: ParsedEvent) -> str:
        """Ask user whether to create the calendar event"""
        try:
            # In voice mode, this would be handled via voice interaction
            # For now, simulate the decision-making process
            
            # Auto-approve high-confidence events with clear dates
            if event.confidence > 0.9 and event.date:
                return "yes"
            
            # For lower confidence or missing info, we'd ask the user
            # This would be integrated with the voice interface
            
            return "ask"  # Placeholder - would be interactive
            
        except Exception as e:
            print(f"Error in user confirmation: {e}")
            return "no"
    
    async def _edit_event_details(self, event: ParsedEvent) -> ParsedEvent:
        """Allow user to edit event details before creation"""
        try:
            # In a full implementation, this would allow voice editing
            # For now, return the original event
            return event
            
        except Exception as e:
            print(f"Error editing event: {e}")
            return event
    
    async def _create_calendar_event(self, event: ParsedEvent) -> str:
        """Create the actual calendar event"""
        try:
            calendar_tool = self.agent.tool_instances.get("smart_google_calendar")
            
            if not calendar_tool:
                return "❌ Calendar tool not available"
            
            # Prepare event data
            event_data = {
                "title": event.title,
                "date": event.date,
                "time": event.time,
                "location": event.location,
                "type": event.event_type
            }
            
            # Create the event
            result = calendar_tool._run("create_from_email", event_data=event_data)
            
            return result
            
        except Exception as e:
            return f"❌ Failed to create event: {e}"

class EmailCalendarIntegration:
    """High-level integration between email parsing and calendar creation"""
    
    def __init__(self, agent):
        self.agent = agent
        self.event_flow = EventCreationFlow(agent)
    
    async def summarize_and_suggest_events(self, days_back: int = 7) -> str:
        """Summarize recent emails and suggest calendar events"""
        try:
            # Get Gmail tool
            gmail_tool = self.agent.tool_instances.get("smart_gmail")
            if not gmail_tool:
                return "Gmail tool not available"
            
            # Parse recent emails for events
            print("🔍 Analyzing recent emails for events...")
            
            result = gmail_tool._run(
                action="parse_events",
                query="",  # All recent emails
                max_emails=20
            )
            
            # Process any found events
            if "Found 0 potential calendar events" not in result:
                flow_result = await self.event_flow.process_email_events(result)
                return f"{result}\n\n{flow_result}"
            else:
                return result
            
        except Exception as e:
            return f"Error in email-calendar integration: {e}"
    
    async def handle_voice_command(self, command: str) -> str:
        """Handle voice commands related to email and calendar"""
        try:
            command_lower = command.lower()
            
            if any(phrase in command_lower for phrase in ["summarize", "summary", "emails"]):
                if "today" in command_lower:
                    return await self.summarize_and_suggest_events(days_back=1)
                else:
                    return await self.summarize_and_suggest_events()
            
            elif any(phrase in command_lower for phrase in ["calendar", "schedule", "events"]):
                calendar_tool = self.agent.tool_instances.get("smart_google_calendar")
                if calendar_tool:
                    today = datetime.datetime.now().strftime("%Y-%m-%d")
                    return calendar_tool._run("read", date=today)
                else:
                    return "Calendar tool not available"
            
            elif "add" in command_lower and ("calendar" in command_lower or "event" in command_lower):
                return "Please provide event details: title, date, and time."
            
            else:
                return "Command not recognized for email-calendar integration"
                
        except Exception as e:
            return f"Error handling voice command: {e}"
