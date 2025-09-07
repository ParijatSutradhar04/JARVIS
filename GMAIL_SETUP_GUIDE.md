# Gmail API Setup Guide for JARVIS

This guide will help you set up Gmail API credentials to enable email functionality in JARVIS.

## Prerequisites

First, ensure you have the required packages installed:
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Create Project" or select an existing project
3. Name your project (e.g., "JARVIS-Assistant")
4. Click "Create"

## Step 2: Enable Gmail API

1. In your Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Gmail API"
3. Click on "Gmail API" and click "Enable"
4. Also enable "Google Calendar API" for calendar functionality

## Step 3: Create Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Fill in app name: "JARVIS Assistant"
   - Add your email as a developer
   - Add scopes:
     - `https://www.googleapis.com/auth/gmail.readonly`
     - `https://www.googleapis.com/auth/gmail.send`
     - `https://www.googleapis.com/auth/gmail.modify`
     - `https://www.googleapis.com/auth/calendar.readonly`
     - `https://www.googleapis.com/auth/calendar.events`
4. For Application type, choose "Desktop application"
5. Name it "JARVIS Desktop Client"
6. Click "Create"

## Step 4: Download Credentials

1. Click the download button for your newly created OAuth 2.0 Client ID
2. Save the file as `credentials.json` in your JARVIS project directory: `C:\Users\parij\JARVIS\credentials.json`

## Step 5: Required File Structure

Your JARVIS directory should have:
```
C:\Users\parij\JARVIS\
├── credentials.json      (OAuth credentials - you download this)
├── token.json           (Generated after first auth - auto-created)
├── tools.py
├── agent.py
├── voice_start.py
└── ... (other files)
```

## Step 6: Test Gmail Setup

Create a test script to verify your Gmail setup:

```python
# test_gmail_setup.py
import os
from tools import SmartGmailTool

def test_gmail():
    print("Testing Gmail API setup...")
    
    try:
        gmail_tool = SmartGmailTool()
        
        # Test reading recent emails
        result = gmail_tool._run(
            action="read",
            max_emails=5
        )
        
        print("✅ Gmail API working!")
        print("Recent emails:")
        print(result[:500] + "..." if len(result) > 500 else result)
        
    except Exception as e:
        print(f"❌ Gmail setup error: {e}")
        print("\nTroubleshooting:")
        print("1. Check if credentials.json exists")
        print("2. Make sure Gmail API is enabled")
        print("3. Check OAuth consent screen configuration")

if __name__ == "__main__":
    test_gmail()
```

## Step 7: First-Time Authentication

1. Run the test script: `python test_gmail_setup.py`
2. A browser window will open for Gmail authorization
3. Sign in to your Google account
4. Grant permissions to your JARVIS app
5. The browser will show "The authentication flow has completed"
6. A `token.json` file will be created automatically

## Troubleshooting

### Common Issues:

1. **"File credentials.json not found"**
   - Download the credentials file from Google Cloud Console
   - Make sure it's named exactly `credentials.json`

2. **"Access blocked: This app's request is invalid"**
   - Configure the OAuth consent screen properly
   - Add your email as a test user
   - Make sure Gmail API is enabled

3. **"insufficient authentication scopes"**
   - Delete `token.json` and re-authenticate
   - Make sure all required scopes are configured

4. **"The user does not have sufficient permissions"**
   - Check OAuth consent screen scopes
   - Make sure you're using the correct Google account

### Security Notes:

- Keep `credentials.json` and `token.json` private
- Don't commit these files to version control
- The app will be in "testing" mode initially (limited to 100 users)

## Usage in JARVIS

Once set up, you can ask JARVIS:
- "Read my recent emails"
- "Send an email to [email] with subject [subject]"
- "Check my emails for meeting invitations"
- "Summarize my emails from today"

The Gmail functionality will now work with your voice commands!
