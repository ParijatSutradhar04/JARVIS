#!/usr/bin/env python3
"""
Test script to verify Gmail + Calendar API setup with unified authentication
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

def test_unified_auth():
    """Test unified Gmail + Calendar authentication"""
    print("\n🔐 Testing unified Gmail + Calendar authentication...")
    
    try:
        from tools import SmartGmailTool, SmartGoogleCalendarTool
        
        print("📧 Testing Gmail authentication...")
        gmail_tool = SmartGmailTool()
        
        # Test Gmail with simple read
        gmail_result = gmail_tool._run(
            action="read",
            max_emails=2
        )
        
        if "error" not in gmail_result.lower():
            print("✅ Gmail authentication successful!")
            print("📨 Sample Gmail result:")
            print("-" * 30)
            print(gmail_result[:200] + "..." if len(gmail_result) > 200 else gmail_result)
            print("-" * 30)
        else:
            print("❌ Gmail authentication failed")
            return False
        
        print("\n📅 Testing Calendar authentication...")
        calendar_tool = SmartGoogleCalendarTool()
        
        # Test Calendar with simple read
        calendar_result = calendar_tool._run(
            action="read"
        )
        
        if "error" not in calendar_result.lower():
            print("✅ Calendar authentication successful!")
            print("📅 Sample Calendar result:")
            print("-" * 30)
            print(calendar_result[:200] + "..." if len(calendar_result) > 200 else calendar_result)
            print("-" * 30)
        else:
            print("❌ Calendar authentication failed")
            return False
        
        # Test creating a calendar event
        print("\n📅 Testing Calendar event creation...")
        create_result = calendar_tool._run(
            action="create",
            title="Test Event from JARVIS",
            date="2025-09-10",
            start_time="10:00",
            end_time="11:00",
            description="This is a test event created by JARVIS"
        )
        
        if "created successfully" in create_result.lower() or "created" in create_result.lower():
            print("✅ Calendar event creation successful!")
            print(f"📅 Event result: {create_result}")
        else:
            print("⚠️ Calendar event creation may have issues:")
            print(f"📅 Result: {create_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Make sure you've added calendar scopes to OAuth consent screen")
        print("2. Delete token.json and re-authenticate")
        print("3. Check that both Gmail API and Calendar API are enabled")
        return False

def main():
    """Run all tests"""
    print("🤖 JARVIS Gmail + Calendar Setup Test")
    print("=" * 45)
    
    all_passed = True
    
    # Run all checks
    if not check_requirements():
        all_passed = False
        return
    
    if not check_credentials():
        all_passed = False
        return
    
    if all_passed:
        if not test_unified_auth():
            all_passed = False
    
    print("\n" + "=" * 45)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("Gmail and Calendar are ready to use with JARVIS!")
        print("\nYou can now ask JARVIS:")
        print("• 'Read my recent emails'")
        print("• 'Create a meeting for tomorrow at 2 PM'")
        print("• 'Check my calendar for today'")
        print("• 'Send an email and add it to my calendar'")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please follow the troubleshooting steps below.")

    print("\n🔧 OAuth Consent Screen Setup:")
    print("1. Go to Google Cloud Console → APIs & Services → OAuth consent screen")
    print("2. Add these scopes:")
    print("   • https://www.googleapis.com/auth/gmail.readonly")
    print("   • https://www.googleapis.com/auth/gmail.send") 
    print("   • https://www.googleapis.com/auth/gmail.modify")
    print("   • https://www.googleapis.com/auth/calendar.readonly")
    print("   • https://www.googleapis.com/auth/calendar.events")
    print("3. Add yourself as a test user")
    print("4. Save and run this test again")

if __name__ == "__main__":
    main()
