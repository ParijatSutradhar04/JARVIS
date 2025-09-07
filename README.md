# JARVIS Voice AI Agent

A voice-first AI agent that behaves like ChatGPT Live using OpenAI's GPT-4o-realtime API, integrated with LangChain for tool orchestration.

## Features

🎤 **Voice Realtime Interaction**
- Full-duplex audio using OpenAI Realtime API
- Real-time microphone input and audio playback
- Fallback to text input/output for debugging

🔧 **Integrated Tools**
- 📧 Gmail (read/send emails)
- 📅 Google Calendar (schedule management)
- 🐍 Python REPL (code execution)
- 🌤️ Weather (OpenWeatherMap integration)
- 🕐 Time (timezone-aware)
- 🧠 Memory (conversation persistence)

⚡ **LangChain Integration**
- Tool orchestration and agent management
- Conversation memory across sessions
- Robust error handling and fallbacks

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file (or update the generated one):

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional but recommended
OPENWEATHER_API_KEY=your_openweather_api_key_here

# For Gmail/Calendar (requires OAuth setup)
GOOGLE_CREDENTIALS_FILE=credentials.json
```

### 3. Run JARVIS

```bash
python main.py
```

## Project Structure

```
JARVIS/
├── main.py              # Main orchestration and entry point
├── agent.py             # LangChain agent with Realtime integration
├── realtime_client.py   # OpenAI Realtime API client
├── tools.py             # LangChain tool implementations
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
└── README.md           # This file
```

## Configuration

### OpenAI API Key
1. Get your API key from https://platform.openai.com/api-keys
2. Add it to your `.env` file as `OPENAI_API_KEY`

### Weather API (Optional)
1. Sign up at https://openweathermap.org/api
2. Get your free API key
3. Add it to your `.env` file as `OPENWEATHER_API_KEY`

### Google APIs (Gmail/Calendar) - TODO
1. Go to Google Cloud Console
2. Create a new project or select existing
3. Enable Gmail API and Calendar API
4. Create OAuth 2.0 credentials
5. Download the credentials JSON file as `credentials.json`

## Usage Modes

### Voice Mode
- Real-time voice conversation
- Speak naturally to interact with JARVIS
- Audio responses played back in real-time

### Text Mode
- Terminal-based chat interface
- Type messages and receive text responses
- Good for debugging and development

### Test Mode
- Interactive tool testing
- Test individual tools before using in conversation
- Useful for development and troubleshooting

## Development Status

### ✅ Completed
- Project structure and scaffolding
- Basic LangChain agent setup
- Tool interfaces (stubs)
- Text mode conversation
- Python REPL tool
- Time and Memory tools
- Configuration management

### 🚧 In Progress / TODO
- OpenAI Realtime API WebSocket implementation
- Audio streaming and processing
- Google OAuth2 authentication flow
- Gmail and Calendar API integration
- Weather API implementation
- Vector database memory (Chroma/Pinecone)

### 🎯 Stretch Goals
- Multi-turn task planning
- External action confirmations
- Voice activity detection improvements
- Custom wake word detection
- Integration with more services

## Troubleshooting

### Audio Issues
- Ensure microphone permissions are granted
- Check PyAudio installation: `pip install pyaudio`
- On Windows, may need to install Visual C++ Build Tools

### API Issues
- Verify API keys are correctly set in `.env`
- Check internet connectivity
- Ensure APIs are enabled in respective dashboards

### Google API Setup
- Follow Google's OAuth2 setup guide
- Ensure correct scopes are requested
- Handle token refresh properly

## Contributing

This is an MVP implementation. Areas for improvement:
1. Robust error handling
2. Better audio processing
3. Enhanced memory management
4. Additional tool integrations
5. Performance optimizations

## License

MIT License - Feel free to use and modify as needed.
