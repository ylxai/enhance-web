#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test API Endpoints - Find Correct Upload Endpoint
================================================

Script untuk test berbagai endpoint API dan find yang benar untuk upload.
"""

import requests
import time
from pathlib import Path

def test_endpoints():
    """Test berbagai kemungkinan endpoint"""
    
    base_url = "http://74.63.10.103:3000"
    
    # Daftar endpoint yang mungkin ada
    test_endpoints = [
        "/api/ping",
        "/api/health", 
        "/api/photos",
        "/api/admin/photos",
        "/api/admin/photos/homepage",
        "/api/events",
        "/api/admin/events",
        "/api/slideshow",
        "/api/admin/slideshow",
        "/api/pricing-packages",
        "/api/admin/pricing-packages"
    ]
    
    print("🔍 TESTING API ENDPOINTS")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    print()
    
    working_endpoints = []
    
    for endpoint in test_endpoints:
        url = base_url + endpoint
        
        try:
            print(f"Testing: {endpoint:30} ... ", end="", flush=True)
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ 200 OK")
                working_endpoints.append(endpoint)
            elif response.status_code == 404:
                print(f"❌ 404 Not Found")
            elif response.status_code == 401:
                print(f"🔐 401 Unauthorized (endpoint exists)")
                working_endpoints.append(f"{endpoint} (needs auth)")
            elif response.status_code == 403:
                print(f"🔐 403 Forbidden (endpoint exists)")
                working_endpoints.append(f"{endpoint} (needs auth)")
            elif response.status_code == 405:
                print(f"⚠️ 405 Method Not Allowed (try POST)")
                working_endpoints.append(f"{endpoint} (try POST)")
            else:
                print(f"❓ {response.status_code}")
                working_endpoints.append(f"{endpoint} ({response.status_code})")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Error")
        except requests.exceptions.Timeout:
            print(f"❌ Timeout")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print()
    print("📊 SUMMARY")
    print("-" * 30)
    
    if working_endpoints:
        print("✅ Working/Existing endpoints:")
        for endpoint in working_endpoints:
            print(f"  {endpoint}")
    else:
        print("❌ No working endpoints found")
    
    print()
    
    # Test specific photo upload endpoints
    print("🔍 TESTING PHOTO UPLOAD ENDPOINTS")
    print("-" * 40)
    
    photo_endpoints = [
        "/api/photos",
        "/api/admin/photos", 
        "/api/admin/photos/homepage",
        "/api/upload",
        "/api/admin/upload",
        "/api/photo/upload",
        "/api/admin/photo/upload"
    ]
    
    for endpoint in photo_endpoints:
        url = base_url + endpoint
        
        try:
            print(f"POST {endpoint:25} ... ", end="", flush=True)
            
            # Test with minimal POST data
            response = requests.post(url, 
                json={"test": "data"}, 
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ 200 OK")
            elif response.status_code == 404:
                print(f"❌ 404 Not Found")
            elif response.status_code == 401:
                print(f"🔐 401 Unauthorized (endpoint exists)")
            elif response.status_code == 403:
                print(f"🔐 403 Forbidden (endpoint exists)")
            elif response.status_code == 400:
                print(f"⚠️ 400 Bad Request (endpoint exists, wrong data)")
            elif response.status_code == 422:
                print(f"⚠️ 422 Validation Error (endpoint exists)")
            else:
                print(f"❓ {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Error")
        except Exception as e:
            print(f"❌ Error: {str(e)[:30]}")

def test_web_server():
    """Test apakah web server running"""
    
    print("\n🌐 TESTING WEB SERVER")
    print("-" * 30)
    
    base_url = "http://74.63.10.103:3000"
    
    try:
        print(f"Testing base URL: {base_url}")
        response = requests.get(base_url, timeout=10)
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            print("✅ Web server is running")
            
            # Check if it's Next.js
            if 'text/html' in response.headers.get('content-type', ''):
                content = response.text[:500]
                if 'Next.js' in content or '_next' in content:
                    print("🔍 Detected: Next.js application")
                else:
                    print("🔍 Detected: HTML application (unknown framework)")
            
        else:
            print(f"⚠️ Web server responding with {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to web server")
        print("💡 Check if web server is running on port 3000")
    except Exception as e:
        print(f"❌ Error: {e}")

def suggest_fixes():
    """Suggest possible fixes"""
    
    print("\n💡 POSSIBLE FIXES")
    print("-" * 30)
    
    print("1. 🔍 Check correct endpoint in your web project:")
    print("   - Look for /api/photos route handler")
    print("   - Check /api/admin/photos if auth required")
    print("   - Look for /api/upload alternative")
    
    print("\n2. 🔧 Update .env file:")
    print("   - Change WEB_UPLOAD_ENDPOINT to correct endpoint")
    print("   - Example: WEB_UPLOAD_ENDPOINT=http://74.63.10.103:3000/api/admin/photos")
    
    print("\n3. 🚀 Start web server if not running:")
    print("   cd /path/to/your/web/project")
    print("   npm run dev  # or pnpm run dev")
    
    print("\n4. 🛡️ Check authentication:")
    print("   - API might require JWT token")
    print("   - Check if endpoint needs admin auth")
    
    print("\n5. 📋 Disable upload temporarily:")
    print("   python3 folder_watcher.py --no-upload")
    print("   (Add --no-upload option to skip web upload)")

if __name__ == "__main__":
    test_web_server()
    test_endpoints()
    suggest_fixes()