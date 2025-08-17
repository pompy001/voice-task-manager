#!/usr/bin/env python3
"""
Test script for PyTTSX3 TTS system
Tests the new TTS implementation without Hugging Face dependencies
"""

import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_pyttsx3_tts():
    """Test the PyTTSX3 TTS system"""
    print("🎤 Testing PyTTSX3 TTS System")
    print("=" * 50)
    
    try:
        # Import the new TTS system
        from text_to_speech_pyttsx3 import TextToSpeech, PyTTSX3TTS
        
        print("✅ Successfully imported PyTTSX3 TTS modules")
        
        # Test 1: Basic TTS initialization
        print("\n🧪 Test 1: TTS Initialization")
        tts = TextToSpeech()
        
        if tts.is_available():
            print("✅ TTS system is available and working")
        else:
            print("❌ TTS system is not available")
            return
        
        # Test 2: List available voices
        print("\n🎵 Test 2: Available Voices")
        voices = tts.list_voices()
        if voices:
            print(f"Found {len(voices)} available voices:")
            for i, voice in enumerate(voices):
                print(f"  {i+1}. {voice['name']} ({voice.get('gender', 'unknown')})")
        else:
            print("⚠️  No voices found or voice listing not supported")
        
        # Test 3: Speech generation
        print("\n🔊 Test 3: Speech Generation")
        test_texts = [
            "Hello! This is a test of the PyTTSX3 text-to-speech system.",
            "The voice task manager is now ready to use.",
            "Press the hotkey to add a new task."
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n  Generating speech {i}/{len(test_texts)}: '{text[:50]}...'")
            
            start_time = time.time()
            result = tts.generate_speech(text)
            generation_time = time.time() - start_time
            
            if result['success']:
                print(f"    ✅ Success: {result['output_file']}")
                print(f"    📊 Duration: {result['audio_duration']:.1f}s, Time: {generation_time:.2f}s")
                
                # Check if file exists and has content
                file_path = Path(result['output_file'])
                if file_path.exists():
                    file_size = file_path.stat().st_size
                    print(f"    📁 File size: {file_size} bytes")
                else:
                    print(f"    ⚠️  File not found: {result['output_file']}")
            else:
                print(f"    ❌ Failed: {result.get('error')}")
        
        # Test 4: Voice selection (if multiple voices available)
        if len(voices) > 1:
            print("\n🎭 Test 4: Voice Selection")
            second_voice = voices[1]['name']
            print(f"  Trying to use voice: {second_voice}")
            
            result = tts.generate_speech("Testing voice selection.", voice=second_voice)
            if result['success']:
                print(f"    ✅ Voice selection successful: {result['voice']}")
            else:
                print(f"    ❌ Voice selection failed: {result.get('error')}")
        
        # Test 5: Cleanup
        print("\n🧹 Test 5: Cleanup")
        tts.cleanup()
        print("    ✅ TTS cleanup completed")
        
        print("\n🎉 All PyTTSX3 TTS tests completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you have installed pyttsx3: pip install pyttsx3")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_audio_playback():
    """Test if the generated audio files can be played"""
    print("\n🔊 Testing Audio Playback")
    print("=" * 30)
    
    try:
        from audio_recorder import AudioPlayer
        
        # Find the most recent TTS file
        temp_dir = Path.home() / '.voice_task_manager' / 'temp'
        if temp_dir.exists():
            tts_files = list(temp_dir.glob("pyttsx3_tts_*.wav"))
            if tts_files:
                # Get the most recent file
                latest_file = max(tts_files, key=lambda x: x.stat().st_mtime)
                print(f"🎵 Found TTS file: {latest_file.name}")
                
                # Test playback
                print("🔊 Testing audio playback...")
                player = AudioPlayer()
                player.play_audio(str(latest_file))
                
                print("✅ Audio playback test completed")
                player.cleanup()
            else:
                print("⚠️  No TTS files found to test playback")
        else:
            print("⚠️  Temp directory not found")
            
    except Exception as e:
        print(f"❌ Audio playback test failed: {e}")

if __name__ == "__main__":
    # Test the TTS system
    test_pyttsx3_tts()
    
    # Test audio playback
    test_audio_playback()
    
    print("\n🚀 PyTTSX3 TTS testing completed!")
    print("💡 If all tests pass, you can now use the new TTS system without Hugging Face dependencies!")
