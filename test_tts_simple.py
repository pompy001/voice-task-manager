#!/usr/bin/env python3
"""
Simple TTS test script
"""

import logging
from text_to_speech import TTSManager, MockTTS
from audio_recorder import AudioPlayer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_tts():
    """Test TTS functionality"""
    print("🔊 TTS Test")
    print("=" * 30)
    
    try:
        # Test 1: Try TTSManager
        print("\n🎯 Test 1: TTSManager")
        try:
            tts = TTSManager()
            print(f"TTSManager created: {type(tts).__name__}")
            print(f"TTS available: {tts.is_available()}")
            
            if tts.is_available():
                print("✅ TTSManager is available")
                test_text = "Hi Ankit, this is a test of the TTS system."
                result = tts.speak(test_text)
                print(f"TTS result: {result}")
                
                if result['success']:
                    print(f"✅ Audio generated: {result['output_file']}")
                    
                    # Try to play it
                    print("\n🎵 Testing audio playback...")
                    player = AudioPlayer()
                    player.play_audio(result['output_file'])
                    player.cleanup()
                else:
                    print(f"❌ TTS failed: {result.get('error')}")
            else:
                print("⚠️  TTSManager not available")
                
        except Exception as e:
            print(f"❌ TTSManager failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 2: MockTTS
        print("\n🎭 Test 2: MockTTS")
        try:
            mock_tts = MockTTS()
            print(f"MockTTS created: {type(mock_tts).__name__}")
            print(f"MockTTS available: {mock_tts.is_available()}")
            
            test_text = "Hi Ankit, this is a mock TTS test."
            result = mock_tts.generate_speech(test_text)
            print(f"MockTTS result: {result}")
            
            if result['success']:
                print(f"✅ Mock audio generated: {result['output_file']}")
                
                # Try to play it
                print("\n🎵 Testing mock audio playback...")
                player = AudioPlayer()
                player.play_audio(result['output_file'])
                player.cleanup()
            else:
                print(f"❌ MockTTS failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ MockTTS failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tts()
