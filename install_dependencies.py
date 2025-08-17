#!/usr/bin/env python3
"""
Installation script for Voice-Activated Task Manager
Installs all required dependencies
"""

import subprocess
import sys
import os

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
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8+")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def upgrade_pip():
    """Upgrade pip to latest version"""
    return run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Upgrading pip"
    )

def install_requirements():
    """Install requirements from requirements.txt"""
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing requirements"
    )

def verify_installations():
    """Verify that key packages are installed correctly"""
    print("\nVerifying installations...")
    
    packages_to_check = [
        ('openai', 'OpenAI API client'),
        ('pynput', 'Global hotkey detection'),
        ('faster_whisper', 'Speech-to-text'),
        ('kittentts', 'Text-to-speech'),
        ('openpyxl', 'Excel integration'),
        ('pyaudio', 'Audio recording'),
        ('soundfile', 'Audio file handling'),
        ('requests', 'HTTP requests'),
        ('python_dateutil', 'Date utilities'),
        ('dotenv', 'Environment variables')
    ]
    
    all_good = True
    
    for package, description in packages_to_check:
        try:
            if package == 'openai':
                import openai
                if hasattr(openai, 'OpenAI'):
                    print(f"✓ {description} (openai)")
                else:
                    print(f"⚠️  {description} (openai) - old version detected")
                    all_good = False
            elif package == 'python_dateutil':
                import dateutil
                print(f"✓ {description} (python-dateutil)")
            elif package == 'dotenv':
                import dotenv
                print(f"✓ {description} (python-dotenv)")
            else:
                __import__(package)
                print(f"✓ {description} ({package})")
        except ImportError:
            print(f"❌ {description} ({package}) - not installed")
            all_good = False
    
    return all_good

def main():
    """Main installation function"""
    print("="*60)
    print("Voice Task Manager - Dependency Installation")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Installation cannot continue. Please upgrade Python.")
        return
    
    # Upgrade pip
    upgrade_pip()
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Some dependencies failed to install.")
        print("Please check the error messages above and try again.")
        return
    
    # Verify installations
    if verify_installations():
        print("\n🎉 All dependencies installed successfully!")
        print("\nNext steps:")
        print("1. Set up your OpenAI API key:")
        print("   python configure_api.py")
        print("\n2. Test the system:")
        print("   python test_system.py")
        print("\n3. Run the voice task manager:")
        print("   python voice_task_manager.py")
    else:
        print("\n⚠️  Some packages may not be installed correctly.")
        print("Please check the warnings above and try reinstalling.")

if __name__ == "__main__":
    main()
