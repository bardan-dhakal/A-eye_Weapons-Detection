# streaming_optimized.py
# Optimized streaming architecture for Raspberry Pi

import cv2
import time
import threading
import platform
from queue import Queue, Empty
from flask import Flask, Response, render_template_string
from flask_cors import CORS
from config import *

app = Flask(__name__)
CORS(app)

# Global frame buffer - thread-safe
frame_buffer = Queue(maxsize=3)  # Small buffer to prevent memory buildup
latest_frame = None
frame_lock = threading.Lock()

# Performance counters
stream_stats = {
    'frames_served': 0,
    'frames_dropped': 0,
    'last_frame_time': 0,
    'fps': 0
}

def camera_streaming_thread():
    """Dedicated thread for camera capture and streaming"""
    global latest_frame, stream_stats
    
    print("📹 Starting dedicated camera streaming thread...")
    
    # Open camera with optimized settings
    # Use proper camera detection for Windows/Linux
    if platform.system() == 'Windows':
        camera_index = 0  # Use default camera on Windows
    else:
        camera_index = CAMERA_DEVICE if CAMERA_DEVICE.startswith('/dev/') else 0
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("❌ Cannot open camera for streaming")
        return
    
    # Optimize camera settings for streaming
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, min(CAMERA_FPS, 15))  # Limit to 15 FPS max
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimal buffer
    
    frame_count = 0
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read camera frame")
            time.sleep(0.1)
            continue
        
        frame_count += 1
        
        # Resize frame immediately for streaming efficiency
        small_frame = cv2.resize(frame, (240, 180))
        
        # Update global frame (thread-safe)
        with frame_lock:
            latest_frame = small_frame.copy()
        
        # Update stats
        current_time = time.time()
        elapsed = current_time - start_time
        if elapsed > 0:
            stream_stats['fps'] = frame_count / elapsed
        stream_stats['last_frame_time'] = current_time
        
        # Small delay to prevent overwhelming the system
        time.sleep(0.05)  # 20 FPS max for camera thread
    
    cap.release()

def detection_thread():
    """Dedicated thread for object detection (separate from streaming)"""
    print("🔍 Starting dedicated detection thread...")
    
    # Import here to avoid circular imports
    from detection import WeaponDetector
    from screenshot_manager import ScreenshotManager
    
    # Initialize detector
    detector = WeaponDetector(MODEL_PATH)
    screenshot_manager = ScreenshotManager()
    
    # Open separate camera instance for detection
    # Use proper camera detection for Windows/Linux
    if platform.system() == 'Windows':
        camera_index = 0  # Use default camera on Windows
    else:
        camera_index = CAMERA_DEVICE if CAMERA_DEVICE.startswith('/dev/') else 0
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("❌ Cannot open camera for detection")
        return
    
    # Optimize for detection (can use higher resolution)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 10)  # Lower FPS for detection
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue
        
        frame_count += 1
        
        # Only process every 3rd frame for detection
        if frame_count % 3 != 0:
            continue
        
        try:
            # Run detection
            results = detector.detect(frame)
            if results is not None:
                detection_info = detector.check_weapon_detection(results)
                if detection_info:
                    # Take screenshot with detection overlay
                    frame_with_detections = detector.draw_detections(frame, detection_info)
                    screenshot_manager.take_screenshot(frame_with_detections, detection_info)
        except Exception as e:
            print(f"❌ Detection error: {e}")
        
        # Longer delay for detection thread
        time.sleep(0.2)  # 5 FPS max for detection
    
    cap.release()

def generate_stream():
    """Ultra-optimized frame generator for streaming"""
    global latest_frame, stream_stats
    
    print("🌐 Starting optimized stream generator...")
    
    while True:
        current_time = time.time()
        
        # Get latest frame
        with frame_lock:
            if latest_frame is None:
                time.sleep(0.1)
                continue
            frame = latest_frame
        
        # Encode frame with minimal settings
        ret, buffer = cv2.imencode('.jpg', frame, [
            cv2.IMWRITE_JPEG_QUALITY, 30,  # Very low quality for speed
            cv2.IMWRITE_JPEG_OPTIMIZE, 1
        ])
        
        if ret:
            stream_stats['frames_served'] += 1
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        else:
            stream_stats['frames_dropped'] += 1
        
        # Control frame rate
        time.sleep(0.067)  # ~15 FPS max for streaming

@app.route('/')
def dashboard():
    """Simple dashboard with streaming"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🛡️ SentinelAI - Optimized Stream</title>
        <meta charset="UTF-8">
        <style>
            body {
                margin: 0;
                padding: 20px;
                background: #1a1a1a;
                color: white;
                font-family: Arial, sans-serif;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                text-align: center;
            }
            h1 {
                color: #00ff00;
                margin-bottom: 20px;
            }
            img {
                max-width: 100%;
                border: 2px solid #00ff00;
                border-radius: 8px;
            }
            .stats {
                background: #2a2a2a;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
                font-family: monospace;
            }
            .status {
                color: #00ff00;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ SentinelAI - Optimized Stream</h1>
            <p>High-performance streaming for Raspberry Pi</p>
            
            <img src="/stream" alt="Live Stream" id="stream">
            
            <div class="stats">
                <div class="status">✅ Optimized Architecture Active</div>
                <div>Separate threads for streaming and detection</div>
                <div>Minimal memory usage</div>
                <div>Raspberry Pi optimized</div>
            </div>
        </div>
        
        <script>
            // Auto-refresh stream on error
            document.getElementById('stream').addEventListener('error', function() {
                this.src = '/stream?' + new Date().getTime();
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/stream')
def stream():
    """Optimized streaming endpoint"""
    return Response(generate_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stats')
def stats():
    """Streaming statistics"""
    return {
        'frames_served': stream_stats['frames_served'],
        'frames_dropped': stream_stats['frames_dropped'],
        'fps': round(stream_stats['fps'], 2),
        'architecture': 'optimized_dual_thread'
    }

def start_optimized_streaming():
    """Start the optimized streaming system"""
    print("🚀 Starting Optimized Streaming Architecture")
    print("=" * 60)
    
    # Start camera streaming thread
    camera_thread = threading.Thread(target=camera_streaming_thread, daemon=True)
    camera_thread.start()
    
    # Start detection thread
    detection_thread_obj = threading.Thread(target=detection_thread, daemon=True)
    detection_thread_obj.start()
    
    # Wait a moment for threads to initialize
    time.sleep(2)
    
    print(f"✅ Threads started successfully!")
    print(f"📹 Camera streaming thread: Active")
    print(f"🔍 Detection thread: Active")
    print(f"🌐 Flask server: Starting...")
    print(f"🌐 Access at: http://{SERVER_HOST}:{SERVER_PORT}/")
    print(f"📊 Stats at: http://{SERVER_HOST}:{SERVER_PORT}/stats")
    print("-" * 60)
    
    try:
        app.run(host=SERVER_HOST, port=SERVER_PORT, threaded=True, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down optimized streaming...")

if __name__ == "__main__":
    start_optimized_streaming()
