"""
Concurrent Worker Agent Adapter for AgentWeaver Swarm Orchestration
===================================================================

This module provides adapters and utilities to make existing worker agents
compatible with concurrent, stateless execution in the swarm orchestration system.
"""

from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime
import logging
import threading
import copy
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid

from .base_agent import BaseWorkerAgent
from .text_analysis_agent import TextAnalysisAgent
from .data_processing_agent import DataProcessingAgent
from .api_interaction_agent import APIInteractionAgent
from ..models import AgentCapability, Task, TaskStatus, AgentStatus


logger = logging.getLogger(__name__)


class ConcurrentWorkerAdapter:
    """
    Adapter to make existing worker agents compatible with concurrent execution.
    
    This class wraps existing worker agents to ensure they can be executed
    concurrently in a thread-safe manner for swarm orchestration.
    """
    
    def __init__(self, worker_agent_class: type, agent_config: Dict[str, Any] = None):
        """
        Initialize the concurrent worker adapter.
        
        Args:
            worker_agent_class: The worker agent class to adapt
            agent_config: Configuration parameters for the agent
        """
        self.worker_agent_class = worker_agent_class
        self.agent_config = agent_config or {}
        self.thread_local = threading.local()
        self.execution_lock = threading.Lock()
        
        # Create a prototype agent to get capabilities and other metadata
        self.prototype_agent = worker_agent_class(**self.agent_config)
        
        logger.info(f"Concurrent adapter initialized for {worker_agent_class.__name__}")
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Get the capabilities of the adapted agent."""
        return self.prototype_agent.capabilities
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the adapted agent."""
        return {
            "agent_class": self.worker_agent_class.__name__,
            "capabilities": [cap.value for cap in self.prototype_agent.capabilities],
            "agent_type": self.prototype_agent.agent_state.agent_type,
            "config": self.agent_config
        }
    
    def execute_subtask(self, subtask_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a sub-task using the adapted worker agent in a thread-safe manner.
        
        Args:
            subtask_data: Data for the sub-task to execute
            context: Additional context data
            
        Returns:
            Execution result dictionary
        """
        try:
            # Create a thread-local agent instance to avoid state conflicts
            agent_instance = self._get_thread_local_agent()
            
            # Convert subtask data to Task object
            task = self._create_task_from_subtask(subtask_data)
            
            # Prepare context
            execution_context = context or {}
            execution_context.update(subtask_data.get("context", {}))
            
            # Mark agent as busy for this execution
            with self.execution_lock:
                agent_instance.start_task(task)
            
            start_time = datetime.utcnow()
            
            try:
                # Execute the task
                result = agent_instance.execute(task, execution_context)
                
                # Calculate execution time
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                # Mark task as completed
                with self.execution_lock:
                    agent_instance.complete_task(task, execution_time, success=True)
                
                # Format result for concurrent execution
                return self._format_concurrent_result(
                    result=result,
                    subtask_data=subtask_data,
                    agent_instance=agent_instance,
                    execution_time=execution_time,
                    success=True
                )
                
            except Exception as task_error:
                # Calculate execution time even for failures
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                # Mark task as failed
                with self.execution_lock:
                    agent_instance.complete_task(task, execution_time, success=False)
                    agent_instance.set_error(f"Task execution failed: {str(task_error)}")
                
                logger.error(f"Task execution failed for {task.task_id}: {str(task_error)}")
                
                # Return error result
                return self._format_concurrent_result(
                    result={"error": str(task_error)},
                    subtask_data=subtask_data,
                    agent_instance=agent_instance,
                    execution_time=execution_time,
                    success=False
                )
        
        except Exception as e:
            logger.error(f"Concurrent worker adapter failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "subtask_id": subtask_data.get("task_id", "unknown"),
                "status": "failed",
                "error": f"Adapter error: {str(e)}",
                "agent_class": self.worker_agent_class.__name__,
                "execution_time": 0.0,
                "completed_at": datetime.utcnow().isoformat()
            }
    
    def _get_thread_local_agent(self) -> BaseWorkerAgent:
        """Get or create a thread-local agent instance."""
        if not hasattr(self.thread_local, 'agent'):
            # Create a new agent instance for this thread
            agent_config = self.agent_config.copy()
            # Add thread identifier to agent name to avoid conflicts
            thread_id = threading.get_ident()
            original_name = agent_config.get('name', self.worker_agent_class.__name__)
            agent_config['name'] = f"{original_name}_thread_{thread_id}"
            
            self.thread_local.agent = self.worker_agent_class(**agent_config)
            logger.debug(f"Created thread-local agent: {self.thread_local.agent.name}")
        
        return self.thread_local.agent
    
    def _create_task_from_subtask(self, subtask_data: Dict[str, Any]) -> Task:
        """Convert subtask data to a Task object."""
        return Task(
            task_id=subtask_data.get("task_id", str(uuid.uuid4())),
            title=subtask_data.get("title", f"Subtask {subtask_data.get('task_id', 'unknown')}"),
            description=subtask_data.get("description", "Concurrent subtask execution"),
            parameters=subtask_data.get("parameters", {}),
            required_capabilities=subtask_data.get("required_capabilities", []),
            priority=subtask_data.get("priority", "medium"),
            status=TaskStatus.IN_PROGRESS
        )
    
    def _format_concurrent_result(self, result: Dict[str, Any], subtask_data: Dict[str, Any], 
                                 agent_instance: BaseWorkerAgent, execution_time: float, 
                                 success: bool) -> Dict[str, Any]:
        """Format the result for concurrent execution context."""
        return {
            "subtask_id": subtask_data.get("task_id", "unknown"),
            "status": "completed" if success else "failed",
            "result": result,
            "agent_id": agent_instance.agent_id,
            "agent_name": agent_instance.name,
            "agent_class": self.worker_agent_class.__name__,
            "execution_time": execution_time,
            "completed_at": datetime.utcnow().isoformat(),
            "thread_id": threading.get_ident(),
            "capabilities_used": [cap.value for cap in agent_instance.capabilities]
        }


class ConcurrentWorkerRegistry:
    """
    Registry for managing concurrent worker adapters.
    
    This class maintains a collection of worker adapters and provides
    methods to find suitable workers for specific tasks.
    """
    
    def __init__(self):
        """Initialize the concurrent worker registry."""
        self.adapters: Dict[str, ConcurrentWorkerAdapter] = {}
        self.capability_map: Dict[str, List[str]] = {}
        
        # Register default worker adapters
        self._register_default_adapters()
    
    def _register_default_adapters(self):
        """Register the default worker agent adapters."""
        # Text Analysis Agent
        self.register_adapter(
            "text_analyzer",
            TextAnalysisAgent,
            {"name": "ConcurrentTextAnalyzer"}
        )
        
        # Data Processing Agent
        self.register_adapter(
            "data_processor", 
            DataProcessingAgent,
            {"name": "ConcurrentDataProcessor"}
        )
        
        # API Interaction Agent
        self.register_adapter(
            "api_agent",
            APIInteractionAgent,
            {"name": "ConcurrentAPIAgent"}
        )
        
        logger.info("Default concurrent worker adapters registered")
    
    def register_adapter(self, adapter_id: str, worker_class: type, config: Dict[str, Any] = None):
        """
        Register a new concurrent worker adapter.
        
        Args:
            adapter_id: Unique identifier for the adapter
            worker_class: Worker agent class to adapt
            config: Configuration for the worker
        """
        try:
            adapter = ConcurrentWorkerAdapter(worker_class, config)
            self.adapters[adapter_id] = adapter
            
            # Update capability mapping
            capabilities = [cap.value for cap in adapter.get_capabilities()]
            for capability in capabilities:
                if capability not in self.capability_map:
                    self.capability_map[capability] = []
                self.capability_map[capability].append(adapter_id)
            
            logger.info(f"Registered concurrent adapter '{adapter_id}' for {worker_class.__name__}")
            
        except Exception as e:
            logger.error(f"Failed to register adapter '{adapter_id}': {str(e)}")
            raise
    
    def find_suitable_adapter(self, required_capabilities: List[str]) -> Optional[ConcurrentWorkerAdapter]:
        """
        Find a suitable adapter for the given capabilities.
        
        Args:
            required_capabilities: List of required capability strings
            
        Returns:
            Suitable adapter or None if no match found
        """
        if not required_capabilities:
            # Return first available adapter if no specific requirements
            return next(iter(self.adapters.values()), None)
        
        # Find adapters that have at least one matching capability
        suitable_adapters = []
        for capability in required_capabilities:
            if capability in self.capability_map:
                for adapter_id in self.capability_map[capability]:
                    if adapter_id in self.adapters:
                        suitable_adapters.append(self.adapters[adapter_id])
        
        # Return the first suitable adapter
        return suitable_adapters[0] if suitable_adapters else None
    
    def get_adapter(self, adapter_id: str) -> Optional[ConcurrentWorkerAdapter]:
        """Get a specific adapter by ID."""
        return self.adapters.get(adapter_id)
    
    def list_adapters(self) -> Dict[str, Dict[str, Any]]:
        """List all registered adapters and their information."""
        return {
            adapter_id: adapter.get_agent_info()
            for adapter_id, adapter in self.adapters.items()
        }
    
    def execute_subtask_with_best_adapter(self, subtask_data: Dict[str, Any], 
                                        context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a subtask using the best available adapter.
        
        Args:
            subtask_data: Subtask data to execute
            context: Additional context
            
        Returns:
            Execution result
        """
        required_capabilities = subtask_data.get("required_capabilities", [])
        
        # Find suitable adapter
        adapter = self.find_suitable_adapter(required_capabilities)
        
        if not adapter:
            logger.warning(f"No suitable adapter found for capabilities: {required_capabilities}")
            return {
                "subtask_id": subtask_data.get("task_id", "unknown"),
                "status": "failed",
                "error": f"No suitable adapter for capabilities: {required_capabilities}",
                "execution_time": 0.0,
                "completed_at": datetime.utcnow().isoformat()
            }
        
        # Execute the subtask
        return adapter.execute_subtask(subtask_data, context)


class ConcurrentExecutionPool:
    """
    Pool for managing concurrent execution of subtasks.
    
    This class provides high-level methods for executing multiple subtasks
    concurrently using thread pools and worker adapters.
    """
    
    def __init__(self, max_workers: int = 4, worker_registry: ConcurrentWorkerRegistry = None):
        """
        Initialize the concurrent execution pool.
        
        Args:
            max_workers: Maximum number of concurrent workers
            worker_registry: Registry of worker adapters
        """
        self.max_workers = max_workers
        self.worker_registry = worker_registry or ConcurrentWorkerRegistry()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        logger.info(f"Concurrent execution pool initialized with {max_workers} workers")
    
    def execute_subtasks_concurrently(self, subtasks: List[Dict[str, Any]], 
                                    context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute multiple subtasks concurrently.
        
        Args:
            subtasks: List of subtask data to execute
            context: Shared context for all subtasks
            
        Returns:
            List of execution results
        """
        if not subtasks:
            return []
        
        logger.info(f"Starting concurrent execution of {len(subtasks)} subtasks")
        
        # Submit all subtasks for concurrent execution
        future_to_subtask = {}
        for subtask in subtasks:
            future = self.executor.submit(
                self.worker_registry.execute_subtask_with_best_adapter,
                subtask,
                context
            )
            future_to_subtask[future] = subtask
        
        # Collect results as they complete
        results = []
        for future in as_completed(future_to_subtask):
            subtask = future_to_subtask[future]
            try:
                result = future.result()
                results.append(result)
                logger.debug(f"Subtask {subtask.get('task_id', 'unknown')} completed")
            except Exception as e:
                logger.error(f"Subtask {subtask.get('task_id', 'unknown')} failed: {str(e)}")
                # Create error result
                error_result = {
                    "subtask_id": subtask.get("task_id", "unknown"),
                    "status": "failed",
                    "error": f"Execution error: {str(e)}",
                    "execution_time": 0.0,
                    "completed_at": datetime.utcnow().isoformat()
                }
                results.append(error_result)
        
        logger.info(f"Concurrent execution completed: {len(results)} results")
        return results
    
    def shutdown(self, wait: bool = True):
        """
        Shutdown the execution pool.
        
        Args:
            wait: Whether to wait for pending tasks to complete
        """
        self.executor.shutdown(wait=wait)
        logger.info("Concurrent execution pool shutdown")


# Global instances for easy access
_global_worker_registry = None
_global_execution_pool = None


def get_global_worker_registry() -> ConcurrentWorkerRegistry:
    """Get the global worker registry instance."""
    global _global_worker_registry
    if _global_worker_registry is None:
        _global_worker_registry = ConcurrentWorkerRegistry()
    return _global_worker_registry


def get_global_execution_pool(max_workers: int = 4) -> ConcurrentExecutionPool:
    """Get the global execution pool instance."""
    global _global_execution_pool
    if _global_execution_pool is None:
        _global_execution_pool = ConcurrentExecutionPool(
            max_workers=max_workers,
            worker_registry=get_global_worker_registry()
        )
    return _global_execution_pool
