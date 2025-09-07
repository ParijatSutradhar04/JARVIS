#!/usr/bin/env python3
"""
Test script to verify Gmail API setup for JARVIS
"""

import os
import sys
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    print("🔍 Checking requirements...")
    
    try:
        import google.auth
        import google.auth.transport.requests
        import google_auth_oauthlib.flow
        import googleapiclient.discovery
        print("✅ Google API packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please install: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        return False

def check_credentials():
    """Check if credentials.json exists"""
    print("\n📁 Checking credentials file...")
    
    creds_path = Path("credentials.json")
    if creds_path.exists():
        print("✅ credentials.json found")
        return True
    else:
        print("❌ credentials.json not found")
        print("Please download it from Google Cloud Console and place it in this directory")
        return False

def test_gmail_import():
    """Test if tools can be imported"""
    print("\n📦 Testing tool imports...")
    
    try:
        from tools import SmartGmailTool
        print("✅ SmartGmailTool imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_gmail_connection():
    """Test Gmail API connection"""
    print("\n📧 Testing Gmail API connection...")
    
    try:
        from tools import SmartGmailTool
        
        gmail_tool = SmartGmailTool()
        
        print("🔐 Attempting Gmail authentication...")
        print("(A browser window may open for authorization)")
        
        # Test with a simple read operation
        result = gmail_tool._run(
            action="read",
            max_emails=3
        )
        
        print("✅ Gmail API connection successful!")
        print("\n📨 Sample of recent emails:")
        print("-" * 50)
        # Show first 300 characters
        sample = result[:300] + "..." if len(result) > 300 else result
        print(sample)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Gmail API error: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure you downloaded credentials.json from Google Cloud Console")
        print("2. Check that Gmail API is enabled in your Google Cloud project")
        print("3. Verify OAuth consent screen is configured")
        print("4. If you get a redirect_uri_mismatch error, make sure you selected 'Desktop application'")
        return False

def main():
    """Run all tests"""
    print("🤖 JARVIS Gmail Setup Test")
    print("=" * 40)
    
    all_passed = True
    
    # Run all checks
    if not check_requirements():
        all_passed = False
    
    if not check_credentials():
        all_passed = False
    
    if not test_gmail_import():
        all_passed = False
    
    if all_passed:
        if not test_gmail_connection():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("Gmail is ready to use with JARVIS!")
        print("\nYou can now ask JARVIS:")
        print("• 'Read my recent emails'")
        print("• 'Send an email to someone'")
        print("• 'Check for meeting invitations'")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please follow the setup guide to fix the issues.")
        print("See GMAIL_SETUP_GUIDE.md for detailed instructions.")

if __name__ == "__main__":
    main()
