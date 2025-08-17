#!/usr/bin/env python3
"""
Universal Voice Task Manager - Cross-platform (Windows, macOS, Linux)
Automatically detects OS and uses appropriate hotkey library
"""

import os
import sys
import time
import logging
import threading
import traceback
from pathlib import Path
from typing import Optional, Dict, Any

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import HOTKEY_COMBO, AUDIO_CONFIG, TEMP_DIR
from audio_recorder import AudioRecorder
from speech_to_text import SpeechToText
from text_to_speech import TextToSpeech
from openai_client import OpenAIClient
from excel_manager import ExcelTaskManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path.home() / '.voice_task_manager' / 'logs' / 'voice_task_manager.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class UniversalVoiceTaskManager:
    """Cross-platform voice task management system"""
    
    def __init__(self):
        self.running = False
        self.current_recording = False
        self.recording_file = None
        self.processing_audio = False
        
        # Initialize components
        self._initialize_components()
        
        # Setup hotkey based on OS
        self._setup_cross_platform_hotkey()
        
        logger.info("Universal Voice Task Manager initialized successfully")
    
    def _initialize_components(self):
        """Initialize all system components"""
        try:
            # Create temp directory
            TEMP_DIR.mkdir(parents=True, exist_ok=True)
            
            # Initialize audio recorder
            logger.info("Initializing audio recorder...")
            self.audio_recorder = AudioRecorder()
            logger.info("Audio recorder initialized successfully")
            
            # Initialize STT component
            logger.info("Initializing STT component...")
            self.stt = SpeechToText()
            if self.stt.is_available():
                logger.info("STT component initialized successfully")
            else:
                logger.warning("STT not available, using mock")
                from speech_to_text import MockSTT
                self.stt = MockSTT()
                logger.info("MockSTT initialized successfully")
            
            # Initialize TTS component
            logger.info("Initializing TTS component...")
            self.tts = TextToSpeech()
            if self.tts.is_available():
                logger.info("TTS component initialized successfully")
            else:
                logger.warning("TTS not available, using mock")
                from text_to_speech import MockTTS
                self.tts = MockTTS()
                logger.info("MockTTS initialized successfully")
            
            # Initialize OpenAI client
            logger.info("Initializing OpenAI client...")
            self.openai_client = OpenAIClient()
            logger.info("OpenAI client initialized successfully")
            
            # Initialize Excel manager
            logger.info("Initializing Excel manager...")
            self.excel_manager = ExcelTaskManager()
            logger.info("Excel manager initialized successfully")
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def _setup_cross_platform_hotkey(self):
        """Setup hotkey based on operating system"""
        import platform
        system = platform.system().lower()
        
        logger.info(f"Detected operating system: {system}")
        
        if system == "darwin":  # macOS
            self._setup_macos_hotkey()
        elif system == "windows":
            self._setup_windows_hotkey()
        else:  # Linux and others
            self._setup_linux_hotkey()
    
    def _setup_macos_hotkey(self):
        """Setup hotkey for macOS using pynput"""
        try:
            from pynput import keyboard
            
            # Use macOS-specific hotkey (Cmd+Shift+V)
            hotkey = HOTKEY_COMBO.get('macos', ['cmd', 'shift', 'v'])
            logger.info(f"Setting up macOS hotkey: {'+'.join(hotkey)}")
            
            # Convert to pynput format
            key_objects = []
            for key_str in hotkey:
                if key_str == 'cmd':
                    key_objects.append(keyboard.Key.cmd)
                elif key_str == 'ctrl':
                    key_objects.append(keyboard.Key.ctrl)
                elif key_str == 'shift':
                    key_objects.append(keyboard.Key.shift)
                elif key_str == 'alt':
                    key_objects.append(keyboard.Key.alt)
                else:
                    key_objects.append(key_str)
            
            hotkey_tuple = tuple(key_objects)
            logger.info(f"Hotkey tuple: {hotkey_tuple}")
            
            # Setup global hotkey listener
            self.hotkey_listener = keyboard.GlobalHotKeys({hotkey_tuple: self._on_hotkey})
            self.hotkey_listener.start()
            
            logger.info(f"macOS hotkey listener active: {'+'.join(hotkey)}")
            
        except ImportError:
            logger.error("pynput not available for macOS hotkey - install with: pip install pynput")
            self.hotkey_listener = None
        except Exception as e:
            logger.error(f"Error setting up macOS hotkey: {e}")
            logger.error(traceback.format_exc())
            self.hotkey_listener = None
    
    def _setup_windows_hotkey(self):
        """Setup hotkey for Windows using keyboard library"""
        try:
            import keyboard
            
            # Use Windows-specific hotkey (Ctrl+Shift+V)
            hotkey = HOTKEY_COMBO.get('windows', ['ctrl', 'shift', 'v'])
            logger.info(f"Setting up Windows hotkey: {'+'.join(hotkey)}")
            
            # Convert to keyboard library format
            hotkey_string = '+'.join(hotkey)
            logger.info(f"Hotkey string: {hotkey_string}")
            
            # Setup global hotkey listener
            keyboard.add_hotkey(hotkey_string, self._on_hotkey)
            
            logger.info(f"Windows hotkey listener active: {hotkey_string}")
            
        except ImportError:
            logger.error("keyboard library not available for Windows hotkey - install with: pip install keyboard")
        except Exception as e:
            logger.error(f"Error setting up Windows hotkey: {e}")
            logger.error(traceback.format_exc())
    
    def _setup_linux_hotkey(self):
        """Setup hotkey for Linux using pynput"""
        try:
            from pynput import keyboard
            
            # Use Linux-specific hotkey (Ctrl+Shift+V)
            hotkey = HOTKEY_COMBO.get('linux', ['ctrl', 'shift', 'v'])
            logger.info(f"Setting up Linux hotkey: {'+'.join(hotkey)}")
            
            # Convert to pynput format
            key_objects = []
            for key_str in hotkey:
                if key_str == 'ctrl':
                    key_objects.append(keyboard.Key.ctrl)
                elif key_str == 'shift':
                    key_objects.append(keyboard.Key.shift)
                elif key_str == 'alt':
                    key_objects.append(keyboard.Key.alt)
                else:
                    key_objects.append(key_str)
            
            hotkey_tuple = tuple(key_objects)
            logger.info(f"Hotkey tuple: {hotkey_tuple}")
            
            # Setup global hotkey listener
            self.hotkey_listener = keyboard.GlobalHotKeys({hotkey_tuple: self._on_hotkey})
            self.hotkey_listener.start()
            
            logger.info(f"Linux hotkey listener active: {'+'.join(hotkey)}")
            
        except ImportError:
            logger.error("pynput not available for Linux hotkey - install with: pip install pynput")
            self.hotkey_listener = None
        except Exception as e:
            logger.error(f"Error setting up Linux hotkey: {e}")
            logger.error(traceback.format_exc())
            self.hotkey_listener = None
    
    def _on_hotkey(self):
        """Handle hotkey press"""
        if self.current_recording:
            logger.info("Hotkey pressed while already recording - ignoring")
            return
        
        logger.info("Hotkey pressed - starting voice input")
        self._start_voice_input()
    
    def _start_voice_input(self):
        """Start voice input process"""
        try:
            logger.info("Starting voice input process")
            self.processing_audio = True  # Set processing flag
            
            # Personalized greeting
            self._speak_response("Hi Ankit, what task would you like to add?")
            
            # Start recording
            self.recording_file = self.audio_recorder.start_recording()
            if not self.recording_file:
                logger.error("Failed to start recording")
                return
            
            self.current_recording = True
            logger.info(f"Recording file: {self.recording_file}")
            logger.info("Press '2' key to stop recording...")
            
            # Wait for recording to complete (either by key press or timeout)
            logger.info("Waiting for recording to complete...")
            recording_start_time = time.time()
            max_recording_time = 30  # Maximum 30 seconds
            
            print("\n🎤 RECORDING - Speak your task now!")
            print("   Press '2' key to stop recording...")
            
            while self.audio_recorder.is_recording():
                # Check if '2' key is pressed to stop recording
                try:
                    import platform
                    system = platform.system().lower()
                    
                    if system == "windows":
                        import keyboard
                        if keyboard.is_pressed('2'):
                            logger.info("Stop key '2' pressed - stopping recording")
                            print("\n⏹️  Stop key pressed - stopping recording...")
                            self.audio_recorder.stop_recording()
                            break
                    else:
                        # For macOS/Linux, we'll use timeout-based recording
                        # since we can't easily detect key presses without pynput
                        pass
                        
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
                self._process_voice_input(self.recording_file)
            
        except Exception as e:
            logger.error(f"Error in voice input: {e}")
            logger.error(traceback.format_exc())
            self._speak_response("Sorry, there was an error processing your voice input")
        finally:
            self.processing_audio = False  # Clear processing flag
    
    def _process_voice_input(self, audio_file: str):
        """Process recorded voice input"""
        try:
            logger.info("Processing voice input...")
            
            # Convert speech to text
            logger.info("Converting speech to text...")
            stt_result = self.stt.transcribe(audio_file)
            
            if not stt_result['success']:
                logger.error(f"STT failed: {stt_result.get('error')}")
                self._speak_response("Sorry, I couldn't understand what you said. Please try again.")
                return
            
            text = stt_result['text']
            logger.info(f"Transcribed text: {text}")
            
            if not text.strip():
                self._speak_response("I didn't hear anything. Please try again.")
                return
            
            # Parse task using OpenAI
            logger.info("Parsing task with OpenAI...")
            parse_result = self.openai_client.parse_task(text)
            
            if not parse_result['success']:
                logger.error(f"Task parsing failed: {parse_result.get('error')}")
                self._speak_response(f"Sorry, I couldn't parse your request: {parse_result.get('error')}")
                return
            
            task_data = parse_result['task_data']
            logger.info(f"Parsed task data: {task_data}")
            
            # Validate task data
            logger.info("Validating task data...")
            validation_result = self.openai_client.validate_task(task_data)
            
            if not validation_result['success']:
                logger.error(f"Task validation failed: {validation_result.get('error')}")
                self._speak_response(f"Sorry, I couldn't validate your task: {validation_result.get('error')}")
                return
            
            # Add task to Excel
            logger.info("Adding task to Excel...")
            add_result = self.excel_manager.add_task(task_data)
            
            if not add_result['success']:
                logger.error(f"Failed to add task: {add_result.get('error')}")
                self._speak_response("Sorry, I couldn't save your task. Please try again.")
                return
            
            # Success response
            task_summary = f"Task added successfully: {task_data.get('task', 'Unknown task')}"
            logger.info(task_summary)
            self._speak_response(task_summary)
            
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            logger.error(traceback.format_exc())
            self._speak_response("Sorry, there was an error processing your task. Please try again.")
    
    def _speak_response(self, text: str):
        """Speak a response using TTS"""
        try:
            logger.info(f"Speaking response: {text}")
            
            # Log TTS type and availability
            tts_type = type(self.tts).__name__
            logger.info(f"TTS type: {tts_type}")
            logger.info(f"TTS available: {self.tts.is_available()}")
            
            # Generate speech
            if hasattr(self.tts, 'generate_speech'):
                logger.info("Using direct TTS.generate_speech method")
                result = self.tts.generate_speech(text)
            else:
                logger.info("Using TTSManager.speak method")
                result = self.tts.speak(text)
            
            logger.info(f"TTS result: {result}")
            
            if result['success']:
                # Play the audio
                audio_file = result['output_file']
                logger.info(f"Playing audio file: {audio_file}")
                self.audio_recorder.player.play_audio(audio_file)
            else:
                logger.error(f"TTS failed: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error in TTS: {e}")
            logger.error(traceback.format_exc())
    
    def start(self):
        """Start the voice task manager"""
        try:
            self.running = True
            logger.info("Starting Universal Voice Task Manager...")
            
            # Speak startup message
            startup_message = "Voice Task Manager is now active. Press the hotkey to add a new task."
            self._speak_response(startup_message)
            
            logger.info("Universal Voice Task Manager is running. Press Ctrl+C to stop.")
            
            # Main loop
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
            logger.error(traceback.format_exc())
        finally:
            self.stop()
    
    def stop(self):
        """Stop the voice task manager"""
        try:
            logger.info("Stopping Universal Voice Task Manager...")
            self.running = False
            
            # Wait for audio processing to complete
            if self.processing_audio:
                logger.info("Waiting for audio processing to complete...")
                while self.processing_audio:
                    time.sleep(0.1)
                logger.info("Audio processing completed")
            
            # Stop hotkey listeners
            if hasattr(self, 'hotkey_listener') and self.hotkey_listener:
                try:
                    self.hotkey_listener.stop()
                    logger.info("Hotkey listener stopped")
                except Exception as e:
                    logger.error(f"Error stopping hotkey listener: {e}")
            
            # Unhook keyboard hotkeys (Windows)
            try:
                import platform
                if platform.system().lower() == "windows":
                    import keyboard
                    keyboard.unhook_all()
                    logger.info("Keyboard hotkeys unhooked")
            except Exception as e:
                logger.error(f"Error unhooking keyboard: {e}")
            
            # Cleanup components
            try:
                if hasattr(self, 'audio_recorder'):
                    self.audio_recorder.cleanup()
                    logger.info("Audio recorder cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up audio recorder: {e}")
            
            try:
                if hasattr(self, 'stt'):
                    self.stt.cleanup()
                    logger.info("STT model cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up STT: {e}")
            
            try:
                if hasattr(self, 'tts'):
                    self.tts.cleanup()
                    logger.info("TTS cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up TTS: {e}")
            
            try:
                if hasattr(self, 'openai_client'):
                    self.openai_client.cleanup()
                    logger.info("OpenAI client cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up OpenAI client: {e}")
            
            try:
                if hasattr(self, 'excel_manager'):
                    self.excel_manager.cleanup()
                    logger.info("Excel task manager cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up Excel manager: {e}")
            
            logger.info("Universal Voice Task Manager stopped")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            logger.error(traceback.format_exc())

def main():
    """Main function"""
    try:
        manager = UniversalVoiceTaskManager()
        manager.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
