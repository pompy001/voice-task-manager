#!/usr/bin/env python3
"""
Universal Installation Script for Voice-Activated Task Manager
Works on Windows, macOS, and Linux
"""

import subprocess
import sys
import os
import platform
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
    """Check Python version compatibility"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected")
        print("This system requires Python 3.8 or higher")
        print("Please upgrade Python and try again")
        return False
    
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def upgrade_pip():
    """Upgrade pip to latest version"""
    return run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Upgrading pip"
    )

def install_cross_platform_dependencies():
    """Install cross-platform dependencies"""
    print("\nInstalling cross-platform dependencies...")
    
    # Install pynput for macOS and Linux hotkeys
    if platform.system().lower() != "windows":
        if not run_command(
            f"{sys.executable} -m pip install pynput>=1.7.6",
            "Installing pynput (macOS/Linux hotkey support)"
        ):
            print("⚠️  pynput installation failed - hotkey functionality may not work")
    
    # Install keyboard for Windows hotkeys
    if platform.system().lower() == "windows":
        if not run_command(
            f"{sys.executable} -m pip install keyboard>=0.13.5",
            "Installing keyboard (Windows hotkey support)"
        ):
            print("⚠️  keyboard installation failed - hotkey functionality may not work")
    
    # Install other dependencies
    dependencies = [
        "faster-whisper==0.10.0",
        "kittentts==0.1.0",
        "soundfile==0.12.1",
        "openpyxl==3.1.2",
        "requests==2.31.0",
        "python-dateutil==2.8.2",
        "openai>=1.0.0",
        "python-dotenv==1.0.0",
        "numpy>=1.21.0"
    ]
    
    for dep in dependencies:
        if not run_command(
            f"{sys.executable} -m pip install {dep}",
            f"Installing {dep}"
        ):
            print(f"⚠️  Failed to install {dep}")
    
    return True

def install_pyaudio_cross_platform():
    """Install PyAudio based on platform"""
    system = platform.system().lower()
    
    if system == "windows":
        print("\nInstalling PyAudio for Windows...")
        
        # Try pipwin first (pre-compiled)
        if run_command(
            f"{sys.executable} -m pip install pipwin",
            "Installing pipwin"
        ):
            if run_command(
                f"{sys.executable} -m pipwin install pyaudio",
                "Installing PyAudio via pipwin (pre-compiled)"
            ):
                return True
        
        # Fallback to direct pip install
        print("\nTrying direct PyAudio installation...")
        if run_command(
            f"{sys.executable} -m pip install pyaudio",
            "Installing PyAudio directly"
        ):
            return True
        
        print("❌ PyAudio installation failed on Windows")
        print("You may need to install Microsoft Visual C++ Build Tools")
        print("Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/")
        return False
        
    elif system == "darwin":  # macOS
        print("\nInstalling PyAudio for macOS...")
        
        # On macOS, PyAudio usually installs without issues
        if run_command(
            f"{sys.executable} -m pip install pyaudio",
            "Installing PyAudio for macOS"
        ):
            return True
        
        print("❌ PyAudio installation failed on macOS")
        print("Try: brew install portaudio && pip install pyaudio")
        return False
        
    else:  # Linux
        print("\nInstalling PyAudio for Linux...")
        
        # On Linux, PyAudio usually installs without issues
        if run_command(
            f"{sys.executable} -m pip install pyaudio",
            "Installing PyAudio for Linux"
        ):
            return True
        
        print("❌ PyAudio installation failed on Linux")
        print("Try: sudo apt-get install portaudio19-dev && pip install pyaudio")
        return False

def verify_installation():
    """Verify key components are working"""
    print("\nVerifying installation...")
    
    try:
        # Test PyAudio
        import pyaudio
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        p.terminate()
        print(f"✓ PyAudio - OK (Found {device_count} audio devices)")
        
        # Test hotkey libraries
        system = platform.system().lower()
        if system == "darwin" or system == "linux":
            try:
                import pynput
                print("✓ pynput - OK (macOS/Linux hotkey support)")
            except ImportError:
                print("❌ pynput - FAILED")
        elif system == "windows":
            try:
                import keyboard
                print("✓ keyboard - OK (Windows hotkey support)")
            except ImportError:
                print("❌ keyboard - FAILED")
        
        # Test other key components
        import openai
        print("✓ OpenAI - OK")
        
        import openpyxl
        print("✓ openpyxl - OK")
        
        print("\n🎉 Installation verification completed!")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    """Main installation function"""
    print("="*70)
    print("Voice Task Manager - Universal Installation")
    print("="*70)
    
    system = platform.system()
    print(f"Detected operating system: {system}")
    
    # Check Python version
    if not check_python_version():
        return
    
    # Upgrade pip
    if not upgrade_pip():
        print("⚠️  pip upgrade failed, continuing with installation...")
    
    # Install cross-platform dependencies
    if not install_cross_platform_dependencies():
        print("⚠️  Some dependencies failed to install")
    
    # Install PyAudio
    if not install_pyaudio_cross_platform():
        print("⚠️  PyAudio installation failed - audio functionality may not work")
    
    # Verify installation
    if verify_installation():
        print("\n🚀 Installation completed successfully!")
        print("\nNext steps:")
        print("1. Set up your OpenAI API key: python configure_api.py")
        print("2. Test the system: python test_system.py")
        print("3. Run the universal voice task manager: python voice_task_manager_universal.py")
    else:
        print("\n⚠️  Installation completed with warnings")
        print("Some components may not work properly")
        print("Check the error messages above for troubleshooting")

if __name__ == "__main__":
    main()
