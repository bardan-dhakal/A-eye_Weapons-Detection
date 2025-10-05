# 🛡️ A-eye - Advanced Weapon Detection System

A comprehensive real-time weapon detection system using YOLOv8 with advanced streaming capabilities, AI analysis, and automated security alerts.

## 🚀 Features

- **Real-time Detection**: YOLOv8-based detection for knives and pistols
- **Live Streaming**: Web-based video streaming with optimized performance
- **AI Analysis**: Gemini Vision API integration for event analysis
- **Voice Alerts**: ElevenLabs text-to-speech for security announcements
- **Phone Notifications**: Twilio integration for calls and SMS alerts
- **Screenshot Capture**: Automatic screenshot capture on weapon detection
- **Raspberry Pi Optimized**: Special optimizations for Raspberry Pi deployment
- **Modular Architecture**: Clean, maintainable code structure

## 📁 Project Structure

```
Weapons-Detection/
├── backend/                    # Main application code
│   ├── main.py                # Main application entry point
│   ├── detection.py           # YOLO detection logic
│   ├── streaming_server.py    # Flask streaming server
│   ├── streaming_optimized.py # Optimized dual-thread architecture
│   ├── launcher.py           # Smart architecture launcher
│   ├── gemini_api.py         # Gemini Vision API integration
│   ├── elevenlabs_api.py     # ElevenLabs TTS integration
│   ├── twilio_api.py         # Twilio phone/SMS integration
│   ├── screenshot_manager.py # Screenshot and event management
│   ├── config.py             # Configuration settings
│   ├── utils.py              # Utility functions
│   └── weapon_detections/    # Screenshot storage
├── guns-knives-yolo_dataset/ # Training dataset
├── models_and_checkpoints/   # Trained models and checkpoints
├── runs/                     # Training and validation outputs
└── requirements.txt          # Python dependencies
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- OpenCV
- CUDA (optional, for GPU acceleration)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/Weapons-Detection.git
   cd Weapons-Detection
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Copy and edit the environment file
   cp backend/.env.example backend/.env
   # Edit backend/.env with your API keys
   ```

4. **Download the trained model**
   ```bash
   # The best_fine-tuned_model.pt should be in the backend directory
   # If not, download it from the models_and_checkpoints directory
   ```

## 🚀 Quick Start

### Option 1: Smart Launcher (Recommended)
```bash
cd backend
python launcher.py
```

### Option 2: Standard Architecture
```bash
cd backend
python main.py
```

### Option 3: Optimized Architecture
```bash
cd backend
python streaming_optimized.py
```

## 🌐 Access the System

Once running, access the system at:
- **Web Dashboard**: `http://localhost:5000/`
- **Live Stream**: `http://localhost:5000/video_feed`
- **API Status**: `http://localhost:5000/api/status`

## ⚙️ Configuration

Edit `backend/config.py` or create a `.env` file to configure:

- **Detection Settings**: Confidence threshold, frame skipping
- **Streaming Settings**: Quality, FPS limits, resolution
- **API Keys**: Gemini, ElevenLabs, Twilio credentials
- **Camera Settings**: Device path, resolution, FPS

## 📊 Performance

### Standard Architecture
- **Streaming FPS**: 5-10 FPS
- **Detection FPS**: 3-5 FPS
- **CPU Usage**: 70-90%

### Optimized Architecture
- **Streaming FPS**: 10-15 FPS
- **Detection FPS**: 5-8 FPS
- **CPU Usage**: 50-70%
- **Memory Usage**: 40% reduction

## 🍓 Raspberry Pi Deployment

The system is optimized for Raspberry Pi deployment:

```bash
# Install additional dependencies
sudo apt install mpg123 omxplayer

# Run with Pi optimizations
cd backend
python streaming_optimized.py
```

## 🧪 Testing

### Performance Testing
```bash
cd backend
python performance_test.py
```

### Streaming Testing
```bash
cd backend
python test_streaming.py
```

### Debug Streaming
```bash
cd backend
python debug_streaming.py
```

## 📈 Training

To train your own models, see the training documentation in the respective directories.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Check the troubleshooting guides in subdirectory READMEs
- Review the performance optimization documentation
- Open an issue on GitHub

## 🔗 Links

- [Backend Documentation](backend/README.md)
- [Streaming Guide](backend/STREAMING_README.md)
- [Dataset Documentation](guns-knives-yolo_dataset/README.md)
- [Models Documentation](models_and_checkpoints/README.md)

---

**🛡️ A-eye - Advanced Weapon Detection & Security Monitoring**
