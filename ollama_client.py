"""
Ollama client module for Voice-Activated Task Manager
"""

import logging
import requests
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from config import OLLAMA_CONFIG

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, base_url: str = None, model: str = None):
        """
        Initialize Ollama client
        
        Args:
            base_url: Ollama server URL
            model: Model to use for requests
        """
        self.base_url = base_url or OLLAMA_CONFIG['base_url']
        self.model = model or OLLAMA_CONFIG['model']
        self.timeout = OLLAMA_CONFIG['timeout']
        self.temperature = OLLAMA_CONFIG['temperature']
        
        # Test connection on initialization
        self._test_connection()
    
    def _test_connection(self):
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info(f"Connected to Ollama server at {self.base_url}")
                self.connected = True
            else:
                logger.warning(f"Ollama server responded with status {response.status_code}")
                self.connected = False
        except Exception as e:
            logger.error(f"Failed to connect to Ollama server: {e}")
            self.connected = False
    
    def is_connected(self) -> bool:
        """Check if connected to Ollama server"""
        return self.connected
    
    def generate_response(self, prompt: str, system_prompt: str = None, temperature: float = None) -> Dict[str, Any]:
        """
        Generate response from Ollama
        
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
                'error': 'Not connected to Ollama server',
                'response': '',
                'model': self.model
            }
        
        try:
            url = f"{self.base_url}/api/generate"
            
            payload = {
                'model': self.model,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': temperature or self.temperature
                }
            }
            
            if system_prompt:
                payload['system'] = system_prompt
            
            logger.info(f"Generating response with model: {self.model}")
            start_time = time.time()
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                generation_time = time.time() - start_time
                
                response_data = {
                    'success': True,
                    'response': result.get('response', ''),
                    'model': result.get('model', self.model),
                    'total_duration': result.get('total_duration', 0),
                    'load_duration': result.get('load_duration', 0),
                    'prompt_eval_duration': result.get('prompt_eval_duration', 0),
                    'eval_duration': result.get('eval_duration', 0),
                    'generation_time': generation_time
                }
                
                logger.info(f"Response generated in {generation_time:.2f}s")
                return response_data
                
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"API error: {response.status_code}",
                    'response': '',
                    'model': self.model
                }
                
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return {
                'success': False,
                'error': 'Request timed out',
                'response': '',
                'model': self.model
            }
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
        from config import TASK_PARSING_PROMPT
        
        prompt = TASK_PARSING_PROMPT.format(user_input=user_input)
        
        logger.info("Parsing task input with Ollama")
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
        from config import TASK_VALIDATION_PROMPT
        
        prompt = TASK_VALIDATION_PROMPT.format(task_data=json.dumps(task_data, indent=2))
        
        logger.info("Validating task data with Ollama")
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
        from config import PRIORITY_MANAGEMENT_PROMPT
        
        tasks_json = json.dumps(current_tasks, indent=2, default=str)
        prompt = PRIORITY_MANAGEMENT_PROMPT.format(current_tasks=tasks_json)
        
        logger.info("Getting priority management suggestions from Ollama")
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
        from config import QUERY_RESPONSE_PROMPT
        
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
        try:
            url = f"{self.base_url}/api/show"
            payload = {'name': self.model}
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'model_info': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f"Failed to get model info: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_models(self) -> Dict[str, Any]:
        """List available models"""
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'models': response.json().get('models', [])
                }
            else:
                return {
                    'success': False,
                    'error': f"Failed to list models: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup(self):
        """Clean up client resources"""
        # No specific cleanup needed for requests-based client
        logger.info("Ollama client cleaned up")


class MockOllamaClient:
    """Mock Ollama client for testing without actual server"""
    
    def __init__(self):
        self.connected = True
        self.model = "mock-llama3.2"
    
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
    # Test Ollama client
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Test with mock client if Ollama server not available
    try:
        client = OllamaClient()
        if not client.is_connected():
            print("Using mock Ollama client for testing")
            client = MockOllamaClient()
    except:
        print("Using mock Ollama client for testing")
        client = MockOllamaClient()
    
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

