# Voice-Activated Task Manager

A **cross-platform** voice-activated task management system that works on **Windows, macOS, and Linux**. Allows instant task creation through speech input, with automatic parsing and Excel integration.

## Features

- **Global Hotkey Activation**: Press designated hotkey anywhere on your system
- **Natural Speech Input**: Speak task details naturally including priority
- **Intelligent Parsing**: OpenAI GPT automatically extracts and validates task data
- **Excel Integration**: Tasks automatically added to Excel with proper formatting
- **Voice Feedback**: Text-to-speech confirmation and responses
- **Smart Priority Management**: Automatic priority redistribution and management
- **Voice Queries**: Ask "what's the next priority task?" and get voice responses

## 🚀 **Installation**

### Prerequisites
- Python 3.8 or higher
- OpenAI API key
- Cross-platform support: Windows, macOS, Linux

### Quick Start
1. **Install Dependencies**:
   ```bash
   # Universal installer (recommended)
   python install_universal.py
   
   # Platform-specific installers
   python install_windows.py      # Windows only
   pip install -r requirements.txt # Manual installation
   ```

2. **Set up OpenAI API Key**:
   ```bash
   python configure_api.py
   ```

3. **Test the System**:
   ```bash
   python test_system.py
   ```

4. **Run the Voice Task Manager**:
   ```bash
   # Universal (auto-detects OS)
   python voice_task_manager_universal.py
   
   # Platform-specific
   python voice_task_manager_keyboard.py  # Windows
   python voice_task_manager.py           # macOS/Linux
   ```

## 🎯 **Usage**

1. **Start the Service**:
   ```bash
   # Universal (auto-detects OS)
   python voice_task_manager_universal.py
   ```

2. **Activate Voice Input**:
   - Press `Ctrl+Shift+V` (Windows) or `Cmd+Shift+V` (macOS/Linux)
   - Speak your task naturally: "please add a high priority task build a dashboard project given by sunny expected completed date 4 july"

3. **Voice Queries**:
   - Ask "what is the next priority task?"
   - Get voice responses about task status and priorities

## 🌍 **Cross-Platform Support**

| Platform | Hotkey | Library | Status |
|----------|--------|---------|---------|
| **Windows** | `Ctrl+Shift+V` | `keyboard` | ✅ Full Support |
| **macOS** | `Cmd+Shift+V` | `pynput` | ✅ Full Support |
| **Linux** | `Ctrl+Shift+V` | `pynput` | ✅ Full Support |

## Configuration

- **Hotkey**: Modify `HOTKEY_COMBO` in `voice_task_manager.py`
- **Excel File**: Set `EXCEL_FILE_PATH` to your preferred location
- **OpenAI Model**: Change `model` parameter in `OpenAIClient()` to use different models

## 🏗️ **Architecture**

```
Cross-Platform Voice Task Manager:
├── OS Detection & Hotkey Setup
│   ├── Windows: keyboard library (Ctrl+Shift+V)
│   ├── macOS: pynput library (Cmd+Shift+V)
│   └── Linux: pynput library (Ctrl+Shift+V)
├── Audio recording module (pyaudio)
├── Speech-to-text (Faster-Whisper)
├── Text-to-speech (KittenTTS)
├── LLM parser & validator (OpenAI GPT API)
├── Excel file handler (openpyxl)
├── Priority management system
└── Query response system
```

## Excel Schema

| Column | Description | Example |
|--------|-------------|---------|
| task | Task description | "build a dashboard project" |
| assigned_by | Person who assigned task | "sunny" |
| priority | Task priority level | "high/medium/low/urgent" |
| expected_date | Expected completion date | "2024-07-04" |
| status | Current task status | "ongoing/done/paused" |
| completed_date | Actual completion date | "2024-07-05" |

## Development

- **Phase 1**: Core functionality (hotkey, STT, TTS, Ollama, Excel)
- **Phase 2**: Intelligence layer (priority management, voice queries)
- **Phase 3**: UX enhancements (conversational flow, analytics)

## 📋 **Requirements**

- **Python**: 3.8 or higher
- **OpenAI API key**: For AI-powered task parsing
- **Microphone access**: For voice input
- **Audio output**: Speakers or headphones for voice feedback
- **Excel-compatible**: Spreadsheet application for task storage
- **Cross-platform**: Windows 10/11, macOS 10.14+, Linux

## 📚 **Installation Guides**

- **[Universal Installation](install_universal.py)**: Cross-platform installer
- **[Windows Installation](WINDOWS_INSTALL_GUIDE.md)**: Windows-specific guide
- **[macOS Installation](MACOS_INSTALL_GUIDE.md)**: macOS-specific guide

