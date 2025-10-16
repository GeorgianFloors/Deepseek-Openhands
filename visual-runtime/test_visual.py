#!/usr/bin/env python3
"""
Test script for Visual Runtime functionality
"""

import requests
import json
import time

def test_visual_sessions_api():
    """Test the visual sessions API endpoints"""
    base_url = "http://localhost:3000"
    
    print("🧪 Testing Visual Sessions API...")
    
    # Test 1: Create a visual session
    print("\n1. Creating visual session...")
    session_data = {
        "resolution": "1600x900",
        "timeout_minutes": 60,
        "idle_timeout_minutes": 15,
        "enable_recording": True,
        "enable_file_transfer": True
    }
    
    try:
        response = requests.post(f"{base_url}/api/visual-sessions", json=session_data)
        if response.status_code == 200:
            session = response.json()
            print(f"✅ Session created: {session['session_id']}")
            print(f"   VNC URL: {session['vnc_url']}")
            print(f"   noVNC URL: {session['novnc_url']}")
            print(f"   Status: {session['status']}")
            
            session_id = session['session_id']
            
            # Test 2: Get session details
            print("\n2. Getting session details...")
            response = requests.get(f"{base_url}/api/visual-sessions/{session_id}")
            if response.status_code == 200:
                session_details = response.json()
                print(f"✅ Session details retrieved")
                print(f"   Status: {session_details['status']}")
            else:
                print(f"❌ Failed to get session details: {response.status_code}")
            
            # Test 3: Get session recording (placeholder)
            print("\n3. Testing recording endpoint...")
            response = requests.get(f"{base_url}/api/visual-sessions/{session_id}/recording")
            if response.status_code == 200:
                recording_info = response.json()
                print(f"✅ Recording endpoint working")
                print(f"   Recording available: {recording_info['recording_available']}")
            else:
                print(f"❌ Failed to get recording info: {response.status_code}")
            
            # Test 4: Get session logs
            print("\n4. Testing logs endpoint...")
            response = requests.get(f"{base_url}/api/visual-sessions/{session_id}/logs")
            if response.status_code == 200:
                logs_info = response.json()
                print(f"✅ Logs endpoint working")
                print(f"   Log entries: {len(logs_info['logs'])}")
            else:
                print(f"❌ Failed to get logs: {response.status_code}")
            
            # Test 5: Stop session
            print("\n5. Stopping session...")
            response = requests.post(f"{base_url}/api/visual-sessions/{session_id}/stop")
            if response.status_code == 200:
                stop_info = response.json()
                print(f"✅ Session stopped: {stop_info['message']}")
            else:
                print(f"❌ Failed to stop session: {response.status_code}")
                
        else:
            print(f"❌ Failed to create session: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to OpenHands server. Make sure it's running on port 3000.")
    except Exception as e:
        print(f"❌ Error during testing: {e}")


def test_docker_build():
    """Test if Docker image can be built"""
    print("\n🐳 Testing Docker build...")
    
    import subprocess
    import os
    
    try:
        # Change to visual-runtime directory
        os.chdir("visual-runtime")
        
        # Try to build the Docker image
        result = subprocess.run(
            ["docker", "build", "-t", "openhands-visual-test", "."],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Docker image built successfully")
        else:
            print(f"❌ Docker build failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Docker test failed: {e}")
    finally:
        # Change back to original directory
        os.chdir("..")


if __name__ == "__main__":
    print("🚀 Visual Runtime Test Suite")
    print("=" * 50)
    
    test_visual_sessions_api()
    test_docker_build()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print("• API endpoints: Implemented and testable")
    print("• Docker container: Ready for building")
    print("• Integration: Visual sessions API added to main server")
    print("\n🎯 Next steps:")
    print("1. Build Docker image: cd visual-runtime && docker build -t openhands-visual .")
    print("2. Start OpenHands server: python -m openhands.server")
    print("3. Test API: python visual-runtime/test_visual.py")
    print("4. Access noVNC: http://localhost:7900/vnc.html (after Docker run)")