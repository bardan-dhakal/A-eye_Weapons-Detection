# 🛡️ SentinelAI Streaming Integration

This document explains the streaming functionality that has been integrated into the main weapon detection system.

## 🌟 Features

- **Real-time video streaming** via Flask web server
- **Raspberry Pi optimized** camera handling
- **Web dashboard** with live detection feed
- **API endpoints** for status and threat data
- **Responsive design** for mobile and desktop
- **Performance monitoring** with FPS and statistics

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Settings

Edit `config.py` or create a `.env` file:

```bash
# Enable/disable streaming
STREAMING_ENABLED=true

# Server settings
SERVER_HOST=0.0.0.0
SERVER_PORT=5000

# Camera settings (for Raspberry Pi)
CAMERA_DEVICE=/dev/video0
CAMERA_WIDTH=640
CAMERA_HEIGHT=480
CAMERA_FPS=30

# Stream quality (1-100)
STREAM_QUALITY=85
```

### 3. Run the System

```bash
python main.py
```

### 4. Access the Dashboard

Open your browser and visit:
- **Dashboard**: `http://YOUR_PI_IP:5000/`
- **Video Feed**: `http://YOUR_PI_IP:5000/video_feed`
- **API Status**: `http://YOUR_PI_IP:5000/api/status`

## 🍓 Raspberry Pi Setup

### Camera Configuration

For Raspberry Pi, you may need to configure the camera device:

```bash
# Check available video devices
ls /dev/video*

# Common Raspberry Pi camera devices:
# /dev/video0 - Primary camera
# /dev/video1 - Secondary camera
# /dev/video2 - USB camera
```

### Performance Optimization

The system automatically detects Raspberry Pi and applies optimizations:

- **Reduced FPS** (max 20 FPS on Pi)
- **Lower buffer size** for reduced latency
- **Optimized resolution** settings

## 🌐 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Main dashboard |
| `/video_feed` | Live video stream |
| `/api/status` | Current detection status |
| `/api/threats` | Current threat detections |
| `/api/screenshots` | Recent screenshots info |
| `/health` | System health check |

### Example API Response

```json
{
  "threats": [
    {
      "class": "knife",
      "confidence": 0.85,
      "bbox": [100, 150, 200, 250]
    }
  ],
  "count": 1,
  "fps": 15.2,
  "frame_count": 1245,
  "total_detections": 23,
  "status": "threat_detected",
  "timestamp": 1640995200.123
}
```

## 🔧 Configuration Options

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# Streaming
STREAMING_ENABLED=true
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
STREAM_QUALITY=85

# Camera
CAMERA_DEVICE=/dev/video0
CAMERA_WIDTH=640
CAMERA_HEIGHT=480
CAMERA_FPS=30

# Detection
CONFIDENCE_THRESHOLD=0.5
WEAPON_CLASSES=knife,pistol

# Screenshots
SCREENSHOTS_PER_EVENT=7
MIN_TIME_BETWEEN_SHOTS=2
```

### Camera Device Selection

The system will automatically try to find the best camera:

1. **Raspberry Pi camera** (`/dev/video0`, `/dev/video1`, etc.)
2. **USB cameras** (fallback to camera indices 0-4)

## 📱 Mobile Access

The web dashboard is responsive and works on mobile devices:

- **Touch-friendly** interface
- **Real-time updates** via JavaScript
- **Optimized for small screens**

## 🛠️ Troubleshooting

### Common Issues

1. **Camera not found**
   ```bash
   # Check camera devices
   ls /dev/video*
   
   # Test camera access
   python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
   ```

2. **Port already in use**
   ```bash
   # Change port in config.py
   SERVER_PORT = 5001
   ```

3. **Poor streaming quality**
   ```bash
   # Adjust quality settings
   STREAM_QUALITY = 70  # Lower = better performance
   CAMERA_FPS = 15      # Lower FPS for better performance
   ```

### Performance Tips

- **Raspberry Pi**: Use lower resolution (320x240) for better performance
- **Network**: Use wired connection for stable streaming
- **Storage**: Ensure sufficient disk space for screenshots

## 🧪 Testing

Run the integration test:

```bash
python test_streaming.py
```

This will verify:
- Configuration loading
- Module imports
- Raspberry Pi detection
- Camera settings
- Flask server initialization

## 🔒 Security Notes

- The server binds to `0.0.0.0` by default (all interfaces)
- Consider using a firewall to restrict access
- Change default port if needed
- Use HTTPS in production environments

## 📊 Monitoring

The dashboard provides real-time monitoring:

- **FPS counter** - Performance indicator
- **Frame count** - Total frames processed
- **Detection count** - Number of weapon detections
- **Status indicator** - System health

## 🚀 Production Deployment

For production deployment:

1. **Use a reverse proxy** (nginx, Apache)
2. **Enable HTTPS** with SSL certificates
3. **Set up monitoring** and logging
4. **Configure firewall** rules
5. **Use systemd service** for auto-start

Example systemd service:

```ini
[Unit]
Description=SentinelAI Weapon Detection
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Weapons-Detection/backend
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📞 Support

For issues or questions:

1. Check the troubleshooting section
2. Run the test script: `python test_streaming.py`
3. Check logs for error messages
4. Verify camera and network connectivity

---

**🛡️ SentinelAI - Advanced Weapon Detection with Real-time Streaming**
