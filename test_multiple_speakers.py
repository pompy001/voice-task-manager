#!/usr/bin/env python3
"""
Test script to try multiple speaker devices with louder audio
"""

import pyaudio
import numpy as np
import soundfile as sf
from pathlib import Path
import time

def test_multiple_speakers():
    """Test multiple speaker devices with louder audio"""
    print("🔊 Multiple Speaker Test")
    print("=" * 40)
    
    audio = pyaudio.PyAudio()
    
    try:
        # List speaker devices
        print("\n📱 Available Speaker Devices:")
        speaker_devices = []
        
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            if (device_info['maxOutputChannels'] > 0 and 
                'speaker' in device_info['name'].lower()):
                speaker_devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxOutputChannels']
                })
                print(f"  Device {i}: {device_info['name']} ({device_info['maxOutputChannels']} channels)")
        
        if not speaker_devices:
            print("❌ No speaker devices found!")
            return
        
        # Create LOUD test audio (multiple frequencies, higher volume)
        print("\n🎵 Creating LOUD test audio...")
        sample_rate = 44100
        duration = 3.0  # 3 seconds
        
        # Create multiple frequencies for better audibility
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Mix multiple frequencies
        freq1 = 440   # A4
        freq2 = 880   # A5  
        freq3 = 1760  # A6
        
        audio1 = np.sin(2 * np.pi * freq1 * t) * 0.4
        audio2 = np.sin(2 * np.pi * freq2 * t) * 0.3
        audio3 = np.sin(2 * np.pi * freq3 * t) * 0.2
        
        # Combine and make it louder
        test_audio = (audio1 + audio2 + audio3) * 0.8  # High volume
        
        # Save test audio
        test_file = "loud_test_audio.wav"
        sf.write(test_file, test_audio, sample_rate)
        print(f"✅ Loud test audio saved: {test_file}")
        print(f"📊 Audio: 3 seconds, multiple frequencies, high volume")
        
        # Test each speaker device
        print(f"\n🎧 Testing {len(speaker_devices)} speaker devices:")
        
        for device in speaker_devices:
            print(f"\n🔊 Testing Device {device['index']}: {device['name']}")
            print(f"  📊 Playing 3-second loud audio...")
            
            try:
                # Open output stream for this device
                stream = audio.open(
                    format=pyaudio.paFloat32,
                    channels=device['channels'],
                    rate=sample_rate,
                    output=True,
                    output_device_index=device['index']
                )
                
                print(f"  ✅ Stream opened successfully")
                
                # Play the audio
                stream.write(test_audio.astype(np.float32).tobytes())
                time.sleep(3.5)  # Wait for audio to finish
                
                stream.stop_stream()
                stream.close()
                print(f"  ✅ Audio playback completed")
                
                # Ask user if they heard it
                response = input(f"  👂 Did you hear the LOUD audio from {device['name']}? (y/n): ").lower().strip()
                if response == 'y':
                    print(f"  🎉 SUCCESS! Device {device['index']} is working!")
                    print(f"  💡 This is the device you should use for TTS")
                    
                    # Save this as the working device
                    with open("working_audio_device.txt", "w") as f:
                        f.write(str(device['index']))
                    print(f"  💾 Working device saved to working_audio_device.txt")
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
    test_multiple_speakers()
