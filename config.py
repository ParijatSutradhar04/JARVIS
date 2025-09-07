"""
Configuration and setup utilities for JARVIS
"""

import os
import json
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class Config:
    """Configuration management for JARVIS"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
        self.google_credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
        self.voice_mode = os.getenv("VOICE_MODE", "true").lower() == "true"
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        
        # Audio settings
        self.sample_rate = int(os.getenv("SAMPLE_RATE", "24000"))
        self.channels = int(os.getenv("CHANNELS", "1"))
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1024"))
        
        # Agent settings
        self.max_iterations = int(os.getenv("MAX_ITERATIONS", "3"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
    def validate(self) -> tuple[bool, list[str]]:
        """Validate configuration and return (is_valid, missing_keys)"""
        missing = []
        
        if not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        
        return len(missing) == 0, missing
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "openai_api_key": "***" if self.openai_api_key else None,
            "openweather_api_key": "***" if self.openweather_api_key else None,
            "google_credentials_file": self.google_credentials_file,
            "voice_mode": self.voice_mode,
            "debug_mode": self.debug_mode,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "chunk_size": self.chunk_size,
            "max_iterations": self.max_iterations,
            "temperature": self.temperature
        }

def setup_logging(debug_mode: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if debug_mode else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('jarvis.log')
        ]
    )

def check_dependencies():
    """Check if all required dependencies are available"""
    dependencies = {
        "openai": "OpenAI API client",
        "langchain": "LangChain framework",
        "pyaudio": "Audio processing",
        "websockets": "WebSocket communication",
        "requests": "HTTP requests",
        "python-dotenv": "Environment variables"
    }
    
    missing = []
    for package, description in dependencies.items():
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append((package, description))
    
    if missing:
        print("❌ Missing dependencies:")
        for package, description in missing:
            print(f"   - {package}: {description}")
        print("\nInstall missing packages with: pip install -r requirements.txt")
        return False
    
    return True
