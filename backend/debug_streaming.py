# debug_streaming.py
# Debug script to identify streaming performance bottlenecks

import cv2
import time
import psutil
import os
from config import *

def test_camera_performance():
    """Test raw camera performance"""
    print("🔍 Testing Camera Performance...")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
    
    frame_count = 0
    start_time = time.time()
    
    print("📹 Capturing 100 frames to test camera speed...")
    
    for i in range(100):
        ret, frame = cap.read()
        if ret:
            frame_count += 1
        else:
            print(f"❌ Failed to read frame {i}")
    
    elapsed = time.time() - start_time
    fps = frame_count / elapsed if elapsed > 0 else 0
    
    print(f"📊 Camera Performance Results:")
    print(f"   Frames captured: {frame_count}")
    print(f"   Time elapsed: {elapsed:.2f} seconds")
    print(f"   Camera FPS: {fps:.2f}")
    
    cap.release()
    return fps

def test_jpeg_encoding_performance():
    """Test JPEG encoding performance"""
    print("\n🔍 Testing JPEG Encoding Performance...")
    
    # Create a test frame
    test_frame = cv2.imread('test_image.jpg') if os.path.exists('test_image.jpg') else None
    if test_frame is None:
        # Create a dummy frame
        test_frame = cv2.zeros((CAMERA_HEIGHT, CAMERA_WIDTH, 3), dtype=cv2.uint8)
        cv2.putText(test_frame, "TEST FRAME", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
    
    # Resize to streaming size
    small_frame = cv2.resize(test_frame, (240, 180))
    
    start_time = time.time()
    encode_count = 0
    
    print("🖼️ Encoding 50 frames to test JPEG speed...")
    
    for i in range(50):
        ret, buffer = cv2.imencode('.jpg', small_frame, [
            cv2.IMWRITE_JPEG_QUALITY, 40,
            cv2.IMWRITE_JPEG_OPTIMIZE, 1
        ])
        if ret:
            encode_count += 1
    
    elapsed = time.time() - start_time
    encode_fps = encode_count / elapsed if elapsed > 0 else 0
    avg_size = len(buffer) if 'buffer' in locals() else 0
    
    print(f"📊 JPEG Encoding Results:")
    print(f"   Frames encoded: {encode_count}")
    print(f"   Time elapsed: {elapsed:.2f} seconds")
    print(f"   Encode FPS: {encode_fps:.2f}")
    print(f"   Average frame size: {avg_size} bytes")
    
    return encode_fps

def test_system_resources():
    """Test system resource usage"""
    print("\n🔍 Testing System Resources...")
    
    # CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # Memory usage
    memory = psutil.virtual_memory()
    
    # Disk usage
    disk = psutil.disk_usage('/')
    
    print(f"📊 System Resources:")
    print(f"   CPU Usage: {cpu_percent}%")
    print(f"   Memory Usage: {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)")
    print(f"   Disk Usage: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)")
    
    return cpu_percent, memory.percent

def test_network_performance():
    """Test network performance"""
    print("\n🔍 Testing Network Performance...")
    
    try:
        import requests
        start_time = time.time()
        response = requests.get(f'http://{SERVER_HOST}:{SERVER_PORT}/health', timeout=5)
        elapsed = time.time() - start_time
        
        print(f"📊 Network Performance:")
        print(f"   Server response time: {elapsed:.3f} seconds")
        print(f"   Server status: {response.status_code}")
        
        return elapsed
    except Exception as e:
        print(f"❌ Network test failed: {e}")
        return None

def main():
    """Run all performance tests"""
    print("🚀 Streaming Performance Debug Tool")
    print("=" * 50)
    
    # Test system resources first
    cpu_usage, memory_usage = test_system_resources()
    
    # Test camera performance
    camera_fps = test_camera_performance()
    
    # Test JPEG encoding
    encode_fps = test_jpeg_encoding_performance()
    
    # Test network (if server is running)
    network_time = test_network_performance()
    
    # Analysis
    print(f"\n📋 Performance Analysis:")
    print(f"   Camera FPS: {camera_fps:.2f}")
    print(f"   Encode FPS: {encode_fps:.2f}")
    print(f"   CPU Usage: {cpu_usage}%")
    print(f"   Memory Usage: {memory_usage}%")
    
    # Bottleneck identification
    print(f"\n🔍 Bottleneck Analysis:")
    
    if camera_fps < 10:
        print("   ⚠️  Camera is the bottleneck - very low FPS")
    elif encode_fps < 20:
        print("   ⚠️  JPEG encoding is the bottleneck - slow compression")
    elif cpu_usage > 80:
        print("   ⚠️  CPU is overloaded - system struggling")
    elif memory_usage > 90:
        print("   ⚠️  Memory is full - system running out of RAM")
    else:
        print("   ✅ No obvious bottlenecks detected")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    
    if camera_fps < 15:
        print("   - Reduce camera resolution further")
        print("   - Lower camera FPS setting")
    
    if encode_fps < 30:
        print("   - Lower JPEG quality to 30 or less")
        print("   - Use even smaller frame size")
    
    if cpu_usage > 70:
        print("   - Increase frame skipping")
        print("   - Disable object detection temporarily")
        print("   - Close other applications")
    
    print(f"\n🎯 Expected streaming FPS: {min(camera_fps, encode_fps, 15):.1f}")

if __name__ == "__main__":
    main()
