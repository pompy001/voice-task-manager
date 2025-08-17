#!/usr/bin/env python3
"""
Test script to debug voice processing step by step
"""

import time
import logging
from pathlib import Path
from audio_recorder import AudioRecorder
from speech_to_text import SpeechToText, MockSTT
from openai_client import OpenAIClient, MockOpenAIClient
from excel_manager import ExcelTaskManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_voice_processing():
    """Test voice processing step by step"""
    print("="*50)
    print("Voice Processing Debug Test")
    print("="*50)
    
    try:
        # Step 1: Test audio recording
        print("\n🎤 Step 1: Testing Audio Recording...")
        recorder = AudioRecorder()
        audio_file = recorder.start_recording()
        
        if audio_file:
            print(f"✅ Recording started: {audio_file}")
            print("🗣️  Speak something now...")
            
            # Wait for recording to complete
            while recorder.is_recording():
                time.sleep(0.1)
            
            print("✅ Recording completed!")
            print(f"📁 Audio saved to: {audio_file}")
            
            # Check if file exists and has content
            if Path(audio_file).exists():
                file_size = Path(audio_file).stat().st_size
                print(f"📊 Audio file size: {file_size} bytes")
                if file_size > 0:
                    print("✅ Audio file is valid")
                else:
                    print("❌ Audio file is empty!")
                    return
            else:
                print("❌ Audio file not found!")
                return
        else:
            print("❌ Failed to start recording")
            return
        
        # Step 2: Test Speech-to-Text
        print("\n🔤 Step 2: Testing Speech-to-Text...")
        try:
            stt = SpeechToText()
            if stt.is_available():
                print("✅ STT component available")
            else:
                print("⚠️  STT not available, using mock")
                stt = MockSTT()
        except Exception as e:
            print(f"⚠️  STT failed, using mock: {e}")
            stt = MockSTT()
        
        print("🔄 Converting speech to text...")
        stt_result = stt.transcribe_audio(audio_file)
        print(f"📝 STT Result: {stt_result}")
        
        if not stt_result['success']:
            print(f"❌ STT failed: {stt_result.get('error', 'Unknown error')}")
            return
        
        transcribed_text = stt_result['text']
        print(f"✅ Transcribed text: '{transcribed_text}'")
        
        # Step 3: Test OpenAI Client
        print("\n🤖 Step 3: Testing OpenAI Client...")
        try:
            openai_client = OpenAIClient()
            if openai_client.is_connected():
                print("✅ OpenAI client connected")
            else:
                print("⚠️  OpenAI not available, using mock")
                openai_client = MockOpenAIClient()
        except Exception as e:
            print(f"⚠️  OpenAI failed, using mock: {e}")
            openai_client = MockOpenAIClient()
        
        # Step 4: Test Task Parsing
        print("\n📋 Step 4: Testing Task Parsing...")
        print("🔄 Parsing task from text...")
        parse_result = openai_client.parse_task(transcribed_text)
        print(f"📝 Parse Result: {parse_result}")
        
        if not parse_result['success']:
            print(f"❌ Task parsing failed: {parse_result}")
            return
        
        task_data = parse_result['parsed_data']
        print(f"✅ Parsed task data: {task_data}")
        
        # Step 5: Test Excel Manager
        print("\n📊 Step 5: Testing Excel Manager...")
        try:
            excel_manager = ExcelTaskManager()
            print("✅ Excel manager initialized")
            
            print("🔄 Adding task to Excel...")
            add_result = excel_manager.add_task(task_data)
            print(f"📝 Add Result: {add_result}")
            
            if add_result['success']:
                print("✅ Task added successfully!")
            else:
                print(f"❌ Failed to add task: {add_result}")
                
        except Exception as e:
            print(f"❌ Excel manager error: {e}")
        
        # Cleanup
        recorder.cleanup()
        print("\n🧹 Cleanup completed")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_voice_processing()
