#!/usr/bin/env python3
"""
Configuration script for Voice-Activated Task Manager
Helps set up OpenAI API key and other configuration
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create a .env file with the API key"""
    env_file = Path('.env')
    
    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("Keeping existing .env file")
            return False
    
    # Get API key from user
    print("\nEnter your OpenAI API key:")
    print("(The key will be stored in a .env file)")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return False
    
    # Create .env file
    try:
        with open(env_file, 'w') as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
            f.write("# Voice Task Manager Configuration\n")
            f.write("# Add any other configuration variables here\n")
        
        print(f"✅ .env file created successfully at {env_file.absolute()}")
        print("⚠️  Remember to add .env to your .gitignore file to keep your API key secure!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def set_environment_variable():
    """Set environment variable directly"""
    print("\nSetting environment variable directly...")
    
    # Get API key from user
    api_key = input("Enter your OpenAI API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return False
    
    # Set environment variable
    os.environ['OPENAI_API_KEY'] = api_key
    
    print("✅ Environment variable set for current session")
    print("⚠️  Note: This will only work for the current terminal session")
    print("   For permanent setup, use the .env file option or set it in your shell profile")
    
    return True

def test_api_key():
    """Test if the API key is working"""
    print("\nTesting API key...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No API key found in environment")
        return False
    
    try:
        import openai
        openai.api_key = api_key
        
        # Test with a simple request
        client = openai.OpenAI(api_key=api_key)
        response = client.models.list()
        
        print("✅ API key is valid and working!")
        print(f"   Available models: {len(response.data)} models")
        return True
        
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        return False

def main():
    """Main configuration function"""
    print("="*60)
    print("Voice Task Manager Configuration")
    print("="*60)
    
    print("\nThis script will help you configure your OpenAI API key.")
    print("Choose an option:")
    print("1. Create .env file (recommended)")
    print("2. Set environment variable directly")
    print("3. Test existing API key")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            if create_env_file():
                print("\n🎉 Configuration completed successfully!")
                print("You can now run the voice task manager.")
            break
            
        elif choice == '2':
            if set_environment_variable():
                print("\n🎉 Environment variable set!")
                print("You can now run the voice task manager in this terminal.")
            break
            
        elif choice == '3':
            test_api_key()
            break
            
        elif choice == '4':
            print("Exiting...")
            break
            
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
