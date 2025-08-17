#!/usr/bin/env python3
"""
Test script to verify audio device selection and playback
"""

import pyaudio
import wave
import numpy as np
import soundfile as sf
from pathlib import Path
import time

def test_audio_devices():
    """Test different audio output devices"""
    print("🔊 Audio Device Test")
    print("=" * 40)
    
    audio = pyaudio.PyAudio()
    
    try:
        # List all devices
        print("\n📱 Available Audio Devices:")
        output_devices = []
        
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            if device_info['maxOutputChannels'] > 0:
                output_devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxOutputChannels'],
                    'sample_rate': device_info['defaultSampleRate']
                })
                print(f"  Device {i}: {device_info['name']} ({device_info['maxOutputChannels']} channels)")
        
        if not output_devices:
            print("❌ No output devices found!")
            return
        
        # Create a test audio file (1 second beep)
        print("\n🎵 Creating test audio...")
        sample_rate = 44100
        duration = 1.0
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        test_audio = np.sin(2 * np.pi * frequency * t) * 0.3
        
        # Save test audio
        test_file = "test_audio.wav"
        sf.write(test_file, test_audio, sample_rate)
        print(f"✅ Test audio saved: {test_file}")
        
        # Test each output device
        print("\n🎧 Testing each output device:")
        
        for device in output_devices[:5]:  # Test first 5 devices
            print(f"\n🔊 Testing Device {device['index']}: {device['name']}")
            
            try:
                # Open output stream for this device
                stream = audio.open(
                    format=pyaudio.paFloat32,
                    channels=device['channels'],
                    rate=int(device['sample_rate']),
                    output=True,
                    output_device_index=device['index']
                )
                
                print(f"  ✅ Stream opened successfully")
                print(f"  📊 Playing 1-second beep at {frequency}Hz...")
                
                # Play the audio
                stream.write(test_audio.astype(np.float32).tobytes())
                time.sleep(1.1)  # Wait for audio to finish
                
                stream.stop_stream()
                stream.close()
                print(f"  ✅ Audio playback completed")
                
                # Ask user if they heard it
                response = input(f"  👂 Did you hear the beep from {device['name']}? (y/n): ").lower().strip()
                if response == 'y':
                    print(f"  🎉 SUCCESS! Device {device['index']} is working!")
                    print(f"  💡 This is the device you should use for TTS")
                    break
                else:
                    print(f"  ❌ No audio heard from this device")
                
            except Exception as e:
                print(f"  ❌ Failed to use device {device['index']}: {e}")
        
        # Clean up
        if Path(test_file).exists():
            Path(test_file).unlink()
            print(f"\n🧹 Test file cleaned up")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        audio.terminate()
        print("\n✅ Audio system cleaned up")

if __name__ == "__main__":
    test_audio_devices()
