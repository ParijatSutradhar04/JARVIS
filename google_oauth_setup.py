"""
Google OAuth Setup Helper
Assists with setting up Gmail and Calendar API authentication
"""

import os
import json
import webbrowser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

class GoogleOAuthSetup:
    """Helper class for Google OAuth2 setup"""
    
    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/calendar.events'
        ]
        self.credentials_file = 'credentials.json'
        self.token_file = 'token.json'
    
    def setup_oauth(self):
        """Interactive OAuth setup"""
        print("🔐 Google OAuth Setup for Gmail & Calendar")
        print("=" * 50)
        
        # Check if credentials file exists
        if not os.path.exists(self.credentials_file):
            print("❌ credentials.json not found")
            print("\nTo set up Google API access:")
            print("1. Go to: https://console.cloud.google.com")
            print("2. Create a new project or select existing")
            print("3. Enable Gmail API and Calendar API")
            print("4. Go to 'Credentials' > 'Create Credentials' > 'OAuth 2.0 Client IDs'")
            print("5. Choose 'Desktop Application'")
            print("6. Download the JSON file and save as 'credentials.json'")
            
            open_console = input("\nOpen Google Cloud Console? (y/n): ").lower().strip()
            if open_console == 'y':
                webbrowser.open("https://console.cloud.google.com")
            
            input("\nPress Enter when you've saved credentials.json...")
            
            if not os.path.exists(self.credentials_file):
                print("❌ credentials.json still not found. Cannot continue.")
                return False
        
        # Authenticate
        try:
            print("🔄 Starting OAuth flow...")
            
            creds = None
            
            # Load existing token
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    print("🔄 Refreshing expired credentials...")
                    creds.refresh(Request())
                else:
                    print("🌐 Opening browser for OAuth authorization...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.scopes)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next time
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
            
            print("✅ Google OAuth setup complete!")
            print(f"✅ Token saved to {self.token_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ OAuth setup failed: {e}")
            return False
    
    def test_authentication(self):
        """Test that authentication is working"""
        try:
            from googleapiclient.discovery import build
            
            # Load credentials
            if not os.path.exists(self.token_file):
                print("❌ No authentication token found. Run setup first.")
                return False
            
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
            
            if not creds.valid:
                print("❌ Credentials are not valid")
                return False
            
            # Test Gmail API
            print("🧪 Testing Gmail API...")
            gmail_service = build('gmail', 'v1', credentials=creds)
            profile = gmail_service.users().getProfile(userId='me').execute()
            print(f"   ✅ Gmail: {profile['emailAddress']}")
            
            # Test Calendar API
            print("🧪 Testing Calendar API...")
            calendar_service = build('calendar', 'v3', credentials=creds)
            calendars = calendar_service.calendarList().list().execute()
            print(f"   ✅ Calendar: Found {len(calendars['items'])} calendars")
            
            print("✅ Google APIs authentication working!")
            return True
            
        except Exception as e:
            print(f"❌ Authentication test failed: {e}")
            return False
    
    def revoke_access(self):
        """Revoke OAuth access and remove tokens"""
        try:
            # Remove token file
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
                print(f"✅ Removed {self.token_file}")
            
            print("✅ OAuth access revoked")
            print("You'll need to re-authenticate next time you use Gmail/Calendar features")
            
        except Exception as e:
            print(f"❌ Error revoking access: {e}")

def main():
    """Main function for OAuth setup"""
    print("🔐 Google OAuth Setup for JARVIS")
    print("=" * 40)
    
    setup = GoogleOAuthSetup()
    
    print("Choose an option:")
    print("1. 🔧 Set up OAuth (first time)")
    print("2. 🧪 Test existing authentication")
    print("3. 🗑️ Revoke access")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        success = setup.setup_oauth()
        if success:
            setup.test_authentication()
    elif choice == "2":
        setup.test_authentication()
    elif choice == "3":
        setup.revoke_access()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
