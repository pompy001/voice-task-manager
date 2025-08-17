#!/usr/bin/env python3
"""
Alternative Voice Task Manager using keyboard library (more reliable on Windows)
"""

import logging
import sys
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional
import platform

# Import our modules
from audio_recorder import AudioRecorder, AudioPlayer
from speech_to_text import SpeechToText, MockSTT
from text_to_speech import TextToSpeech, MockTTS, TTSManager
from openai_client import OpenAIClient, MockOpenAIClient
from excel_manager import ExcelTaskManager
from config import HOTKEY_COMBO, LOG_FILE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class VoiceTaskManagerKeyboard:
    """Main voice task management system using keyboard library"""
    
    def __init__(self):
        """Initialize the voice task manager"""
        self.running = False
        self.current_recording = None
        self.recording_file = None
        self.hotkey_registered = False
        self.processing_audio = False  # Flag to prevent cleanup during processing
        
        # Initialize components
        self._initialize_components()
        
        # Setup hotkey listener
        self._setup_hotkey_listener()
        
        logger.info("Voice Task Manager (Keyboard) initialized successfully")
    
    def _initialize_components(self):
        """Initialize all system components"""
        try:
            # Initialize audio components
            self.audio_recorder = AudioRecorder()
            self.audio_player = AudioPlayer()
            
            # Initialize STT (with fallback to mock)
            try:
                self.stt = SpeechToText()
                if not self.stt.is_available():
                    logger.warning("STT not available, using mock")
                    self.stt = MockSTT()
                else:
                    logger.info("STT component initialized successfully")
            except Exception as e:
                logger.warning(f"STT initialization failed, using mock: {e}")
                self.stt = MockSTT()
                logger.info("Using MockSTT for testing")
            
            # Initialize TTS (with fallback to mock)
            try:
                logger.info("Initializing TTS component...")
                self.tts = TTSManager()
                logger.info(f"TTSManager created, checking availability...")
                
                if not self.tts.is_available():
                    logger.warning("TTS not available, using mock")
                    self.tts = MockTTS()
                    logger.info("MockTTS initialized successfully")
                else:
                    logger.info("TTS component initialized successfully")
                    
            except Exception as e:
                logger.warning(f"TTS initialization failed, using mock: {e}")
                self.tts = MockTTS()
                logger.info("Using MockTTS for testing")
            
            # Initialize OpenAI client (with fallback to mock)
            try:
                self.ollama = OpenAIClient()
                if not self.ollama.is_connected():
                    logger.warning("OpenAI not available, using mock")
                    self.ollama = MockOpenAIClient()
            except Exception as e:
                logger.warning(f"OpenAI initialization failed, using mock: {e}")
                self.ollama = MockOpenAIClient()
            
            # Initialize Excel manager
            self.excel_manager = ExcelTaskManager()
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            raise
    
    def _setup_hotkey_listener(self):
        """Setup global hotkey listener using keyboard library"""
        try:
            import keyboard
            
            # Determine OS and set appropriate hotkey
            os_name = platform.system().lower()
            hotkey_combo = HOTKEY_COMBO.get(os_name, HOTKEY_COMBO['windows'])
            
            # Convert to keyboard library format
            hotkey_string = '+'.join(hotkey_combo)
            logger.info(f"Setting up hotkey: {hotkey_string}")
            
            # Setup hotkey listener
            def on_hotkey():
                logger.info("Hotkey pressed - starting voice input")
                self._handle_hotkey_press()
            
            # Register the hotkey
            keyboard.add_hotkey(hotkey_string, on_hotkey)
            self.hotkey_registered = True
            logger.info(f"Hotkey listener active: {hotkey_string}")
            
        except ImportError:
            logger.error("keyboard library not available - hotkey functionality disabled")
            logger.info("Install with: pip install keyboard")
        except Exception as e:
            logger.error(f"Error setting up hotkey listener: {e}")
            logger.error(f"Hotkey combo: {hotkey_combo}")
            logger.error(f"OS detected: {platform.system()}")
            # Try to continue without hotkey functionality
            logger.info("Continuing without hotkey functionality - you can still use voice commands directly")
    
    def _handle_hotkey_press(self):
        """Handle hotkey press event"""
        if self.current_recording:
            logger.warning("Recording already in progress, ignoring hotkey")
            return
        
        # Start recording in a separate thread
        recording_thread = threading.Thread(target=self._start_voice_input)
        recording_thread.daemon = True
        recording_thread.start()
    
    def _start_voice_input(self):
        """Start voice input process"""
        try:
            logger.info("Starting voice input process")
            self.processing_audio = True  # Set processing flag
            
            # Personalized greeting
            self._speak_response("Hi Ankit, what task would you like to add?")
            
            # Start recording
            logger.info("Starting audio recording...")
            self.recording_file = self.audio_recorder.start_recording()
            self.current_recording = True
            
            logger.info(f"Recording file: {self.recording_file}")
            # Wait for recording to complete (either by key press or timeout)
            logger.info("Waiting for recording to complete...")
            recording_start_time = time.time()
            max_recording_time = 30  # Maximum 30 seconds
            
            print("\n🎤 RECORDING - Speak your task now!")
            print("   Press '2' key to stop recording...")
            
            while self.audio_recorder.is_recording():
                # Check if '2' key is pressed to stop recording
                try:
                    import keyboard
                    if keyboard.is_pressed('2'):
                        logger.info("Stop key '2' pressed - stopping recording")
                        print("\n⏹️  Stop key pressed - stopping recording...")
                        self.audio_recorder.stop_recording()
                        break
                except:
                    pass
                
                # Check for timeout
                if time.time() - recording_start_time > max_recording_time:
                    logger.info("Maximum recording time reached - stopping recording")
                    print("\n⏰ Timeout reached - stopping recording...")
                    self.audio_recorder.stop_recording()
                    break
                
                time.sleep(0.1)
            
            print("\n✅ Recording stopped - processing audio...")
            logger.info("Recording completed, processing audio...")
            self.current_recording = False
            
            # Small delay to ensure recording is fully stopped
            time.sleep(0.5)
            
            if self.recording_file:
                # Check if file exists and has content
                from pathlib import Path
                if Path(self.recording_file).exists():
                    file_size = Path(self.recording_file).stat().st_size
                    logger.info(f"Audio file size: {file_size} bytes")
                    if file_size > 0:
                        logger.info("Audio file is valid, processing...")
                        # Process the recording
                        self._process_voice_input(self.recording_file)
                    else:
                        logger.error("Audio file is empty!")
                        self._speak_response("Sorry, the recording was empty. Please try again.")
                else:
                    logger.error("Audio file not found!")
                    self._speak_response("Sorry, there was an error saving the recording.")
            else:
                logger.error("No recording file generated")
                self._speak_response("Sorry, there was an error recording your voice.")
                
        except Exception as e:
            logger.error(f"Error in voice input process: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self._speak_response("Sorry, there was an error processing your voice input.")
            self.current_recording = False
        finally:
            self.processing_audio = False  # Clear processing flag
    
    def _process_voice_input(self, audio_file: str):
        """Process recorded voice input"""
        try:
            logger.info(f"Processing voice input: {audio_file}")
            
            # Step 1: Convert speech to text
            self._speak_response("Processing your voice input...")
            logger.info("Starting speech-to-text conversion...")
            
            stt_result = self.stt.transcribe_audio(audio_file)
            logger.info(f"STT result: {stt_result}")
            
            if not stt_result['success']:
                logger.error(f"STT failed: {stt_result.get('error', 'Unknown error')}")
                self._speak_response("Sorry, I couldn't understand what you said. Please try again.")
                return
            
            transcribed_text = stt_result['text']
            logger.info(f"Transcribed text: '{transcribed_text}'")
            
            # Step 2: Parse task using OpenAI
            self._speak_response("Analyzing your task...")
            logger.info("Starting task parsing...")
            
            parse_result = self.ollama.parse_task(transcribed_text)
            logger.info(f"Parse result: {parse_result}")
            
            if not parse_result['success']:
                # Handle missing fields or parsing errors
                logger.warning(f"Task parsing failed: {parse_result}")
                self._handle_parsing_error(parse_result)
                return
            
            task_data = parse_result['parsed_data']
            logger.info(f"Parsed task data: {task_data}")
            
            # Step 3: Validate task data
            logger.info("Starting task validation...")
            validation_result = self.ollama.validate_task(task_data)
            logger.info(f"Validation result: {validation_result}")
            
            if not validation_result['success']:
                logger.error(f"Task validation failed: {validation_result}")
                self._speak_response("The task data couldn't be validated. Please try again.")
                return
            
            if not validation_result['validation_result'].get('valid', False):
                errors = validation_result['validation_result'].get('errors', [])
                error_message = f"Task validation failed: {', '.join(errors)}"
                logger.error(error_message)
                self._speak_response(error_message)
                return
            
            # Step 4: Add task to Excel
            self._speak_response("Adding your task to the system...")
            logger.info("Adding task to Excel...")
            
            add_result = self.excel_manager.add_task(task_data)
            logger.info(f"Excel add result: {add_result}")
            
            if not add_result['success']:
                logger.error(f"Failed to add task: {add_result}")
                self._speak_response("Sorry, there was an error adding your task. Please try again.")
                return
            
            # Step 5: Confirm task addition
            confirmation_message = f"Task added successfully! Your {task_data['priority']} priority task '{task_data['task']}' has been recorded and is due on {task_data['expected_date']}."
            self._speak_response(confirmation_message)
            
            logger.info(f"Task added successfully: {add_result}")
            
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self._speak_response("Sorry, there was an error processing your task. Please try again.")
    
    def _handle_parsing_error(self, parse_result: Dict[str, Any]):
        """Handle parsing errors and prompt for missing information"""
        error_type = parse_result.get('error')
        
        if error_type == 'missing_field':
            field = parse_result.get('field', '')
            message = parse_result.get('message', '')
            
            if field == 'task':
                prompt = "I couldn't identify the task description. Please repeat the task more clearly."
            elif field == 'assigned_by':
                prompt = "Who assigned this task? Please specify the person's name."
            elif field == 'priority':
                prompt = "What priority level should this task have? Please say urgent, high, medium, or low."
            elif field == 'expected_date':
                prompt = "When is this task due? Please specify the completion date."
            else:
                prompt = f"Please provide the {field} information: {message}"
            
            self._speak_response(prompt)
            
            # Start a new recording for the missing information
            self._record_missing_information(field, prompt)
        else:
            error_message = parse_result.get('message', 'Unknown parsing error')
            self._speak_response(f"Sorry, I couldn't parse your request: {error_message}")
    
    def _record_missing_information(self, field: str, prompt: str):
        """Record missing information from user"""
        try:
            logger.info(f"Recording missing information for field: {field}")
            
            # Start recording for missing information
            self.recording_file = self.audio_recorder.start_recording(duration=10)
            self.current_recording = True
            
            # Wait for recording to complete
            while self.audio_recorder.is_recording():
                time.sleep(0.1)
            
            self.current_recording = False
            
            if self.recording_file:
                # Process the missing information
                self._process_missing_information(field, self.recording_file)
            else:
                logger.error("No recording file generated for missing information")
                self._speak_response("Sorry, I couldn't record your response. Please try again.")
                
        except Exception as e:
            logger.error(f"Error recording missing information: {e}")
            self._speak_response("Sorry, there was an error recording your response.")
            self.current_recording = False
    
    def _process_missing_information(self, field: str, audio_file: str):
        """Process recorded missing information"""
        try:
            # Convert speech to text
            stt_result = self.stt.transcribe_audio(audio_file)
            
            if not stt_result['success']:
                self._speak_response("Sorry, I couldn't understand your response. Please try again.")
                return
            
            response_text = stt_result['text']
            logger.info(f"Missing information response for {field}: {response_text}")
            
            # For now, just acknowledge the response
            # In a full implementation, you would update the task data and continue
            self._speak_response(f"Thank you for providing the {field} information. I've recorded '{response_text}'.")
            
        except Exception as e:
            logger.error(f"Error processing missing information: {e}")
            self._speak_response("Sorry, there was an error processing your response.")
    
    def _speak_response(self, text: str):
        """Convert text to speech and play it"""
        try:
            logger.info(f"Speaking response: {text}")
            logger.info(f"TTS type: {type(self.tts).__name__}")
            logger.info(f"TTS available: {self.tts.is_available()}")
            
            if hasattr(self.tts, 'speak'):
                # Using TTSManager
                logger.info("Using TTSManager.speak method")
                result = self.tts.speak(text)
            else:
                # Using direct TTS
                logger.info("Using direct TTS.generate_speech method")
                result = self.tts.generate_speech(text)
            
            logger.info(f"TTS result: {result}")
            
            if result['success']:
                # Play the audio
                logger.info(f"Playing audio file: {result['output_file']}")
                self.audio_player.play_audio(result['output_file'])
            else:
                logger.error(f"TTS failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error in speech response: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def handle_voice_query(self, query: str):
        """Handle voice queries about tasks"""
        try:
            logger.info(f"Processing voice query: {query}")
            
            # Get available tasks
            available_tasks = self.excel_manager.get_all_tasks()
            
            # Get response from OpenAI
            response_result = self.ollama.answer_query(query, available_tasks)
            
            if not response_result['success']:
                logger.error(f"Query response failed: {response_result}")
                self._speak_response("Sorry, I couldn't process your query. Please try again.")
                return
            
            response_text = response_result['response']
            logger.info(f"Query response: {response_text}")
            
            # Speak the response
            self._speak_response(response_text)
            
        except Exception as e:
            logger.error(f"Error handling voice query: {e}")
            self._speak_response("Sorry, there was an error processing your query.")
    
    def start(self):
        """Start the voice task manager"""
        try:
            logger.info("Starting Voice Task Manager (Keyboard)...")
            self.running = True
            
            # Speak startup message
            startup_message = "Voice Task Manager is now active. Press Ctrl+Shift+V to add a new task. When recording, press '2' to stop."
            self._speak_response(startup_message)
            
            # Keep the main thread running
            logger.info("Voice Task Manager is running. Press Ctrl+C to stop.")
            try:
                while self.running:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
                # Don't stop immediately if processing audio
                if self.processing_audio:
                    logger.info("Audio processing in progress, waiting for completion...")
                    while self.processing_audio and self.running:
                        time.sleep(0.1)
                    logger.info("Audio processing completed, proceeding with shutdown")
                
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the voice task manager"""
        logger.info("Stopping Voice Task Manager...")
        self.running = False
        
        # Stop any ongoing recording
        if self.current_recording:
            self.audio_recorder.stop_recording()
        
        # Wait for audio processing to complete
        if self.processing_audio:
            logger.info("Waiting for audio processing to complete...")
            while self.processing_audio:
                time.sleep(0.1)
            logger.info("Audio processing completed")
        
        # Unhook keyboard hotkeys
        if self.hotkey_registered:
            try:
                import keyboard
                keyboard.unhook_all()
                logger.info("Keyboard hotkeys unhooked")
            except Exception as e:
                logger.error(f"Error unhooking keyboard: {e}")
        
        # Cleanup components
        try:
            self.audio_recorder.cleanup()
            self.audio_player.cleanup()
            self.stt.cleanup()
            self.tts.cleanup()
            self.ollama.cleanup()
            self.excel_manager.cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
        logger.info("Voice Task Manager stopped")


def main():
    """Main entry point"""
    try:
        # Create and start the voice task manager
        manager = VoiceTaskManagerKeyboard()
        
        # Start the manager
        manager.start()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
