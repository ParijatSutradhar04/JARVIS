# JARVIS Voice AI Agent - File Structure

## Core Files
- `main.py` - Main entry point (simplified, focuses on voice mode)  
- `voice_start.py` - Quick voice mode launcher (for testing)
- `agent.py` - Main agent class with LangChain integration
- `realtime_client.py` - OpenAI Realtime API client
- `tools.py` - LangChain tools (Gmail, Calendar, Weather, etc.)

## Configuration & Setup
- `.env` - Environment variables (API keys)
- `.env.example` - Example environment file
- `credentials.json` - Google OAuth credentials (user-provided)
- `token.json` - Google OAuth tokens (auto-generated)

## Installation & Documentation  
- `install.py` - Dependency installer
- `install_windows.py` - Windows-specific installer
- `requirements.txt` - Python dependencies
- `requirements_windows.txt` - Windows-specific dependencies
- `setup.py` - Package setup configuration
- `GMAIL_SETUP_GUIDE.md` - Complete Gmail/Calendar setup guide
- `README.md` - Main project documentation

## Integration & Testing
- `email_calendar_integration.py` - Email-Calendar integration logic
- `test_gmail_calendar_setup.py` - Unified Gmail & Calendar test

## Usage

### Voice Mode (Primary)
```bash
python main.py
# or for quick testing
python voice_start.py
```

### Test Gmail & Calendar Setup  
```bash  
python test_gmail_calendar_setup.py
```

### Install Dependencies
```bash
python install.py
```

## Cleaned Up (Removed)
- ❌ All old test files and debug scripts
- ❌ Duplicate realtime client versions
- ❌ Old configuration and setup files
- ❌ Audio test files  
- ❌ Diagnostic and connectivity test files

The project is now clean and focused on the core voice AI functionality.
