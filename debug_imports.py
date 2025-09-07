"""
Simple debug script to identify the hanging issue
"""

print("1. Starting debug...")

try:
    print("2. Importing basic modules...")
    import os
    import sys
    print("3. Basic imports OK")
    
    print("4. Testing tools import...")
    from tools import get_all_tools
    print("5. Tools import OK")
    
    print("6. Creating tools...")
    tools = get_all_tools()
    print(f"7. Created {len(tools)} tools")
    
    print("8. Testing agent import...")
    from agent import VoiceAgent
    print("9. Agent import OK")
    
    print("10. All imports successful!")
    
except Exception as e:
    print(f"ERROR at step: {e}")
    import traceback
    traceback.print_exc()
