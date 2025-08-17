"""
OpenAI client module for Voice-Activated Task Manager
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, continue without it

try:
    import openai
    # Check if it's the new version (1.0.0+)
    if hasattr(openai, 'OpenAI'):
        openai_available = True
    else:
        print("Warning: Old version of openai package detected. Please upgrade with: pip install --upgrade openai")
        openai_available = False
except ImportError:
    print("Warning: openai not installed. Install with: pip install openai")
    openai_available = False

from config import TASK_PARSING_PROMPT, TASK_VALIDATION_PROMPT, PRIORITY_MANAGEMENT_PROMPT, QUERY_RESPONSE_PROMPT

logger = logging.getLogger(__name__)

class OpenAIClient:
    """Client for interacting with OpenAI API"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize OpenAI client
        
        Args:
            api_key: OpenAI API key (will try to get from environment if None)
            model: Model to use for requests
        """
        self.model = model
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        # Configure OpenAI client
        if openai_available:
            self.client = openai.OpenAI(api_key=self.api_key)
            self.connected = True
        else:
            self.client = None
            self.connected = False
        
        logger.info(f"OpenAI client initialized with model: {self.model}")
    
    def is_connected(self) -> bool:
        """Check if connected to OpenAI API"""
        return self.connected and self.client is not None
    
    def generate_response(self, prompt: str, system_prompt: str = None, temperature: float = 0.1) -> Dict[str, Any]:
        """
        Generate response from OpenAI
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Temperature for generation (optional)
            
        Returns:
            Dictionary containing response and metadata
        """
        if not self.connected:
            return {
                'success': False,
                'error': 'Not connected to OpenAI API',
                'response': '',
                'model': self.model
            }
        
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            logger.info(f"Generating response with model: {self.model}")
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=1000
            )
            
            generation_time = time.time() - start_time
            
            response_data = {
                'success': True,
                'response': response.choices[0].message.content,
                'model': response.model,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                },
                'generation_time': generation_time
            }
            
            logger.info(f"Response generated in {generation_time:.2f}s")
            return response_data
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': '',
                'model': self.model
            }
    
    def parse_task(self, user_input: str) -> Dict[str, Any]:
        """
        Parse user input to extract task information
        
        Args:
            user_input: Raw user input text
            
        Returns:
            Parsed task data or error information
        """
        prompt = TASK_PARSING_PROMPT.format(user_input=user_input)
        
        logger.info("Parsing task input with OpenAI")
        result = self.generate_response(prompt)
        
        if not result['success']:
            return result
        
        try:
            # Try to parse JSON response
            response_text = result['response'].strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            parsed_data = json.loads(response_text)
            
            # Check if it's an error response
            if 'error' in parsed_data:
                return {
                    'success': False,
                    'error': parsed_data['error'],
                    'field': parsed_data.get('field', ''),
                    'message': parsed_data.get('message', ''),
                    'parsed_data': parsed_data
                }
            
            # Validate required fields
            required_fields = ['task', 'assigned_by', 'priority', 'expected_date']
            missing_fields = [field for field in required_fields if field not in parsed_data]
            
            if missing_fields:
                return {
                    'success': False,
                    'error': 'missing_fields',
                    'missing_fields': missing_fields,
                    'parsed_data': parsed_data
                }
            
            return {
                'success': True,
                'parsed_data': parsed_data,
                'model': result['model']
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {
                'success': False,
                'error': 'json_parse_error',
                'message': f"Failed to parse response: {e}",
                'raw_response': result['response']
            }
    
    def validate_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate parsed task data
        
        Args:
            task_data: Parsed task data to validate
            
        Returns:
            Validation result
        """
        prompt = TASK_VALIDATION_PROMPT.format(task_data=json.dumps(task_data, indent=2))
        
        logger.info("Validating task data with OpenAI")
        result = self.generate_response(prompt)
        
        if not result['success']:
            return result
        
        try:
            response_text = result['response'].strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            validation_result = json.loads(response_text)
            
            return {
                'success': True,
                'validation_result': validation_result,
                'model': result['model']
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse validation response: {e}")
            return {
                'success': False,
                'error': 'json_parse_error',
                'message': f"Failed to parse validation response: {e}",
                'raw_response': result['response']
            }
    
    def manage_priorities(self, current_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get priority management suggestions
        
        Args:
            current_tasks: List of current tasks
            
        Returns:
            Priority management suggestions
        """
        tasks_json = json.dumps(current_tasks, indent=2, default=str)
        prompt = PRIORITY_MANAGEMENT_PROMPT.format(current_tasks=tasks_json)
        
        logger.info("Getting priority management suggestions from OpenAI")
        result = self.generate_response(prompt)
        
        if not result['success']:
            return result
        
        try:
            response_text = result['response'].strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            suggestions = json.loads(response_text)
            
            return {
                'success': True,
                'suggestions': suggestions,
                'model': result['model']
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse priority suggestions: {e}")
            return {
                'success': False,
                'error': 'json_parse_error',
                'message': f"Failed to parse priority suggestions: {e}",
                'raw_response': result['response']
            }
    
    def answer_query(self, user_query: str, available_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Answer user queries about tasks
        
        Args:
            user_query: User's question
            available_tasks: List of available tasks
            
        Returns:
            Query response
        """
        tasks_json = json.dumps(available_tasks, indent=2, default=str)
        prompt = QUERY_RESPONSE_PROMPT.format(
            user_query=user_query,
            available_tasks=tasks_json
        )
        
        logger.info(f"Answering query: {user_query}")
        result = self.generate_response(prompt)
        
        if not result['success']:
            return result
        
        return {
            'success': True,
            'response': result['response'],
            'model': result['model']
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            'success': True,
            'model': self.model,
            'provider': 'OpenAI',
            'api_key_set': bool(self.api_key)
        }
    
    def cleanup(self):
        """Clean up client resources"""
        # No specific cleanup needed for OpenAI client
        logger.info("OpenAI client cleaned up")


class MockOpenAIClient:
    """Mock OpenAI client for testing without actual API"""
    
    def __init__(self):
        self.connected = True
        self.model = "mock-gpt-3.5-turbo"
    
    def is_connected(self) -> bool:
        return True
    
    def parse_task(self, user_input: str) -> Dict[str, Any]:
        """Mock task parsing"""
        # Simulate parsing the example input
        if "dashboard project" in user_input.lower():
            return {
                'success': True,
                'parsed_data': {
                    'task': 'build a dashboard project',
                    'assigned_by': 'sunny',
                    'priority': 'high',
                    'expected_date': '2024-07-04',
                    'notes': 'Dashboard for project management'
                },
                'model': self.model
            }
        else:
            return {
                'success': False,
                'error': 'missing_field',
                'field': 'task',
                'message': 'Could not identify the task description'
            }
    
    def validate_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock task validation"""
        return {
            'success': True,
            'validation_result': {'valid': True},
            'model': self.model
        }
    
    def answer_query(self, user_query: str, available_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Mock query response"""
        if "next priority" in user_query.lower():
            return {
                'success': True,
                'response': 'Your next priority task is to build the dashboard project, assigned by Sunny, due on July 4th. This is marked as high priority.',
                'model': self.model
            }
        else:
            return {
                'success': True,
                'response': 'I understand your query. How can I help you with your tasks?',
                'model': self.model
            }
    
    def cleanup(self):
        pass


if __name__ == "__main__":
    # Test OpenAI client
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Test with mock client if OpenAI not available
    try:
        if os.getenv('OPENAI_API_KEY'):
            client = OpenAIClient()
            if not client.is_connected():
                print("Using mock OpenAI client for testing")
                client = MockOpenAIClient()
        else:
            print("No OpenAI API key found, using mock client for testing")
            client = MockOpenAIClient()
    except:
        print("Using mock OpenAI client for testing")
        client = MockOpenAIClient()
    
    try:
        # Test task parsing
        test_input = "please add a high priority task build a dashboard project given by sunny expected completed date 4 july"
        result = client.parse_task(test_input)
        print(f"Task parsing result: {result}")
        
        # Test query response
        if result['success']:
            query_result = client.answer_query("what is the next priority task?", [result['parsed_data']])
            print(f"Query response: {query_result}")
        
    finally:
        client.cleanup()
