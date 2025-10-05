# launcher.py
# Smart launcher that chooses the best streaming architecture

import sys
import platform
from config import *

def detect_raspberry_pi():
    """Detect if running on Raspberry Pi"""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            return 'BCM' in cpuinfo or 'Raspberry Pi' in cpuinfo
    except:
        return False

def detect_system_performance():
    """Detect system performance characteristics"""
    import psutil
    
    cpu_count = psutil.cpu_count()
    memory_gb = psutil.virtual_memory().total // (1024**3)
    
    return {
        'cpu_cores': cpu_count,
        'memory_gb': memory_gb,
        'is_pi': detect_raspberry_pi()
    }

def choose_architecture():
    """Choose the best streaming architecture based on system"""
    system_info = detect_system_performance()
    
    print("🔍 System Analysis:")
    print(f"   CPU Cores: {system_info['cpu_cores']}")
    print(f"   Memory: {system_info['memory_gb']}GB")
    print(f"   Raspberry Pi: {system_info['is_pi']}")
    
    # Decision logic
    if system_info['is_pi'] or system_info['memory_gb'] < 4 or system_info['cpu_cores'] < 4:
        print("📱 Recommended: Optimized Architecture (Dual-Thread)")
        return 'optimized'
    else:
        print("💻 Recommended: Standard Architecture")
        return 'standard'

def launch_optimized():
    """Launch optimized streaming architecture"""
    print("\n🚀 Launching Optimized Streaming Architecture...")
    from streaming_optimized import start_optimized_streaming
    start_optimized_streaming()

def launch_standard():
    """Launch standard streaming architecture"""
    print("\n🚀 Launching Standard Streaming Architecture...")
    from main import main
    main()

def main():
    """Main launcher function"""
    print("🛡️ SentinelAI Smart Launcher")
    print("=" * 50)
    
    # Check configuration and platform
    if OPTIMIZED_STREAMING and platform.system() == 'Linux':
        print("⚙️  Configuration: Optimized streaming enabled for Linux")
        architecture = 'optimized'
    else:
        print("⚙️  Configuration: Using standard architecture")
        architecture = choose_architecture()
    
    # Launch appropriate architecture
    if architecture == 'optimized':
        launch_optimized()
    else:
        launch_standard()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Launcher stopped by user")
    except Exception as e:
        print(f"\n❌ Launcher error: {e}")
        print("💡 Try running with: python main.py (standard) or python streaming_optimized.py (optimized)")
