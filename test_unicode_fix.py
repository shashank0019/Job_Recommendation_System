#!/usr/bin/env python3
"""Test script to verify the Unicode encoding fix for the main route."""

import requests
import time

def test_main_route():
    """Test the main route to see if Unicode error is fixed."""
    try:
        print("Testing main route...")
        response = requests.get('http://localhost:5000/', timeout=10)
        
        if response.status_code == 200:
            print("✅ SUCCESS: Main route returned 200 OK")
            print(f"📄 Response length: {len(response.text)} characters")
            print(f"🔤 Content type: {response.headers.get('content-type', 'unknown')}")
            
            # Check if it's valid HTML
            if '<!DOCTYPE html>' in response.text[:100]:
                print("✅ SUCCESS: Valid HTML response detected")
            else:
                print("⚠️  WARNING: Response doesn't appear to be HTML")
                
            return True
        else:
            print(f"❌ ERROR: Server returned status code {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server. Make sure it's running on port 5000.")
        return False
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        return False

if __name__ == '__main__':
    print("🔧 Testing Unicode encoding fix...")
    time.sleep(2)  # Give server time to start
    success = test_main_route()
    
    if success:
        print("\n🎉 Unicode encoding fix appears to be working!")
    else:
        print("\n💥 There may still be issues with the server.")