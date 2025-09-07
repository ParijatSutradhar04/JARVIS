"""
LangChain Tools for the Voice AI Agent (Pydantic v2 Compatible)
Implements Gmail, Calendar, Python REPL, Weather, Time, and Memory tools
"""

import os
import subprocess
import datetime
import pytz
import requests
import re
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List, Type
import json
import base64
import pickle
import logging

# Configure module logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from langchain.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage
from langchain_openai import ChatOpenAI

# Google API imports (will need OAuth setup)
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("Google API libraries not available. Install google-api-python-client and related packages.")

# Input schemas for Pydantic v2
class SmartGmailInput(BaseModel):
    action: str = Field(description="Action to perform: 'read', 'search', 'send', 'parse_events', 'summary'")
    query: str = Field(default="", description="Search query for emails")
    recipient: str = Field(default="", description="Email recipient")
    subject: str = Field(default="", description="Email subject")
    body: str = Field(default="", description="Email body")
    max_emails: int = Field(default=10, description="Maximum number of emails to fetch")
    parse_events: bool = Field(default=True, description="Whether to parse emails for events")

class SmartCalendarInput(BaseModel):
    action: str = Field(description="Action to perform: 'read', 'create', 'check', 'create_from_email'")
    date: str = Field(default="", description="Date in YYYY-MM-DD format")
    title: str = Field(default="", description="Event title")
    start_time: str = Field(default="", description="Start time (HH:MM)")
    end_time: str = Field(default="", description="End time (HH:MM)")
    description: str = Field(default="", description="Event description")
    location: str = Field(default="", description="Event location")
    event_data: Optional[Dict] = Field(default=None, description="Parsed event data from email")

class PythonREPLInput(BaseModel):
    code: str = Field(description="Python code to execute")

class WeatherInput(BaseModel):
    location: str = Field(description="Location to get weather for")

class TimeInput(BaseModel):
    timezone: str = Field(default="local", description="Timezone or 'local'")

class MemoryInput(BaseModel):
    action: str = Field(description="Memory action: 'store', 'retrieve', 'search', or 'list'")
    key: str = Field(default="", description="Memory key")
    value: str = Field(default="", description="Value to store")
    query: str = Field(default="", description="Search query")

class SmartGmailTool(BaseTool):
    """Enhanced Gmail tool with intelligent email parsing for events and meetings"""
    
    name: str = "smart_gmail"
    description: str = "Read emails, parse for events/meetings, send emails, and suggest calendar entries"
    args_schema: Type[BaseModel] = SmartGmailInput
    
    # Allow extra fields in Pydantic v2
    model_config = ConfigDict(extra='allow')
    
    # Define as class attributes to avoid Pydantic field issues
    scopes: List[str] = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(self):
        super().__init__()
        # These are now allowed as extra fields
        self.service = None
        self.llm = None
    
    def _run(self, action: str, query: str = "", recipient: str = "", subject: str = "", 
             body: str = "", max_emails: int = 10, parse_events: bool = True) -> str:
        """
        Execute Gmail operations with intelligent parsing
        
        Args:
            action: "read", "search", "send", "parse_events", "summary"
            query: Search query for emails
            recipient: Email recipient (for send)
            subject: Email subject (for send)
            body: Email body (for send)
            max_emails: Maximum number of emails to fetch
            parse_events: Whether to parse emails for events/meetings
        """
        try:
            service = self._get_gmail_service()
            if not service:
                return "Gmail service not available. Please configure Google OAuth."
            
            if action == "read":
                return self._read_emails(service, query, max_emails, parse_events)
            elif action == "search":
                return self._search_emails(service, query, max_emails)
            elif action == "send":
                return self._send_email(service, recipient, subject, body)
            elif action == "parse_events":
                return self._parse_emails_for_events(service, query, max_emails)
            elif action == "summary":
                return self._get_email_summary(service, max_emails)
            else:
                return f"Unknown action: {action}"
                
        except Exception as e:
            return f"Gmail error: {str(e)}"
    
    def _get_gmail_service(self):
        """Authenticate and return Gmail service object"""
        if not GOOGLE_AVAILABLE:
            return None
            
        try:
            creds = None
            
            # Load existing credentials
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', self.scopes)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists('credentials.json'):
                        print("credentials.json not found. Please set up Google OAuth.")
                        return None
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', self.scopes)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next time
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('gmail', 'v1', credentials=creds)
            return self.service
            
        except Exception as e:
            print(f"Gmail authentication error: {e}")
            return None
    
    def _read_emails(self, service, query: str = "", max_emails: int = 10, parse_events: bool = True) -> str:
        """Read recent emails with intelligent parsing"""
        try:
            # Build search query
            search_query = query if query else "in:inbox"
            
            # Get message list
            results = service.users().messages().list(
                userId='me', 
                q=search_query, 
                maxResults=max_emails
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return "No emails found."
            
            email_summaries = []
            potential_events = []
            
            for msg in messages:
                # Get full message
                message = service.users().messages().get(
                    userId='me', 
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Extract email details
                headers = message['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
                
                # Get email body
                body = self._extract_email_body(message['payload'])
                
                email_data = {
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'body': body[:500]  # Truncate for processing
                }
                
                # Parse for events if requested
                if parse_events:
                    event_info = self._parse_email_for_events(email_data)
                    if event_info:
                        potential_events.append(event_info)
                
                # Create summary
                summary = f"From: {sender}\nSubject: {subject}\nDate: {date}"
                if len(body) > 100:
                    summary += f"\nPreview: {body[:100]}..."
                
                email_summaries.append(summary)
            
            result = f"Found {len(messages)} emails:\n\n"
            result += "\n\n".join(email_summaries)
            
            if potential_events:
                result += f"\n\n🗓️ Found {len(potential_events)} potential calendar events:"
                for event in potential_events:
                    result += f"\n- {event['title']} on {event.get('date', 'TBD')}"
                result += "\n\nWould you like me to add any of these to your calendar?"
            
            return result
            
        except Exception as e:
            return f"Error reading emails: {str(e)}"
    
    def _extract_email_body(self, payload):
        """Extract text body from email payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
        elif payload['mimeType'] == 'text/plain':
            data = payload['body']['data']
            body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body
    
    def _parse_email_for_events(self, email_data: Dict) -> Optional[Dict]:
        """Parse email content for potential calendar events using LLM"""
        try:
            # Initialize LLM if not already done
            if not self.llm:
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    return None
                self.llm = ChatOpenAI(model="gpt-4", api_key=api_key, temperature=0.1)
            
            # Create prompt for event extraction
            prompt = f"""
            Analyze this email and extract any meeting, appointment, class, test, or event information.
            
            Subject: {email_data['subject']}
            From: {email_data['sender']}
            Content: {email_data['body']}
            
            If this email contains information about a meeting, appointment, class, test, deadline, or any scheduled event, extract:
            1. Event title/description
            2. Date (if mentioned)
            3. Time (if mentioned)
            4. Location (if mentioned)
            5. Type (meeting, class, test, deadline, etc.)
            
            Respond with JSON format:
            {{
                "has_event": true/false,
                "title": "event title",
                "date": "YYYY-MM-DD or null",
                "time": "HH:MM or null",
                "location": "location or null",
                "type": "meeting/class/test/deadline/other",
                "confidence": 0.0-1.0
            }}
            
            Only extract if confidence > 0.7. Return {{"has_event": false}} if no clear event is found.
            """
            
            response = self.llm.invoke(prompt)
            result = json.loads(response.content)
            
            if result.get("has_event") and result.get("confidence", 0) > 0.7:
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing email for events: {e}")
            return None
    
    def _search_emails(self, service, query: str, max_emails: int = 10) -> str:
        """Search emails with query"""
        try:
            results = service.users().messages().list(
                userId='me', 
                q=query, 
                maxResults=max_emails
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return f"No emails found for query: {query}"
            
            summaries = []
            for msg in messages:
                message = service.users().messages().get(
                    userId='me', 
                    id=msg['id'],
                    format='metadata'
                ).execute()
                
                headers = message['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                
                summaries.append(f"• {subject} (from {sender})")
            
            return f"Found {len(messages)} emails for '{query}':\n" + "\n".join(summaries)
            
        except Exception as e:
            return f"Search error: {str(e)}"
    
    def _send_email(self, service, recipient: str, subject: str, body: str) -> str:
        """Send an email"""
        try:
            # Create message
            message = MIMEText(body)
            message['to'] = recipient
            message['subject'] = subject
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send via API
            service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return f"✅ Email sent to {recipient} with subject: {subject}"
            
        except Exception as e:
            return f"Failed to send email: {str(e)}"
    
    def _parse_emails_for_events(self, service, query: str = "", max_emails: int = 20) -> str:
        """Parse recent emails specifically for events and return structured data"""
        try:
            search_query = query if query else "in:inbox"
            
            results = service.users().messages().list(
                userId='me', 
                q=search_query, 
                maxResults=max_emails
            ).execute()
            
            messages = results.get('messages', [])
            events_found = []
            
            for msg in messages:
                message = service.users().messages().get(
                    userId='me', 
                    id=msg['id'],
                    format='full'
                ).execute()
                
                headers = message['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
                
                body = self._extract_email_body(message['payload'])
                
                event_info = self._parse_email_for_events({
                    'subject': subject,
                    'sender': sender,
                    'body': body
                })
                
                if event_info:
                    event_info['email_subject'] = subject
                    event_info['email_sender'] = sender
                    events_found.append(event_info)
            
            if not events_found:
                return "No events or meetings found in recent emails."
            
            result = f"🗓️ Found {len(events_found)} potential calendar events:\n\n"
            
            for i, event in enumerate(events_found, 1):
                result += f"{i}. **{event['title']}**\n"
                result += f"   Type: {event['type']}\n"
                if event.get('date'):
                    result += f"   Date: {event['date']}\n"
                if event.get('time'):
                    result += f"   Time: {event['time']}\n"
                if event.get('location'):
                    result += f"   Location: {event['location']}\n"
                result += f"   From email: {event['email_subject']}\n"
                result += f"   Confidence: {event['confidence']:.2f}\n\n"
            
            return result
            
        except Exception as e:
            return f"Error parsing emails for events: {str(e)}"
    
    def _get_email_summary(self, service, max_emails: int = 5) -> str:
        """Get a summary of recent emails"""
        try:
            results = service.users().messages().list(
                userId='me', 
                q='in:inbox', 
                maxResults=max_emails
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return "No recent emails found."
            
            summaries = []
            
            for msg in messages:
                message = service.users().messages().get(
                    userId='me', 
                    id=msg['id'],
                    format='full'
                ).execute()
                
                headers = message['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                
                # Extract sender name only (remove email address)
                sender_name = re.sub(r'<.*?>', '', sender).strip()
                
                body = self._extract_email_body(message['payload'])
                
                # Use LLM to create a concise summary
                summary = self._summarize_email_with_llm(subject, sender_name, body[:300])
                summaries.append(f"• {summary}")
            
            return f"📧 Recent Email Summary ({len(summaries)} emails):\n" + "\n".join(summaries)
            
        except Exception as e:
            return f"Error getting email summary: {str(e)}"
    
    def _summarize_email_with_llm(self, subject: str, sender: str, body: str) -> str:
        """Use LLM to create a concise email summary"""
        try:
            if not self.llm:
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    return f"{subject} from {sender}"
                self.llm = ChatOpenAI(model="gpt-4", api_key=api_key, temperature=0.1)
            
            prompt = f"""
            Summarize this email in one clear, concise line:
            
            From: {sender}
            Subject: {subject}
            Content: {body}
            
            Focus on the main point or request. Keep it under 80 characters.
            Format: "From [sender]: [main point]"
            """
            
            response = self.llm.invoke(prompt)
            return response.content.strip()
            
        except Exception as e:
            return f"{subject} from {sender}"

class SmartGoogleCalendarTool(BaseTool):
    """Enhanced Calendar tool with event creation from email parsing"""
    
    name: str = "smart_google_calendar"
    description: str = "Read calendar, create events, and integrate with email parsing results"
    args_schema: Type[BaseModel] = SmartCalendarInput
    
    # Allow extra fields in Pydantic v2
    model_config = ConfigDict(extra='allow')
    
    # Define as class attributes to avoid Pydantic field issues
    scopes: List[str] = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(self):
        super().__init__()
        # These are now allowed as extra fields
        self.service = None
    
    def _run(self, action: str, date: str = "", title: str = "", start_time: str = "", 
             end_time: str = "", description: str = "", location: str = "", 
             event_data: Optional[Dict] = None) -> str:
        """
        Execute Calendar operations with smart event creation
        
        Args:
            action: "read", "create", "check", "create_from_email"
            date: Date (YYYY-MM-DD)
            title: Event title
            start_time: Start time (HH:MM)
            end_time: End time (HH:MM)
            description: Event description
            location: Event location
            event_data: Parsed event data from email
        """
        try:
            service = self._get_calendar_service()
            if not service:
                return "Calendar service not available. Please configure Google OAuth."
            
            if action == "read":
                return self._read_calendar(service, date)
            elif action == "create":
                return self._create_event(service, title, date, start_time, end_time, description, location)
            elif action == "check":
                return self._check_availability(service, date)
            elif action == "create_from_email":
                return self._create_event_from_email_data(service, event_data)
            else:
                return f"Unknown action: {action}"
                
        except Exception as e:
            return f"Calendar error: {str(e)}"
    
    def _get_calendar_service(self):
        """Authenticate and return Calendar service object"""
        if not GOOGLE_AVAILABLE:
            return None
            
        try:
            creds = None
            
            # Load existing credentials
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', self.scopes)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists('credentials.json'):
                        return None
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', self.scopes)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('calendar', 'v3', credentials=creds)
            return self.service
            
        except Exception as e:
            print(f"Calendar authentication error: {e}")
            return None
    
    def _read_calendar(self, service, date: str = "") -> str:
        """Read calendar events for a specific date"""
        try:
            if date:
                start_date = datetime.datetime.strptime(date, "%Y-%m-%d")
            else:
                start_date = datetime.datetime.now()
            
            # Set time range for the day
            start_time = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + datetime.timedelta(days=1)
            
            # Format for API
            start_iso = start_time.isoformat() + 'Z'
            end_iso = end_time.isoformat() + 'Z'
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_iso,
                timeMax=end_iso,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                return f"No events found for {start_date.strftime('%Y-%m-%d')}"
            
            result = f"📅 Events for {start_date.strftime('%A, %B %d, %Y')}:\n\n"
            
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                title = event.get('summary', 'No title')
                location = event.get('location', '')
                
                # Format time
                if 'T' in start:  # DateTime event
                    event_time = datetime.datetime.fromisoformat(start.replace('Z', ''))
                    time_str = event_time.strftime('%I:%M %p')
                else:  # All-day event
                    time_str = "All day"
                
                result += f"• {time_str}: {title}"
                if location:
                    result += f" ({location})"
                result += "\n"
            
            return result
            
        except Exception as e:
            return f"Error reading calendar: {str(e)}"
    
    def _create_event(self, service, title: str, date: str, start_time: str = "", 
                     end_time: str = "", description: str = "", location: str = "") -> str:
        """Create a calendar event"""
        try:
            # Parse date
            event_date = datetime.datetime.strptime(date, "%Y-%m-%d")
            
            # Handle time
            if start_time:
                start_hour, start_min = map(int, start_time.split(':'))
                start_datetime = event_date.replace(hour=start_hour, minute=start_min)
                
                if end_time:
                    end_hour, end_min = map(int, end_time.split(':'))
                    end_datetime = event_date.replace(hour=end_hour, minute=end_min)
                else:
                    # Default to 1 hour duration
                    end_datetime = start_datetime + datetime.timedelta(hours=1)
                
                # Convert to ISO format
                start_iso = start_datetime.isoformat()
                end_iso = end_datetime.isoformat()
                
            else:
                # All-day event
                start_iso = event_date.strftime('%Y-%m-%d')
                end_iso = (event_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            
            # Create event object
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime' if start_time else 'date': start_iso,
                    'timeZone': 'America/New_York' if start_time else None
                },
                'end': {
                    'dateTime' if start_time else 'date': end_iso,
                    'timeZone': 'America/New_York' if start_time else None
                }
            }
            
            if location:
                event['location'] = location
            
            # Create the event
            created_event = service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return f"✅ Created calendar event: {title} on {date}"
            
        except Exception as e:
            return f"Failed to create event: {str(e)}"
    
    def _create_event_from_email_data(self, service, event_data: Optional[Dict]) -> str:
        """Create calendar event from parsed email data"""
        try:
            if not event_data:
                return "No event data provided"
            
            title = event_data.get('title', 'Untitled Event')
            date = event_data.get('date')
            time = event_data.get('time')
            location = event_data.get('location', '')
            event_type = event_data.get('type', 'event')
            
            if not date:
                return f"Cannot create event '{title}' - no date specified"
            
            # Create event
            description = f"Created from email. Type: {event_type}"
            
            return self._create_event(
                service, title, date, time, "", description, location
            )
            
        except Exception as e:
            return f"Failed to create event from email: {str(e)}"
    
    def _check_availability(self, service, date: str) -> str:
        """Check availability for a specific date"""
        try:
            events = self._read_calendar(service, date)
            
            if "No events found" in events:
                return f"✅ You're free all day on {date}"
            else:
                return f"📅 You have events on {date}:\n{events}"
                
        except Exception as e:
            return f"Error checking availability: {str(e)}"

class PythonREPLTool(BaseTool):
    """Tool for executing Python code snippets"""
    
    name: str = "python_repl"
    description: str = "Execute Python code and return the results. Use for calculations, data processing, or quick scripts."
    args_schema: Type[BaseModel] = PythonREPLInput
    
    # Allow extra fields in Pydantic v2
    model_config = ConfigDict(extra='allow')
    
    def _run(self, code: str) -> str:
        """
        Execute Python code in a safe environment
        
        Args:
            code: Python code to execute
        """
        try:
            # Create a safe execution environment
            safe_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'list': list,
                    'dict': dict,
                    'range': range,
                    'sum': sum,
                    'max': max,
                    'min': min,
                    'abs': abs,
                    'round': round,
                    'sorted': sorted,
                    'enumerate': enumerate,
                    'zip': zip,
                    'datetime': datetime,
                    'json': json,
                    'math': __import__('math'),
                    'random': __import__('random'),
                }
            }
            
            safe_locals = {}
            
            # Capture output
            import io
            import sys
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            try:
                # Execute the code
                exec(code, safe_globals, safe_locals)
                output = sys.stdout.getvalue()
                
                # If no output, try to evaluate as expression
                if not output.strip():
                    try:
                        result = eval(code, safe_globals, safe_locals)
                        if result is not None:
                            output = str(result)
                    except:
                        pass
                
                return output.strip() if output.strip() else "Code executed successfully (no output)"
                
            finally:
                sys.stdout = old_stdout
                
        except Exception as e:
            return f"Python execution error: {str(e)}"

class WeatherTool(BaseTool):
    """Tool for fetching weather information"""
    
    name: str = "get_weather"
    description: str = "Get current weather information for a specific location"
    args_schema: Type[BaseModel] = WeatherInput
    
    # Allow extra fields in Pydantic v2
    model_config = ConfigDict(extra='allow')
    
    def _run(self, location: str) -> str:
        """
        Get weather for a location
        
        Args:
            location: City name or "City, Country" format
        """
        try:
            api_key = os.getenv("OPENWEATHER_API_KEY")
            
            if not api_key:
                return "Weather API key not configured. Please set OPENWEATHER_API_KEY environment variable."
            
            # Current weather endpoint
            base_url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": api_key,
                "units": "metric"  # Use Celsius
            }
            
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract weather information
            weather_info = {
                "location": data["name"],
                "country": data["sys"]["country"],
                "temperature": round(data["main"]["temp"], 1),
                "feels_like": round(data["main"]["feels_like"], 1),
                "description": data["weather"][0]["description"].title(),
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "pressure": data["main"]["pressure"]
            }
            
            # Create natural response
            result = (f"🌤️ Weather in {weather_info['location']}, {weather_info['country']}: "
                     f"{weather_info['temperature']}°C (feels like {weather_info['feels_like']}°C). "
                     f"{weather_info['description']}. "
                     f"Humidity {weather_info['humidity']}%, "
                     f"wind {weather_info['wind_speed']} m/s.")
            
            return result
            
        except requests.exceptions.Timeout:
            return f"Weather request timed out for {location}. Please try again."
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return f"Location '{location}' not found. Please check the spelling."
            else:
                return f"Weather API error: {e.response.status_code}"
        except requests.RequestException as e:
            return f"Weather API connection error: {str(e)}"
        except KeyError as e:
            return f"Weather data parsing error - missing field: {str(e)}"
        except Exception as e:
            return f"Weather error: {str(e)}"

class TimeTool(BaseTool):
    """Tool for getting current time information"""
    
    name: str = "get_time"
    description: str = "Get current local time or time in a specific timezone"
    args_schema: Type[BaseModel] = TimeInput
    
    # Allow extra fields in Pydantic v2
    model_config = ConfigDict(extra='allow')
    
    def _run(self, timezone: str = "local") -> str:
        """
        Get current time
        
        Args:
            timezone: Timezone name (e.g., "US/Eastern", "Europe/London") or "local"
        """
        try:
            if timezone.lower() == "local":
                now = datetime.datetime.now()
                tz_name = "local time"
            else:
                tz = pytz.timezone(timezone)
                now = datetime.datetime.now(tz)
                tz_name = timezone
            
            formatted_time = now.strftime("%A, %B %d, %Y at %I:%M:%S %p")
            return f"Current {tz_name}: {formatted_time}"
            
        except pytz.exceptions.UnknownTimeZoneError:
            return f"Unknown timezone: {timezone}. Please use a valid timezone name."
        except Exception as e:
            return f"Time error: {str(e)}"

class MemoryTool(BaseTool):
    """Tool for managing conversation memory"""
    
    name: str = "memory"
    description: str = "Store or retrieve information from conversation memory"
    args_schema: Type[BaseModel] = MemoryInput
    
    # Allow extra fields in Pydantic v2
    model_config = ConfigDict(extra='allow')
    
    def __init__(self):
        super().__init__()
        # These are now allowed as extra fields
        self.memory_file = "conversation_memory.json"
        self.memory_data = self._load_memory()
    
    def _run(self, action: str, key: str = "", value: str = "", query: str = "") -> str:
        """
        Memory operations
        
        Args:
            action: "store", "retrieve", "search", or "list"
            key: Memory key (for store/retrieve)
            value: Value to store (for store)
            query: Search query (for search)
        """
        try:
            if action == "store":
                return self._store_memory(key, value)
            elif action == "retrieve":
                return self._retrieve_memory(key)
            elif action == "search":
                return self._search_memory(query)
            elif action == "list":
                return self._list_memory()
            else:
                return f"Unknown memory action: {action}"
                
        except Exception as e:
            return f"Memory error: {str(e)}"
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def _save_memory(self):
        """Save memory to file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory_data, f, indent=2)
        except Exception as e:
            print(f"Failed to save memory: {e}")
    
    def _store_memory(self, key: str, value: str) -> str:
        """Store a key-value pair in memory"""
        self.memory_data[key] = {
            "value": value,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self._save_memory()
        return f"Stored in memory: {key} = {value}"
    
    def _retrieve_memory(self, key: str) -> str:
        """Retrieve a value from memory"""
        if key in self.memory_data:
            item = self.memory_data[key]
            return f"Retrieved from memory: {key} = {item['value']} (stored: {item['timestamp']})"
        else:
            return f"No memory found for key: {key}"
    
    def _search_memory(self, query: str) -> str:
        """Search memory for keys or values containing the query"""
        results = []
        query_lower = query.lower()
        
        for key, item in self.memory_data.items():
            if (query_lower in key.lower() or 
                query_lower in str(item['value']).lower()):
                results.append(f"{key}: {item['value']}")
        
        if results:
            return f"Memory search results for '{query}':\n" + "\n".join(results)
        else:
            return f"No memory entries found for '{query}'"
    
    def _list_memory(self) -> str:
        """List all memory entries"""
        if not self.memory_data:
            return "No memory entries found."
        
        entries = []
        for key, item in self.memory_data.items():
            entries.append(f"{key}: {item['value']}")
        
        return "Memory entries:\n" + "\n".join(entries)

def get_all_tools():
    """Return a list of all available tools"""
    return [
        SmartGmailTool(),
        SmartGoogleCalendarTool(),
        PythonREPLTool(),
        WeatherTool(),
        TimeTool(),
        MemoryTool()
    ]

def get_tools_for_realtime():
    """Convert LangChain tools to OpenAI Realtime API format"""
    tools = []
    
    # Smart Gmail tool
    tools.append({
        "type": "function",
        "name": "smart_gmail",
        "description": "Read emails, parse for events/meetings, send emails, and suggest calendar entries",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["read", "search", "send", "parse_events", "summary"]},
                "query": {"type": "string", "description": "Search query for emails"},
                "recipient": {"type": "string", "description": "Email recipient"},
                "subject": {"type": "string", "description": "Email subject"},
                "body": {"type": "string", "description": "Email body"},
                "max_emails": {"type": "integer", "description": "Maximum emails to fetch", "default": 10},
                "parse_events": {"type": "boolean", "description": "Parse emails for events", "default": True}
            },
            "required": ["action"]
        }
    })
    
    # Smart Calendar tool
    tools.append({
        "type": "function",
        "name": "smart_google_calendar",
        "description": "Read calendar, create events, and integrate with email parsing results",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["read", "create", "check", "create_from_email"]},
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                "title": {"type": "string", "description": "Event title"},
                "start_time": {"type": "string", "description": "Start time (HH:MM)"},
                "end_time": {"type": "string", "description": "End time (HH:MM)"},
                "description": {"type": "string", "description": "Event description"},
                "location": {"type": "string", "description": "Event location"},
                "event_data": {"type": "object", "description": "Parsed event data from email"}
            },
            "required": ["action"]
        }
    })
    
    tools.append({
        "type": "function",
        "name": "python_repl",
        "description": "Execute Python code and return results",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code to execute"}
            },
            "required": ["code"]
        }
    })
    
    tools.append({
        "type": "function",
        "name": "get_weather",
        "description": "Get current weather information for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Location to get weather for"}
            },
            "required": ["location"]
        }
    })
    
    tools.append({
        "type": "function",
        "name": "get_time",
        "description": "Get current time in local or specified timezone",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {"type": "string", "description": "Timezone or 'local'", "default": "local"}
            }
        }
    })
    
    tools.append({
        "type": "function",
        "name": "memory",
        "description": "Store or retrieve information from conversation memory",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["store", "retrieve", "search", "list"]},
                "key": {"type": "string", "description": "Memory key"},
                "value": {"type": "string", "description": "Value to store"},
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["action"]
        }
    })
    
    return tools
