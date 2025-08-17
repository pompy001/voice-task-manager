#!/usr/bin/env python3
"""
Test script to verify speaker device selection
"""

import logging
from audio_recorder import AudioPlayer
from text_to_speech import MockTTS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_speaker_selection():
    """Test speaker device selection"""
    print("🔊 Speaker Selection Test")
    print("=" * 40)
    
    try:
        # Test 1: Create AudioPlayer (should find preferred device)
        print("\n🎯 Test 1: AudioPlayer Device Selection")
        player = AudioPlayer()
        
        if hasattr(player, 'preferred_device') and player.preferred_device is not None:
            print(f"✅ Preferred device found: {player.preferred_device}")
        else:
            print("⚠️  No preferred device found, using default")
        
        # Test 2: Generate test audio with MockTTS
        print("\n🎵 Test 2: Generate Test Audio")
        mock_tts = MockTTS()
        test_text = "Hi Ankit, this is a test of the speaker selection. Can you hear this?"
        
        result = mock_tts.generate_speech(test_text)
        if result['success']:
            print(f"✅ Audio generated: {result['output_file']}")
        else:
            print(f"❌ Audio generation failed: {result.get('error')}")
            return
        
        # Test 3: Play audio through selected device
        print("\n🔊 Test 3: Audio Playback")
        print("   Playing test audio through selected device...")
        print("   You should hear: 'Hi Ankit, this is a test of the speaker selection. Can you hear this?'")
        
        player.play_audio(result['output_file'])
        
        # Ask user if they heard it
        print("\n👂 Did you hear the audio clearly?")
        response = input("   Enter 'y' if you heard it, 'n' if not: ").lower().strip()
        
        if response == 'y':
            print("🎉 SUCCESS! Speaker selection is working!")
            print("💡 The voice task manager should now speak through the right device")
        else:
            print("❌ Still no audio heard")
            print("🔧 Let's try a different approach...")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            player.cleanup()
            print("\n🧹 Audio player cleaned up")
        except:
            pass

if __name__ == "__main__":
    test_speaker_selection()
