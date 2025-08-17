#!/usr/bin/env python3
"""
Setup script for Voice-Activated Task Manager
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"✗ Python 3.8+ is required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\nInstalling Python dependencies...")
    
    # Install base requirements
    if not run_command("pip install -r requirements.txt", "Installing base requirements"):
        return False
    
    # Install KittenTTS separately (it's not on PyPI)
    if not run_command(
        "pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl",
        "Installing KittenTTS"
    ):
        print("Warning: KittenTTS installation failed. The system will use mock TTS instead.")
    
    return True

def check_openai_api_key():
    """Check if OpenAI API key is set"""
    print("\nChecking OpenAI API key...")
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OpenAI API key not found!")
        print("To set your API key:")
        print("1. Get an API key from: https://platform.openai.com/")
        print("2. Set the environment variable:")
        if os.name == 'nt':  # Windows
            print("   set OPENAI_API_KEY=your-api-key-here")
        else:  # Unix/Linux/macOS
            print("   export OPENAI_API_KEY='your-api-key-here'")
        print("\nThe system will use mock components until the API key is set.")
        return False
    else:
        print("✓ OpenAI API key is set")
        return True

def create_directories():
    """Create necessary directories"""
    print("\nCreating necessary directories...")
    try:
        # Create temp and log directories
        temp_dir = Path.home() / '.voice_task_manager' / 'temp'
        log_dir = Path.home() / '.voice_task_manager' / 'logs'
        
        temp_dir.mkdir(parents=True, exist_ok=True)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        print("✓ Directories created successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to create directories: {e}")
        return False

def test_installation():
    """Test if the installation works"""
    print("\nTesting installation...")
    try:
        # Try to import main components
        import config
        import audio_recorder
        import speech_to_text
        import text_to_speech
        import openai_client
        import excel_manager
        
        print("✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("="*60)
    print("Voice-Activated Task Manager Setup")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Python version incompatible")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed: Dependency installation failed")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("\n❌ Setup failed: Directory creation failed")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("\n❌ Setup failed: Installation test failed")
        sys.exit(1)
    
    # Check OpenAI API key
    check_openai_api_key()
    
    print("\n" + "="*60)
    print("🎉 Setup completed successfully!")
    print("="*60)
    
    print("\nNext steps:")
    print("1. Set your OpenAI API key (if not already done)")
    print("2. Test the system: python test_system.py")
    print("3. Start the voice task manager: python voice_task_manager.py")
    print("4. Use Ctrl+Shift+V (Windows) or Cmd+Shift+V (macOS) to activate voice input")
    
    print("\nFor help and documentation, see README.md")
    print("\nHappy voice task managing! 🎤📝")

if __name__ == "__main__":
    main()
