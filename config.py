"""
Configuration file for Voice-Activated Task Manager
"""

import os
from pathlib import Path

# Hotkey Configuration
HOTKEY_COMBO = {
    'windows': ['ctrl', 'shift', 'v'],
    'macos': ['cmd', 'shift', 'v']
}

# Audio Configuration
AUDIO_CONFIG = {
    'sample_rate': 16000,
    'chunk_size': 1024,
    'channels': 1,
    'format': 'int16',
    'recording_duration': 10,  # seconds
    'silence_threshold': 0.005  # Lower threshold for better silence detection
}

# Speech-to-Text Configuration
STT_CONFIG = {
    'model_size': 'base',  # tiny, base, small, medium, large
    'device': 'cpu',  # cpu or cuda
    'compute_type': 'int8',
    'language': 'en'
}

# Text-to-Speech Configuration
TTS_CONFIG = {
    'model': 'KittenML/kitten-tts-nano-0.1',
    'voice': 'expr-voice-2-f',  # Available: expr-voice-2-m, expr-voice-2-f, expr-voice-3-m, expr-voice-3-f, expr-voice-4-m, expr-voice-4-f, expr-voice-5-m, expr-voice-5-f
    'sample_rate': 24000
}

# Ollama Configuration
OLLAMA_CONFIG = {
    'base_url': 'http://localhost:11434',
    'model': 'llama3.2',
    'timeout': 30,
    'temperature': 0.1
}

# Excel Configuration
EXCEL_CONFIG = {
    'file_path': str(Path.home() / 'Documents' / 'voice_tasks.xlsx'),
    'sheet_name': 'Tasks',
    'columns': [
        'task',
        'assigned_by', 
        'priority',
        'expected_date',
        'status',
        'completed_date',
        'created_date',
        'notes'
    ],
    'priority_levels': ['urgent', 'high', 'medium', 'low'],
    'status_levels': ['ongoing', 'done', 'paused', 'cancelled']
}

# Task Parsing Prompts
TASK_PARSING_PROMPT = """
You are a task management assistant. Parse the following user input and extract task information in JSON format.

Required fields:
- task: The main task description
- assigned_by: Person who assigned the task
- priority: Priority level (urgent/high/medium/low)
- expected_date: Expected completion date (YYYY-MM-DD format)

Optional fields:
- notes: Any additional context or notes

User input: "{user_input}"

Respond with ONLY valid JSON. If any required field is missing or unclear, respond with:
{{"error": "missing_field", "field": "field_name", "message": "description of what's needed"}}

Example valid response:
{{"task": "build dashboard project", "assigned_by": "sunny", "priority": "high", "expected_date": "2024-07-04", "notes": "Dashboard for project management"}}
"""

# Task Validation Prompt
TASK_VALIDATION_PROMPT = """
You are a task validation assistant. Validate the following task data and ensure all required fields are present and properly formatted.

Task data: {task_data}

Validation rules:
1. task: Must be a clear, actionable description
2. assigned_by: Must be a valid name or identifier
3. priority: Must be one of: urgent, high, medium, low
4. expected_date: Must be in YYYY-MM-DD format and a valid future date

If validation passes, respond with: {{"valid": true}}
If validation fails, respond with: {{"valid": false, "errors": ["error1", "error2"]}}
"""

# Priority Management Prompt
PRIORITY_MANAGEMENT_PROMPT = """
You are a priority management assistant. Analyze the current task list and suggest priority adjustments based on:

1. Task deadlines
2. Current workload
3. Task dependencies
4. Business impact

Current tasks: {current_tasks}

Suggest priority adjustments in JSON format:
{{"adjustments": [{{"task_id": "id", "new_priority": "priority", "reason": "explanation"}}]}}
"""

# Query Response Prompt
QUERY_RESPONSE_PROMPT = """
You are a task management assistant. Answer the user's query about their tasks in a natural, helpful way.

User query: "{user_query}"

Available tasks: {available_tasks}

Provide a clear, concise response that directly answers the user's question. Include relevant task details, priorities, and deadlines when appropriate.

Response should be conversational and informative, suitable for text-to-speech output.
"""

# File Paths
TEMP_DIR = Path.home() / '.voice_task_manager' / 'temp'
LOG_FILE = Path.home() / '.voice_task_manager' / 'logs' / 'voice_task_manager.log'

# Create necessary directories
TEMP_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

