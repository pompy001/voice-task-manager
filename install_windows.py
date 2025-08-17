#!/usr/bin/env python3
"""
Windows-specific installation script for Voice-Activated Task Manager
Handles PyAudio and other Windows-specific dependencies
"""

import subprocess
import sys
import os
import platform

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

def check_windows():
    """Check if running on Windows"""
    if platform.system() != 'Windows':
        print("❌ This script is designed for Windows systems")
        return False
    print("✓ Running on Windows")
    return True

def install_pipwin():
    """Install pipwin for pre-compiled packages"""
    return run_command(
        f"{sys.executable} -m pip install pipwin",
        "Installing pipwin"
    )

def install_pyaudio_windows():
    """Install PyAudio using pipwin (pre-compiled)"""
    return run_command(
        f"{sys.executable} -m pipwin install pyaudio",
        "Installing PyAudio (pre-compiled)"
    )

def install_other_dependencies():
    """Install other dependencies"""
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing other dependencies"
    )

def verify_pyaudio():
    """Verify PyAudio installation"""
    print("\nVerifying PyAudio installation...")
    try:
        import pyaudio
        print("✓ PyAudio installed successfully")
        
        # Test basic functionality
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        print(f"✓ Found {device_count} audio devices")
        p.terminate()
        return True
    except ImportError:
        print("❌ PyAudio not installed")
        return False
    except Exception as e:
        print(f"⚠️  PyAudio installed but may have issues: {e}")
        return False

def main():
    """Main Windows installation function"""
    print("="*60)
    print("Voice Task Manager - Windows Installation")
    print("="*60)
    
    if not check_windows():
        return
    
    print("\nThis script will install dependencies optimized for Windows.")
    print("It will use pre-compiled packages to avoid compilation issues.")
    
    # Install pipwin first
    if not install_pipwin():
        print("\n❌ Failed to install pipwin. Cannot continue.")
        return
    
    # Install PyAudio using pipwin
    if not install_pyaudio_windows():
        print("\n❌ Failed to install PyAudio. Trying alternative method...")
        
        # Alternative: try direct pip install
        print("\nTrying alternative PyAudio installation...")
        if not run_command(
            f"{sys.executable} -m pip install pyaudio",
            "Installing PyAudio (alternative method)"
        ):
            print("\n❌ All PyAudio installation methods failed.")
            print("You may need to install Microsoft Visual C++ Build Tools.")
            print("Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/")
            return
    
    # Install other dependencies
    if not install_other_dependencies():
        print("\n⚠️  Some dependencies failed to install.")
        print("Continuing with verification...")
    
    # Verify PyAudio
    if verify_pyaudio():
        print("\n🎉 PyAudio installation successful!")
        print("\nNext steps:")
        print("1. Set up your OpenAI API key:")
        print("   python configure_api.py")
        print("\n2. Test the system:")
        print("   python test_system.py")
        print("\n3. Run the voice task manager:")
        print("   python voice_task_manager.py")
    else:
        print("\n❌ PyAudio installation failed.")
        print("\nAlternative solutions:")
        print("1. Install Microsoft Visual C++ Build Tools:")
        print("   https://visualstudio.microsoft.com/visual-cpp-build-tools/")
        print("2. Use the regular install script:")
        print("   python install_dependencies.py")

if __name__ == "__main__":
    main()
