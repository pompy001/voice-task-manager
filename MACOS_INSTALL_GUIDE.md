# macOS Installation Guide for Voice Task Manager

## 🍎 **macOS Compatibility**

This system is fully compatible with macOS and automatically detects your OS to use the appropriate hotkey library (`pynput`).

## 🚀 **Quick Installation**

### Option 1: Universal Installer (Recommended)
```bash
python install_universal.py
```

### Option 2: Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Set up API key
python configure_api.py

# Test the system
python test_system.py

# Run the voice task manager
python voice_task_manager_universal.py
```

## 🔧 **System Requirements**

- **macOS**: 10.14 (Mojave) or later
- **Python**: 3.8 or higher
- **Audio**: Built-in speakers or external audio output
- **Permissions**: Microphone access for voice recording

## 📦 **Dependencies**

### Core Dependencies
- **PyAudio**: Audio recording and playback
- **pynput**: Global hotkey detection (Cmd+Shift+V)
- **faster-whisper**: Speech-to-text conversion
- **kittentts**: Text-to-speech synthesis
- **openai**: AI-powered task parsing
- **openpyxl**: Excel file management

### Installation Commands
```bash
# Audio processing
pip install pyaudio
pip install faster-whisper
pip install kittentts

# Hotkey support
pip install pynput

# AI and data processing
pip install openai
pip install openpyxl
pip install python-dotenv

# Utilities
pip install soundfile
pip install numpy
pip install requests
pip install python-dateutil
```

## 🎯 **macOS-Specific Features**

### Hotkey Configuration
- **Default Hotkey**: `Cmd+Shift+V`
- **Library**: `pynput` (reliable on macOS)
- **Permissions**: May require accessibility permissions

### Audio Device Detection
- **Automatic**: Detects built-in speakers and external audio
- **Fallback**: Uses default system audio output
- **Compatibility**: Works with AirPods, external speakers, etc.

## 🔐 **Permission Setup**

### Microphone Access
1. **System Preferences** → **Security & Privacy** → **Privacy**
2. **Microphone** → **Add your terminal app**
3. **Restart terminal** after granting permissions

### Accessibility Permissions (if needed)
1. **System Preferences** → **Security & Privacy** → **Privacy**
2. **Accessibility** → **Add your terminal app**
3. **Check the box** for your terminal app

## 🚨 **Common Issues & Solutions**

### Issue: PyAudio Installation Fails
```bash
# Solution 1: Install via Homebrew
brew install portaudio
pip install pyaudio

# Solution 2: Use conda
conda install pyaudio
```

### Issue: Microphone Not Working
1. Check **System Preferences** → **Sound** → **Input**
2. Ensure microphone is selected and volume is up
3. Grant microphone permissions to terminal

### Issue: Hotkey Not Responding
1. Check accessibility permissions
2. Ensure no other apps are using Cmd+Shift+V
3. Try restarting the application

### Issue: No Audio Output
1. Check **System Preferences** → **Sound** → **Output**
2. Ensure speakers are selected and volume is up
3. Check if audio is muted

## 🧪 **Testing on macOS**

### Test Audio Recording
```bash
python test_audio_recording.py
```

### Test Hotkey Detection
```bash
python test_simple_hotkey.py
```

### Test Full System
```bash
python test_system.py
```

### Test Cross-Platform Manager
```bash
python voice_task_manager_universal.py
```

## 🎵 **Audio Device Configuration**

The system automatically detects macOS audio devices:

- **Built-in Speakers**: Automatically selected
- **External Speakers**: Detected and used if available
- **AirPods/Bluetooth**: Works when connected
- **USB Audio**: Automatically detected

## 🔄 **macOS Updates**

### Before Major Updates
1. **Backup** your voice tasks Excel file
2. **Test** the system after update
3. **Reinstall** dependencies if needed

### After Updates
```bash
# Reinstall dependencies if issues occur
pip install --upgrade -r requirements.txt

# Test the system
python test_system.py
```

## 🚀 **Getting Started on macOS**

1. **Install Dependencies**
   ```bash
   python install_universal.py
   ```

2. **Configure API Key**
   ```bash
   python configure_api.py
   ```

3. **Test the System**
   ```bash
   python test_system.py
   ```

4. **Run Voice Task Manager**
   ```bash
   python voice_task_manager_universal.py
   ```

5. **Use the System**
   - Press `Cmd+Shift+V` to activate
   - Speak your task
   - Wait for confirmation

## 🎉 **macOS Advantages**

- **Native Audio**: Better audio device compatibility
- **Reliable Hotkeys**: `pynput` works excellently on macOS
- **System Integration**: Seamless with macOS audio system
- **Performance**: Optimized for Apple hardware

## 🆘 **macOS Support**

If you encounter issues:

1. **Check logs**: `~/.voice_task_manager/logs/`
2. **Verify permissions**: System Preferences → Privacy
3. **Test components**: Use individual test scripts
4. **Reinstall dependencies**: `pip install --upgrade -r requirements.txt`

## 📱 **macOS Integration Tips**

- **Dock Icon**: Pin your terminal app for easy access
- **Spotlight**: Use Spotlight to quickly launch the manager
- **Automator**: Create custom workflows if needed
- **Shortcuts**: Use macOS Shortcuts for additional automation

---

**🎯 The system is designed to work seamlessly on macOS with automatic OS detection and appropriate library selection!**
