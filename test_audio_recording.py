#!/usr/bin/env python3
"""
Test script for improved audio recording with silence detection
"""

import time
import logging
from audio_recorder import AudioRecorder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_audio_recording():
    """Test audio recording with silence detection"""
    print("="*50)
    print("Audio Recording Test with Silence Detection")
    print("="*50)
    
    recorder = AudioRecorder()
    
    try:
        print("\n🎤 Starting voice recording test...")
        print("📝 Speak something, then stay quiet for 1 second to stop recording")
        print("⏹️  Recording will stop automatically after 1 second of silence")
        print("⏱️  Or press Ctrl+C to stop manually")
        
        # Start recording (no duration - will use silence detection)
        audio_file = recorder.start_recording()
        
        if audio_file:
            print(f"✅ Recording started: {audio_file}")
            print("🗣️  Speak now...")
            
            # Wait for recording to complete
            while recorder.is_recording():
                time.sleep(0.1)
            
            print("✅ Recording completed!")
            print(f"📁 Audio saved to: {audio_file}")
            
        else:
            print("❌ Failed to start recording")
            
    except KeyboardInterrupt:
        print("\n⏹️  Recording stopped by user")
        recorder.stop_recording()
    except Exception as e:
        print(f"❌ Error during recording: {e}")
    finally:
        recorder.cleanup()
        print("🧹 Audio recorder cleaned up")

if __name__ == "__main__":
    test_audio_recording()
