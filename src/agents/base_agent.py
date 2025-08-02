"""
Base Worker Agent for AgentWeaver.

This module defines the base structure and interface that all worker agents 
must implement to integrate with the LangGraph and Supervisor system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..models import AgentState, AgentCapability, AgentStatus, Task, TaskStatus


logger = logging.getLogger(__name__)


class BaseWorkerAgent(ABC):
    """
    Abstract base class for all worker agents in the AgentWeaver system.
    
    This class defines the standard interface that all worker agents must implement
    to work with the LangGraph state management and Supervisor node.
    """
    
    def __init__(self, name: str, capabilities: List[AgentCapability], agent_type: str = "worker"):
        """
        Initialize the base worker agent.
        
        Args:
            name: Human-readable name for the agent
            capabilities: List of capabilities this agent provides
            agent_type: Type of agent (default: "worker")
        """
        self.agent_state = AgentState(
            name=name,
            agent_type=agent_type,
            capabilities=capabilities,
            status=AgentStatus.AVAILABLE
        )
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @property
    def agent_id(self) -> str:
        """Get the unique agent ID."""
        return self.agent_state.agent_id
    
    @property
    def name(self) -> str:
        """Get the agent name."""
        return self.agent_state.name
    
    @property
    def capabilities(self) -> List[AgentCapability]:
        """Get the agent's capabilities."""
        return self.agent_state.capabilities
    
    @property
    def status(self) -> AgentStatus:
        """Get the current agent status."""
        return self.agent_state.status
    
    @abstractmethod
    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task assigned to this agent.
        
        This is the main method that contains the agent's core logic.
        Each agent implementation must override this method.
        
        Args:
            task: The task to execute
            context: Additional context data from the graph state
            
        Returns:
            Dictionary containing the result of the task execution
            
        Raises:
            Exception: If the task execution fails
        """
        pass
    
    def can_handle_task(self, task: Task) -> bool:
        """
        Check if this agent can handle the given task.
        
        Args:
            task: The task to check
            
        Returns:
            True if the agent can handle the task, False otherwise
        """
        # Check if any of the task's required capabilities match this agent's capabilities
        if not task.required_capabilities:
            return True  # If no specific capabilities required, any agent can handle it
        
        return any(cap in self.capabilities for cap in task.required_capabilities)
    
    def start_task(self, task: Task) -> None:
        """
        Mark the agent as busy and start working on a task.
        
        Args:
            task: The task being started
        """
        self.agent_state.status = AgentStatus.BUSY
        self.agent_state.current_task_id = task.task_id
        self.agent_state.last_activity = datetime.utcnow()
        self.agent_state.last_updated = datetime.utcnow()
        
        self.logger.info(f"Agent {self.name} starting task {task.task_id}: {task.title}")
    
    def complete_task(self, task: Task, execution_time: float = 0.0, success: bool = True) -> None:
        """
        Mark the agent as available and update performance metrics.
        
        Args:
            task: The completed task
            execution_time: Time taken to execute the task in seconds
            success: Whether the task was completed successfully
        """
        self.agent_state.status = AgentStatus.AVAILABLE
        self.agent_state.current_task_id = None
        self.agent_state.update_performance(execution_time, success)
        
        status_msg = "completed successfully" if success else "failed"
        self.logger.info(f"Agent {self.name} {status_msg} task {task.task_id} in {execution_time:.2f}s")
    
    def set_error(self, error_message: str) -> None:
        """
        Set the agent to error status.
        
        Args:
            error_message: Description of the error
        """
        self.agent_state.status = AgentStatus.ERROR
        self.agent_state.error_message = error_message
        self.agent_state.health_check_passed = False
        self.agent_state.last_updated = datetime.utcnow()
        
        self.logger.error(f"Agent {self.name} error: {error_message}")
    
    def reset_error(self) -> None:
        """Reset the agent from error status to available."""
        self.agent_state.status = AgentStatus.AVAILABLE
        self.agent_state.error_message = None
        self.agent_state.health_check_passed = True
        self.agent_state.last_updated = datetime.utcnow()
        
        self.logger.info(f"Agent {self.name} error status cleared")
    
    def health_check(self) -> bool:
        """
        Perform a health check on the agent.
        
        Returns:
            True if the agent is healthy, False otherwise
        """
        try:
            # Basic health check - override in subclasses for specific checks
            is_healthy = (
                self.agent_state.status != AgentStatus.ERROR and
                self.agent_state.status != AgentStatus.OFFLINE
            )
            
            self.agent_state.health_check_passed = is_healthy
            self.agent_state.last_updated = datetime.utcnow()
            
            return is_healthy
            
        except Exception as e:
            self.logger.error(f"Health check failed for agent {self.name}: {str(e)}")
            self.set_error(f"Health check failed: {str(e)}")
            return False
    
    def get_state(self) -> AgentState:
        """
        Get the current state of the agent.
        
        Returns:
            Copy of the agent's current state
        """
        return self.agent_state.copy(deep=True)
    
    def update_context(self, context: Dict[str, Any]) -> None:
        """
        Update the agent's context data.
        
        Args:
            context: New context data to merge with existing context
        """
        self.agent_state.context.update(context)
        self.agent_state.last_updated = datetime.utcnow()
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.name}', id='{self.agent_id}', status='{self.status}')"
    
    def __repr__(self) -> str:
        """Detailed string representation of the agent."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"id='{self.agent_id}', "
            f"status='{self.status}', "
            f"capabilities={[cap.value for cap in self.capabilities]}"
            f")"
        )
