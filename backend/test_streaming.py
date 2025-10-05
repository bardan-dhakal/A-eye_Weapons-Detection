# test_streaming.py
# Simple test script to verify streaming functionality

import sys
import time
from config import *

def test_config():
    """Test if configuration is properly loaded"""
    print("🧪 Testing Configuration...")
    print(f"   Streaming enabled: {STREAMING_ENABLED}")
    print(f"   Server host: {SERVER_HOST}")
    print(f"   Server port: {SERVER_PORT}")
    print(f"   Camera device: {CAMERA_DEVICE}")
    print(f"   Camera resolution: {CAMERA_WIDTH}x{CAMERA_HEIGHT}")
    print(f"   Stream quality: {STREAM_QUALITY}")
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🧪 Testing Imports...")
    try:
        from flask import Flask
        from flask_cors import CORS
        print("   ✅ Flask and Flask-CORS imported successfully")
        
        from streaming_server import set_detector, update_streaming_frame, start_server
        print("   ✅ Streaming server module imported successfully")
        
        from utils import is_raspberry_pi, get_optimal_camera_settings
        print("   ✅ Utils module imported successfully")
        
        from detection import WeaponDetector
        print("   ✅ Detection module imported successfully")
        
        from screenshot_manager import ScreenshotManager
        print("   ✅ Screenshot manager imported successfully")
        
        return True
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False

def test_raspberry_pi_detection():
    """Test Raspberry Pi detection"""
    print("\n🧪 Testing Raspberry Pi Detection...")
    from utils import is_raspberry_pi
    is_pi = is_raspberry_pi()
    print(f"   Running on Raspberry Pi: {is_pi}")
    return True

def test_camera_settings():
    """Test camera settings generation"""
    print("\n🧪 Testing Camera Settings...")
    from utils import get_optimal_camera_settings
    settings = get_optimal_camera_settings()
    print(f"   Optimal settings: {settings}")
    return True

def test_streaming_server():
    """Test streaming server initialization"""
    print("\n🧪 Testing Streaming Server...")
    try:
        from streaming_server import app
        print("   ✅ Flask app created successfully")
        
        # Test if we can create a test client
        with app.test_client() as client:
            response = client.get('/health')
            print(f"   ✅ Health endpoint accessible: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"   ❌ Streaming server test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🛡️ SentinelAI Streaming Integration Test")
    print("=" * 50)
    
    tests = [
        test_config,
        test_imports,
        test_raspberry_pi_detection,
        test_camera_settings,
        test_streaming_server
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Streaming integration is ready.")
        print("\n🚀 To start the system:")
        print("   python main.py")
        print(f"\n🌐 Then visit: http://{SERVER_HOST}:{SERVER_PORT}/")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
