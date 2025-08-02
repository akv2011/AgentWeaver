"""
AgentWeaver - A sophisticated multi-agent orchestration system built with LangGraph.

This package provides the core functionality for creating, managing, and orchestrating
multiple AI agents in complex workflows with advanced communication patterns,
supervision, and failure handling.
"""

__version__ = "0.1.0"
__author__ = "AgentWeaver Team"

# Import core components
from .core import (
    AgentState, Task, Message, WorkflowState, SystemState,
    TaskStatus, TaskPriority, MessageType, MessagePriority, 
    AgentCapability, AgentStatus, StateManager, RedisConfig
)

# Import orchestration components
from .orchestration import (
    SupervisorNode, EnhancedSupervisor, SwarmSupervisorNode,
    ParallelForkNode, ParallelWorkerNode, ParallelAggregatorNode,
    ParallelExecutionState, create_parallel_execution_router
)

# Import communication components
from .communication import (
    P2PCommunicationManager, AgentRegistry, 
    HierarchicalWorkflowOrchestrator
)

# Import workflow components
from .linear_workflow import LinearWorkflowOrchestrator
from .conditional_workflow import ConditionalWorkflowOrchestrator

__all__ = [
    # Core components
    "AgentState", "Task", "Message", "WorkflowState", "SystemState",
    "TaskStatus", "TaskPriority", "MessageType", "MessagePriority", 
    "AgentCapability", "AgentStatus", "StateManager", "RedisConfig",
    
    # Orchestration components
    "SupervisorNode", "EnhancedSupervisor", "SwarmSupervisorNode",
    "ParallelForkNode", "ParallelWorkerNode", "ParallelAggregatorNode",
    "ParallelExecutionState", "create_parallel_execution_router",
    
    # Communication components
    "P2PCommunicationManager", "AgentRegistry", 
    "HierarchicalWorkflowOrchestrator",
    
    # Workflow components
    "LinearWorkflowOrchestrator", "ConditionalWorkflowOrchestrator"
]
