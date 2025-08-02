"""
Redis Configuration for AgentWeaver Persistent State Management

This module provides Redis connection management and configuration for
persistent state storage using Redis Cloud or local Redis instances.
"""

import os
import redis
from typing import Optional
# TODO: Fix Redis checkpoint import when package is properly installed
# from langgraph.checkpoint.redis import RedisSaver
import logging

logger = logging.getLogger(__name__)


class RedisConfig:
    """Configuration class for Redis connections."""
    
    def __init__(self):
        """Initialize Redis configuration."""
        # Default configuration for Redis Cloud
        # In production, these would come from environment variables
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_password = os.getenv('REDIS_PASSWORD', None)
        self.redis_db = int(os.getenv('REDIS_DB', 0))
        self.redis_ssl = os.getenv('REDIS_SSL', 'false').lower() == 'true'
        
        # Connection pool settings
        self.max_connections = int(os.getenv('REDIS_MAX_CONNECTIONS', 10))
        self.retry_on_timeout = True
        self.socket_timeout = 30.0
        self.socket_connect_timeout = 30.0
        
        logger.info(f"Redis config initialized - Host: {self.redis_host}:{self.redis_port}")
    
    def get_connection_params(self) -> dict:
        """
        Get Redis connection parameters.
        
        Returns:
            Dictionary of Redis connection parameters
        """
        params = {
            'host': self.redis_host,
            'port': self.redis_port,
            'db': self.redis_db,
            'retry_on_timeout': self.retry_on_timeout,
            'socket_timeout': self.socket_timeout,
            'socket_connect_timeout': self.socket_connect_timeout,
            'max_connections': self.max_connections,
            'decode_responses': True  # Important for LangChain compatibility
        }
        
        if self.redis_password:
            params['password'] = self.redis_password
        
        if self.redis_ssl:
            params['ssl'] = True
            params['ssl_cert_reqs'] = None  # For Redis Cloud
        
        return params


class RedisConnectionManager:
    """Manages Redis connections and provides LangChain integration."""
    
    def __init__(self, config: Optional[RedisConfig] = None):
        """
        Initialize Redis connection manager.
        
        Args:
            config: Redis configuration object
        """
        self.config = config or RedisConfig()
        self._client = None
        self._saver = None
        
        logger.info("Redis connection manager initialized")
    
    def get_client(self) -> redis.Redis:
        """
        Get a Redis client instance.
        
        Returns:
            Redis client instance
        """
        if self._client is None:
            try:
                connection_params = self.config.get_connection_params()
                self._client = redis.Redis(**connection_params)
                
                # Test the connection
                self._client.ping()
                logger.info("Redis client connected successfully")
                
            except redis.ConnectionError as e:
                logger.error(f"Failed to connect to Redis: {str(e)}")
                # Fall back to a mock client for development
                logger.warning("Using mock Redis client for development")
                self._client = MockRedisClient()
            except Exception as e:
                logger.error(f"Unexpected error connecting to Redis: {str(e)}")
                self._client = MockRedisClient()
        
        return self._client
    
    def get_saver(self):
        """
        Get a LangChain Saver instance for persistent state management.
        
        Returns:
            Saver instance configured with Redis connection or memory fallback
        """
        if self._saver is None:
            try:
                client = self.get_client()
                
                # Only create RedisSaver if we have a real Redis connection
                if not isinstance(client, MockRedisClient):
                    try:
                        # Try to import and use RedisSaver
                        from langgraph.checkpoint.redis import RedisSaver
                        self._saver = RedisSaver(client)
                        logger.info("RedisSaver initialized successfully")
                    except ImportError:
                        logger.warning("RedisSaver not available, using memory fallback")
                        from langgraph.checkpoint.memory import MemorySaver
                        self._saver = MemorySaver()
                else:
                    # Use memory saver as fallback
                    from langgraph.checkpoint.memory import MemorySaver
                    self._saver = MemorySaver()
                    logger.warning("Using MemorySaver fallback instead of Redis")
                    
            except Exception as e:
                logger.error(f"Failed to initialize RedisSaver: {str(e)}")
                # Fallback to memory saver
                from langgraph.checkpoint.memory import MemorySaver
                self._saver = MemorySaver()
                logger.warning("Using MemorySaver fallback due to Redis initialization failure")
        
        return self._saver
    
    def test_connection(self) -> bool:
        """
        Test the Redis connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            client = self.get_client()
            if isinstance(client, MockRedisClient):
                return False
            
            result = client.ping()
            logger.info("Redis connection test successful")
            return result
            
        except Exception as e:
            logger.error(f"Redis connection test failed: {str(e)}")
            return False
    
    def get_connection_info(self) -> dict:
        """
        Get information about the Redis connection.
        
        Returns:
            Dictionary with connection information
        """
        return {
            'host': self.config.redis_host,
            'port': self.config.redis_port,
            'database': self.config.redis_db,
            'ssl_enabled': self.config.redis_ssl,
            'password_protected': bool(self.config.redis_password),
            'connected': self.test_connection(),
            'client_type': type(self._client).__name__ if self._client else 'None'
        }


class MockRedisClient:
    """Mock Redis client for development when Redis is not available."""
    
    def __init__(self):
        """Initialize mock Redis client."""
        self._data = {}
        logger.info("Mock Redis client initialized")
    
    def ping(self):
        """Mock ping method."""
        return True
    
    def set(self, key, value):
        """Mock set method."""
        self._data[key] = value
        return True
    
    def get(self, key):
        """Mock get method."""
        return self._data.get(key)
    
    def delete(self, *keys):
        """Mock delete method."""
        count = 0
        for key in keys:
            if key in self._data:
                del self._data[key]
                count += 1
        return count
    
    def exists(self, key):
        """Mock exists method."""
        return key in self._data
    
    def keys(self, pattern="*"):
        """Mock keys method."""
        if pattern == "*":
            return list(self._data.keys())
        # Simple pattern matching for basic patterns
        import fnmatch
        return [key for key in self._data.keys() if fnmatch.fnmatch(key, pattern)]


def create_redis_manager() -> RedisConnectionManager:
    """
    Factory function to create a Redis connection manager.
    
    Returns:
        Configured RedisConnectionManager instance
    """
    config = RedisConfig()
    manager = RedisConnectionManager(config)
    
    # Log connection info
    info = manager.get_connection_info()
    logger.info(f"Redis manager created - Connected: {info['connected']}, Type: {info['client_type']}")
    
    return manager


# Global instance for easy access
redis_manager = create_redis_manager()


def get_redis_saver():
    """
    Get the global Redis saver instance.
    
    Returns:
        RedisSaver or MemorySaver instance
    """
    return redis_manager.get_saver()


def get_redis_client():
    """
    Get the global Redis client instance.
    
    Returns:
        Redis client instance
    """
    return redis_manager.get_client()
