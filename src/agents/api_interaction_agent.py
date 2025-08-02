"""
API Interaction Worker Agent for AgentWeaver.

This module implements a worker agent specialized in making HTTP requests
and interacting with external APIs.
"""

from typing import Dict, Any, Optional, List
import logging
import json
from datetime import datetime
import requests
from urllib.parse import urljoin, urlparse

from .base_agent import BaseWorkerAgent
from ..models import AgentCapability, Task, TaskStatus


logger = logging.getLogger(__name__)


class APIInteractionAgent(BaseWorkerAgent):
    """
    Worker agent specialized in API interactions and HTTP requests.
    
    This agent can fetch data from external APIs, handle authentication,
    and process responses in various formats.
    """
    
    def __init__(self, name: str = "APIFetcher"):
        """
        Initialize the API Interaction Agent.
        
        Args:
            name: Name for this agent instance
        """
        capabilities = [AgentCapability.COMMUNICATION, AgentCapability.DATA_PROCESSING]
        super().__init__(name, capabilities, "api_client")
        
        # Agent-specific configuration
        self.timeout = 30  # Default timeout in seconds
        self.max_retries = 3
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': f'AgentWeaver-APIAgent/{self.agent_id}',
            'Accept': 'application/json, text/plain, */*'
        })
        
        self.logger.info(f"API Interaction Agent '{name}' initialized")
    
    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an API interaction task.
        
        Args:
            task: The task to execute
            context: Additional context data from the graph state
            
        Returns:
            Dictionary containing the API response and metadata
            
        Raises:
            ValueError: If required parameters are missing
            Exception: If API request fails
        """
        start_time = datetime.utcnow()
        
        try:
            # Extract parameters from task
            url = task.parameters.get('url', '')
            method = task.parameters.get('method', 'GET').upper()
            headers = task.parameters.get('headers', {})
            data = task.parameters.get('data')
            params = task.parameters.get('params', {})
            auth = task.parameters.get('auth')
            
            # Get URL from context if not in task parameters
            if not url:
                url = context.get('url', '')
            
            if not url:
                raise ValueError("No URL provided for API request")
            
            # Validate URL
            if not self._is_valid_url(url):
                raise ValueError(f"Invalid URL format: {url}")
            
            self.logger.info(f"Making {method} request to {url}")
            
            # Prepare request parameters
            request_kwargs = {
                'timeout': task.parameters.get('timeout', self.timeout),
                'headers': headers,
                'params': params
            }
            
            # Add authentication if provided
            if auth:
                if auth.get('type') == 'bearer':
                    request_kwargs['headers']['Authorization'] = f"Bearer {auth.get('token')}"
                elif auth.get('type') == 'basic':
                    request_kwargs['auth'] = (auth.get('username'), auth.get('password'))
                elif auth.get('type') == 'api_key':
                    key_name = auth.get('key_name', 'X-API-Key')
                    request_kwargs['headers'][key_name] = auth.get('api_key')
            
            # Add data for POST/PUT/PATCH requests
            if method in ['POST', 'PUT', 'PATCH'] and data is not None:
                if isinstance(data, dict):
                    request_kwargs['json'] = data
                else:
                    request_kwargs['data'] = data
            
            # Make the request with retry logic
            response = self._make_request_with_retry(method, url, **request_kwargs)
            
            # Process the response
            result = self._process_response(response)
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Prepare the final result
            final_result = {
                'url': url,
                'method': method,
                'status_code': response.status_code,
                'success': response.status_code < 400,
                'response': result,
                'execution_time': execution_time,
                'agent_id': self.agent_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"API request completed in {execution_time:.2f}s with status {response.status_code}")
            return final_result
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"API request failed: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                'error': error_msg,
                'execution_time': execution_time,
                'agent_id': self.agent_id,
                'timestamp': datetime.utcnow().isoformat(),
                'success': False
            }
    
    def _make_request_with_retry(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method
            url: Target URL
            **kwargs: Request parameters
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: If all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(method, url, **kwargs)
                
                # Don't retry on client errors (4xx), only on server errors (5xx) and network issues
                if response.status_code < 500:
                    return response
                
                if attempt < self.max_retries - 1:
                    self.logger.warning(f"Server error {response.status_code}, retrying... (attempt {attempt + 1}/{self.max_retries})")
                    continue
                
                return response
                
            except requests.RequestException as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    self.logger.warning(f"Request failed, retrying... (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                    continue
        
        # If we get here, all retries failed
        raise last_exception or requests.RequestException("All retry attempts failed")
    
    def _process_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Process the HTTP response and extract data.
        
        Args:
            response: Response object
            
        Returns:
            Processed response data
        """
        result = {
            'headers': dict(response.headers),
            'encoding': response.encoding,
            'url': response.url
        }
        
        try:
            # Try to parse as JSON first
            if response.headers.get('content-type', '').startswith('application/json'):
                result['data'] = response.json()
                result['format'] = 'json'
            else:
                # Fall back to text
                result['data'] = response.text
                result['format'] = 'text'
                
                # Try to parse as JSON anyway if it looks like JSON
                if response.text.strip().startswith(('{', '[')):
                    try:
                        result['data'] = response.json()
                        result['format'] = 'json'
                    except json.JSONDecodeError:
                        pass  # Keep as text
        
        except Exception as e:
            self.logger.warning(f"Failed to process response content: {str(e)}")
            result['data'] = response.text
            result['format'] = 'text'
            result['parse_error'] = str(e)
        
        return result
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def can_handle_task(self, task: Task) -> bool:
        """
        Check if this agent can handle the given task.
        
        Args:
            task: The task to check
            
        Returns:
            True if the agent can handle API interaction tasks
        """
        # Check if it's an API task
        if task.task_type in ['api_request', 'fetch_data', 'http_request']:
            return True
        
        # Check if the task has URL parameter
        if 'url' in task.parameters:
            return True
        
        # Fall back to base capability checking
        return super().can_handle_task(task)
    
    def health_check(self) -> bool:
        """
        Perform a health check specific to API interaction capabilities.
        
        Returns:
            True if the agent is healthy and can make API requests
        """
        try:
            # Basic health check from parent
            if not super().health_check():
                return False
            
            # Test basic HTTP capability with a simple request
            # Using httpbin.org as a reliable test endpoint
            test_url = "https://httpbin.org/status/200"
            
            try:
                response = self.session.get(test_url, timeout=5)
                if response.status_code != 200:
                    self.set_error(f"HTTP capability test failed with status {response.status_code}")
                    return False
            except requests.RequestException as e:
                self.logger.warning(f"HTTP health check failed (network may be unavailable): {str(e)}")
                # Don't mark as error for network issues during health check
                # The agent might still work when network is available
                pass
            
            self.logger.debug(f"API Interaction Agent {self.name} health check passed")
            return True
            
        except Exception as e:
            self.set_error(f"Health check failed: {str(e)}")
            return False
    
    def set_custom_headers(self, headers: Dict[str, str]) -> None:
        """
        Set custom headers for all requests.
        
        Args:
            headers: Dictionary of headers to add
        """
        self.session.headers.update(headers)
        self.logger.info(f"Updated session headers: {list(headers.keys())}")
    
    def set_timeout(self, timeout: int) -> None:
        """
        Set default timeout for requests.
        
        Args:
            timeout: Timeout in seconds
        """
        self.timeout = timeout
        self.logger.info(f"Updated default timeout to {timeout}s")
    
    def clear_session(self) -> None:
        """Clear the session and create a new one."""
        self.session.close()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'AgentWeaver-APIAgent/{self.agent_id}',
            'Accept': 'application/json, text/plain, */*'
        })
        self.logger.info("Session cleared and reset")
    
    def __del__(self):
        """Cleanup when agent is destroyed."""
        try:
            self.session.close()
        except Exception:
            pass
