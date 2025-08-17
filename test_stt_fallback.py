#!/usr/bin/env python3
"""
Test script to verify STT fallback mechanism
"""

import logging
from speech_to_text import SpeechToText, MockSTT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_stt_fallback():
    """Test STT fallback mechanism"""
    print("="*50)
    print("STT Fallback Test")
    print("="*50)
    
    try:
        # Test 1: Try to create real STT
        print("\n🔤 Test 1: Creating Real STT...")
        try:
            stt = SpeechToText()
            if stt.is_available():
                print("✅ Real STT is available")
                stt_type = "Real STT"
            else:
                print("⚠️  Real STT not available, should use MockSTT")
                stt_type = "MockSTT"
        except Exception as e:
            print(f"❌ Real STT failed: {e}")
            stt_type = "MockSTT"
        
        # Test 2: Create MockSTT directly
        print("\n🎭 Test 2: Creating MockSTT...")
        mock_stt = MockSTT()
        if mock_stt.is_available():
            print("✅ MockSTT is available")
        else:
            print("❌ MockSTT not available")
            return
        
        # Test 3: Test transcription with MockSTT
        print("\n📝 Test 3: Testing MockSTT Transcription...")
        result = mock_stt.transcribe_audio("fake_audio.wav")
        print(f"📝 Transcription result: {result}")
        
        if result['success']:
            print(f"✅ MockSTT working! Text: '{result['text']}'")
        else:
            print(f"❌ MockSTT failed: {result.get('error', 'Unknown error')}")
        
        # Test 4: Test multiple transcriptions
        print("\n🔄 Test 4: Testing Multiple MockSTT Calls...")
        for i in range(3):
            result = mock_stt.transcribe_audio("fake_audio.wav")
            print(f"Call {i+1}: '{result['text']}'")
        
        # Cleanup
        mock_stt.cleanup()
        print("\n🧹 MockSTT cleanup completed")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_stt_fallback()
