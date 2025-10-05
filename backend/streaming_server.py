# streaming_server.py
# Flask server to stream AI detection feed to frontend

from flask import Flask, Response, jsonify, render_template_string
from flask_cors import CORS
import cv2
import numpy as np
import time
import json
from threading import Thread, Lock
from pathlib import Path
from config import *

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Global variables for streaming
current_frame = None
detection_data = {
    'threats': [],
    'count': 0,
    'fps': 0,
    'frame_count': 0,
    'total_detections': 0,
    'status': 'initializing',
    'timestamp': 0
}
frame_lock = Lock()
data_lock = Lock()

# Global detector reference (will be set by main system)
detector = None
screenshot_manager = None

def set_detector(detector_instance, screenshot_manager_instance):
    """Set the detector and screenshot manager instances from main system"""
    global detector, screenshot_manager
    detector = detector_instance
    screenshot_manager = screenshot_manager_instance

def generate_frames():
    """Ultra-optimized generator function for video streaming"""
    last_frame_time = 0
    frame_interval = 1.0 / STREAM_MAX_FPS
    skip_counter = 0
    
    while True:
        current_time = time.time()
        
        # Skip frames if updating too frequently
        if current_time - last_frame_time < frame_interval:
            time.sleep(0.005)  # Longer sleep to reduce CPU usage
            continue
        
        # Additional frame skipping for streaming
        skip_counter += 1
        if skip_counter <= STREAMING_SKIP_FRAMES:
            continue
        skip_counter = 0
            
        # Try to get frame without blocking
        try:
            with frame_lock:
                if current_frame is None:
                    time.sleep(0.02)
                    continue
                # Use reference instead of copy for speed
                frame = current_frame
        except:
            time.sleep(0.01)
            continue
        
        # Resize to very small size for maximum speed
        small_frame = cv2.resize(frame, (240, 180))  # Even smaller resolution
        
        # Encode with very low quality for speed
        ret, buffer = cv2.imencode('.jpg', small_frame, [
            cv2.IMWRITE_JPEG_QUALITY, 40,  # Very low quality
            cv2.IMWRITE_JPEG_OPTIMIZE, 1,
            cv2.IMWRITE_JPEG_PROGRESSIVE, 1
        ])
        
        if not ret:
            continue
        
        frame_bytes = buffer.tobytes()
        
        # Yield frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        last_frame_time = current_time

def update_streaming_frame(frame, detection_info, fps, frame_count, total_detections):
    """Update the current frame and detection data for streaming"""
    global current_frame, detection_data
    
    # Only update if we don't already have a frame or if enough time has passed
    try:
        with frame_lock:
            # Use reference instead of copy for speed - be careful with this!
            current_frame = frame
    except:
        pass  # Skip if lock fails
    
    # Prepare detection data
    threats = []
    if detection_info:
        for i, weapon in enumerate(detection_info.get('classes', [])):
            threats.append({
                'class': weapon,
                'confidence': detection_info.get('confidences', [])[i] if i < len(detection_info.get('confidences', [])) else 0.0,
                'bbox': [0, 0, 100, 100]  # Placeholder bbox - you can extract from detection results if needed
            })
    
    with data_lock:
        detection_data = {
            'threats': threats,
            'count': len(threats),
            'fps': round(fps, 2),
            'frame_count': frame_count,
            'total_detections': total_detections,
            'status': 'threat_detected' if len(threats) > 0 else 'monitoring',
            'timestamp': time.time()
        }

# --- API ENDPOINTS ---

@app.route('/')
def index():
    """Main dashboard page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🛡️ SentinelAI - Weapon Detection System</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                color: white;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                min-height: 100vh;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            h1 {
                color: #00ff00;
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
            }
            .subtitle {
                color: #aaa;
                font-size: 1.2em;
                margin-bottom: 20px;
            }
            .video-container {
                text-align: center;
                margin: 20px 0;
                position: relative;
            }
            img {
                max-width: 100%;
                max-height: 600px;
                border: 3px solid #00ff00;
                border-radius: 12px;
                box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
                transition: all 0.3s ease;
            }
            img:hover {
                box-shadow: 0 0 30px rgba(0, 255, 0, 0.4);
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .stat-card {
                background: rgba(42, 42, 42, 0.8);
                padding: 20px;
                border-radius: 12px;
                border: 1px solid #444;
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
            }
            .stat-card:hover {
                background: rgba(52, 52, 52, 0.9);
                border-color: #00ff00;
            }
            .stat-title {
                font-size: 0.9em;
                color: #aaa;
                margin-bottom: 5px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .stat-value {
                font-size: 2em;
                font-weight: bold;
                margin-bottom: 5px;
            }
            .status {
                color: #00ff00;
            }
            .status.threat {
                color: #ff4444;
                animation: pulse 1s infinite;
            }
            .fps {
                color: #44aaff;
            }
            .frames {
                color: #ffaa44;
            }
            .detections {
                color: #ff4444;
            }
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
            .controls {
                margin-top: 30px;
                text-align: center;
            }
            .btn {
                background: #00ff00;
                color: #000;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                cursor: pointer;
                margin: 0 10px;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
            }
            .btn:hover {
                background: #00cc00;
                transform: translateY(-2px);
            }
            .footer {
                margin-top: 40px;
                text-align: center;
                color: #666;
                font-size: 0.9em;
            }
            .loading {
                color: #ffaa44;
                animation: blink 1s infinite;
            }
            @keyframes blink {
                0%, 50% { opacity: 1; }
                51%, 100% { opacity: 0.3; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛡️ SentinelAI</h1>
                <div class="subtitle">Real-Time Weapon Detection & Security Monitoring</div>
            </div>
            
            <div class="video-container">
                <img src="/video_feed" alt="Detection Feed" id="videoFeed">
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-title">System Status</div>
                    <div class="stat-value status" id="status">Loading...</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-title">Frames Per Second</div>
                    <div class="stat-value fps" id="fps">0</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-title">Total Frames</div>
                    <div class="stat-value frames" id="frames">0</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-title">Total Detections</div>
                    <div class="stat-value detections" id="total">0</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-title">Current Threats</div>
                    <div class="stat-value" id="current">0</div>
                </div>
            </div>
            
            <div class="controls">
                <a href="/api/status" class="btn" target="_blank">📊 API Status</a>
                <a href="/api/threats" class="btn" target="_blank">🚨 Threat Data</a>
                <a href="/health" class="btn" target="_blank">❤️ Health Check</a>
            </div>
            
            <div class="footer">
                <p>🛡️ SentinelAI Weapon Detection System | Powered by YOLOv8 & AI</p>
                <p>Real-time monitoring • Automated alerts • Secure streaming</p>
            </div>
        </div>
        
        <script>
            // Update stats every second
            setInterval(() => {
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => {
                        const statusEl = document.getElementById('status');
                        statusEl.textContent = data.status;
                        statusEl.className = 'status ' + (data.status === 'threat_detected' ? 'threat' : '');
                        
                        document.getElementById('fps').textContent = data.fps;
                        document.getElementById('frames').textContent = data.frame_count;
                        document.getElementById('total').textContent = data.total_detections || 0;
                        document.getElementById('current').textContent = data.count;
                    })
                    .catch(err => {
                        console.error('Error fetching status:', err);
                        document.getElementById('status').textContent = 'Connection Error';
                        document.getElementById('status').className = 'status threat';
                    });
            }, 1000);
            
            // Handle video feed errors
            document.getElementById('videoFeed').addEventListener('error', function() {
                this.src = '/video_feed?' + new Date().getTime();
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/status')
def get_status():
    """Get current detection status"""
    with data_lock:
        return jsonify(detection_data)

@app.route('/api/threats')
def get_threats():
    """Get current threat detections"""
    with data_lock:
        return jsonify({
            'threats': detection_data.get('threats', []),
            'count': detection_data.get('count', 0),
            'timestamp': detection_data.get('timestamp', 0)
        })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': detector is not None,
        'screenshot_manager_active': screenshot_manager is not None,
        'streaming_enabled': STREAMING_ENABLED,
        'timestamp': time.time()
    })

@app.route('/api/screenshots')
def get_screenshots():
    """Get information about recent screenshots"""
    if screenshot_manager is None:
        return jsonify({'error': 'Screenshot manager not available'})
    
    try:
        # Get recent screenshots info
        import os
        screenshot_folder = SCREENSHOT_FOLDER
        if not os.path.exists(screenshot_folder):
            return jsonify({'screenshots': [], 'count': 0})
        
        screenshots = []
        for filename in os.listdir(screenshot_folder):
            if filename.endswith('.jpg'):
                filepath = os.path.join(screenshot_folder, filename)
                stat = os.stat(filepath)
                screenshots.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'created': stat.st_ctime,
                    'modified': stat.st_mtime
                })
        
        # Sort by modification time (newest first)
        screenshots.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({
            'screenshots': screenshots[:10],  # Return last 10 screenshots
            'count': len(screenshots),
            'folder': screenshot_folder
        })
    except Exception as e:
        return jsonify({'error': str(e)})

def start_server():
    """Start the Flask server"""
    if not STREAMING_ENABLED:
        print("⚠️  Streaming is disabled in configuration")
        return None
    
    print(f"\n🌐 Starting Flask streaming server...")
    print(f"   Host: {SERVER_HOST}")
    print(f"   Port: {SERVER_PORT}")
    print(f"   Dashboard: http://{SERVER_HOST}:{SERVER_PORT}/")
    print(f"   Video feed: http://{SERVER_HOST}:{SERVER_PORT}/video_feed")
    print(f"   API status: http://{SERVER_HOST}:{SERVER_PORT}/api/status")
    
    try:
        app.run(host=SERVER_HOST, port=SERVER_PORT, threaded=True, debug=False)
        return True
    except Exception as e:
        print(f"❌ Failed to start Flask server: {e}")
        return False

if __name__ == '__main__':
    # This allows running the streaming server independently for testing
    print("🛡️ SentinelAI Streaming Server")
    print("=" * 50)
    print("Note: This server needs to be started from main.py to get detector instances")
    print("Starting in test mode...")
    
    # Start server
    start_server()
