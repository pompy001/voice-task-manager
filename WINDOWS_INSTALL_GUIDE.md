# Windows Installation Guide for Voice Task Manager

## 🚨 **PyAudio Installation Issue**

The main problem on Windows is **PyAudio** - it requires Microsoft Visual C++ 14.0 or greater to compile from source.

## 🔧 **Solution 1: Use Pre-compiled PyAudio (Recommended)**

### Step 1: Install pipwin
```bash
pip install pipwin
```

### Step 2: Install PyAudio using pipwin
```bash
python -m pipwin install pyaudio
```

### Step 3: Install other dependencies
```bash
pip install -r requirements.txt
```

## 🔧 **Solution 2: Manual Installation**

### Step 1: Install Microsoft Visual C++ Build Tools
1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install the "C++ build tools" workload
3. Restart your terminal

### Step 2: Install PyAudio
```bash
pip install pyaudio
```

### Step 3: Install other dependencies
```bash
pip install -r requirements.txt
```

## 🔧 **Solution 3: Use Conda (Alternative)**

### Step 1: Install Conda
Download from: https://docs.conda.io/en/latest/miniconda.html

### Step 2: Install PyAudio via Conda
```bash
conda install pyaudio
```

### Step 3: Install other dependencies
```bash
pip install -r requirements.txt
```

## 🔧 **Solution 4: Download Pre-compiled Wheel**

### Step 1: Find your Python version
```bash
python --version
```

### Step 2: Download appropriate wheel
Go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

Download the file matching your Python version and system architecture:
- `PyAudio‑0.2.11‑cp39‑cp39‑win_amd64.whl` (Python 3.9, 64-bit)
- `PyAudio‑0.2.11‑cp310‑cp310‑win_amd64.whl` (Python 3.10, 64-bit)
- `PyAudio‑0.2.11‑cp311‑cp311‑win_amd64.whl` (Python 3.11, 64-bit)

### Step 3: Install the wheel
```bash
pip install PyAudio‑0.2.11‑cp39‑cp39‑win_amd64.whl
```

## ✅ **Verification**

After installation, verify PyAudio works:
```bash
python -c "import pyaudio; p = pyaudio.PyAudio(); print(f'Found {p.get_device_count()} audio devices'); p.terminate()"
```

## 🚀 **Next Steps**

Once PyAudio is installed:
1. Set up your OpenAI API key: `python configure_api.py`
2. Test the system: `python test_system.py`
3. Run the voice task manager: `python voice_task_manager.py`

## 🆘 **Still Having Issues?**

If none of the above solutions work:
1. Check your Python version: `python --version`
2. Check your system architecture: `python -c "import platform; print(platform.architecture())"`
3. Try using a virtual environment
4. Consider using WSL (Windows Subsystem for Linux) for easier Python development
