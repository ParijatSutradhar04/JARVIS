"""
Network and API Access Diagnosis Script
"""
import subprocess
import socket
import os
from dotenv import load_dotenv

load_dotenv()

def test_dns_resolution():
    """Test if we can resolve OpenAI domain"""
    print("🔍 Testing DNS resolution...")
    try:
        ip = socket.gethostbyname("api.openai.com")
        print(f"✅ api.openai.com resolves to {ip}")
        return True
    except Exception as e:
        print(f"❌ DNS resolution failed: {e}")
        return False

def test_port_connectivity():
    """Test if we can connect to OpenAI ports"""
    print("🔍 Testing port connectivity...")
    
    # Test HTTPS port (443)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(("api.openai.com", 443))
        sock.close()
        
        if result == 0:
            print("✅ Port 443 (HTTPS) is accessible")
            return True
        else:
            print("❌ Port 443 (HTTPS) is blocked or unreachable")
            return False
    except Exception as e:
        print(f"❌ Port test failed: {e}")
        return False

def test_websocket_port():
    """Test WebSocket port connectivity"""
    print("🔍 Testing WebSocket port connectivity...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(("api.openai.com", 443))  # WSS uses 443
        sock.close()
        
        if result == 0:
            print("✅ WebSocket port (443) is accessible")
            return True
        else:
            print("❌ WebSocket port (443) is blocked")
            return False
    except Exception as e:
        print(f"❌ WebSocket port test failed: {e}")
        return False

def check_proxy_settings():
    """Check if there are proxy settings that might interfere"""
    print("🔍 Checking proxy settings...")
    
    # Check environment variables
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY']
    proxy_found = False
    
    for var in proxy_vars:
        value = os.environ.get(var) or os.environ.get(var.lower())
        if value:
            print(f"⚠️ Proxy setting found: {var}={value}")
            proxy_found = True
    
    if not proxy_found:
        print("✅ No proxy environment variables found")
    
    return not proxy_found

def test_curl_equivalent():
    """Test with curl if available"""
    print("🔍 Testing with curl (if available)...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    try:
        # Try to use curl to test the API
        curl_cmd = [
            'curl',
            '-X', 'POST',
            'https://api.openai.com/v1/models',
            '-H', f'Authorization: Bearer {api_key}',
            '-H', 'Content-Type: application/json',
            '--timeout', '10',
            '--max-time', '10'
        ]
        
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ curl request successful")
            # Check if we get models back
            if 'gpt' in result.stdout:
                print("✅ API is responding with model data")
                return True
            else:
                print(f"⚠️ Unexpected response: {result.stdout[:200]}...")
        else:
            print(f"❌ curl failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ curl request timed out")
    except FileNotFoundError:
        print("⚠️ curl not available")
    except Exception as e:
        print(f"❌ curl test failed: {e}")
    
    return False

def main():
    print("🔍 Network and API Access Diagnosis")
    print("=" * 50)
    
    tests = [
        ("DNS Resolution", test_dns_resolution),
        ("Port Connectivity", test_port_connectivity), 
        ("WebSocket Port", test_websocket_port),
        ("Proxy Settings", check_proxy_settings),
        ("Curl Test", test_curl_equivalent)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 DIAGNOSIS SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print("\n🔍 LIKELY ISSUES:")
    if not all_passed:
        print("Based on the failed tests above, you likely have:")
        failed_tests = [name for name, result in results if not result]
        
        if "DNS Resolution" in failed_tests:
            print("• DNS/Network connectivity issues")
        if "Port Connectivity" in failed_tests or "WebSocket Port" in failed_tests:
            print("• Firewall blocking OpenAI connections")
        if not results[3][1]:  # Proxy check failed (found proxies)
            print("• Proxy server interfering with connections")
        if "Curl Test" in failed_tests:
            print("• API access issues or regional restrictions")
            
        print("\n💡 SUGGESTED SOLUTIONS:")
        print("1. Check your internet connection")
        print("2. Temporarily disable firewall/antivirus")
        print("3. Try connecting from a different network")
        print("4. Contact your IT department if on corporate network")
        print("5. Verify your OpenAI account has Realtime API access")
    else:
        print("✅ All network tests passed!")
        print("The issue might be:")
        print("• Realtime API not available in your region")
        print("• Your API key doesn't have Realtime API access") 
        print("• Rate limiting or temporary API issues")

if __name__ == "__main__":
    main()
