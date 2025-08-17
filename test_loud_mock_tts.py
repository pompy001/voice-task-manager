#!/usr/bin/env python3
"""
Test script to verify loud MockTTS audio
"""

import logging
from text_to_speech import MockTTS
from audio_recorder import AudioPlayer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_loud_mock_tts():
    """Test loud MockTTS audio generation"""
    print("🔊 Loud MockTTS Test")
    print("=" * 40)
    
    try:
        # Test 1: Generate loud audio with MockTTS
        print("\n🎵 Test 1: Generate Loud Audio")
        mock_tts = MockTTS()
        
        test_text = "Hi Ankit, this is a LOUD test of the MockTTS system. Can you hear this clearly now?"
        print(f"📝 Text: {test_text}")
        
        result = mock_tts.generate_speech(test_text)
        if result['success']:
            print(f"✅ Audio generated: {result['output_file']}")
            print(f"📊 Duration: {result['audio_duration']} seconds")
            print(f"📊 Sample rate: {result['sample_rate']} Hz")
        else:
            print(f"❌ Audio generation failed: {result.get('error')}")
            return
        
        # Test 2: Play the loud audio
        print("\n🔊 Test 2: Audio Playback")
        print("   Playing LOUD MockTTS audio through Device 6...")
        print("   You should hear 3 seconds of LOUD multi-frequency tones!")
        
        player = AudioPlayer()
        player.play_audio(result['output_file'])
        
        # Ask user if they heard it
        print("\n👂 Did you hear the LOUD audio clearly?")
        response = input("   Enter 'y' if you heard it, 'n' if not: ").lower().strip()
        
        if response == 'y':
            print("🎉 SUCCESS! Loud MockTTS is working!")
            print("💡 The voice task manager should now speak loudly and clearly")
        else:
            print("❌ Still no audio heard")
            print("🔧 There might be a deeper audio system issue")
            
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
    test_loud_mock_tts()
