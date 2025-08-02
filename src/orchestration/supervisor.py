"""
Supervisor Node Implementation for AgentWeaver
==============================================

This module implements the central Supervisor Node as a LangGraph node.
The supervisor handles agent registration, health monitoring, and task assignment.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid
import logging
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from ..core.models import (
    AgentState, Task, Message, WorkflowState, SystemState,
    TaskStatus, TaskPriority, MessageType, MessagePriority, 
    AgentCapability, AgentStatus
)

logger = logging.getLogger(__name__)


class SupervisorNode:
    """
    Central Supervisor Node for managing worker agents and task assignment.
    
    This class implements the supervisor as a LangGraph node that maintains
    a registry of available worker agents, monitors their health, and assigns
    tasks based on agent capabilities and availability.
    """
    
    def __init__(self, checkpointer: Optional[MemorySaver] = None):
        """
        Initialize the Supervisor Node.
        
        Args:
            checkpointer: Optional MemorySaver for state persistence
        """
        self.checkpointer = checkpointer or MemorySaver()
        self.agent_registry: Dict[str, AgentState] = {}
        self.task_queue: List[Task] = []
        self.system_state = SystemState()
        self._setup_supervisor_graph()
        
    def _setup_supervisor_graph(self):
        """Set up the LangGraph StateGraph for the supervisor."""
        # Create the graph with our SystemState
        graph = StateGraph(dict)
        
        # Add supervisor nodes
        graph.add_node("register_agent", self._register_agent_node)
        graph.add_node("unregister_agent", self._unregister_agent_node)
        graph.add_node("assign_task", self._assign_task_node)
        graph.add_node("monitor_health", self._monitor_health_node)
        graph.add_node("process_supervisor_message", self._process_supervisor_message_node)
        
        # Define routing function
        def route_message(state: Dict[str, Any]) -> str:
            """Route messages to appropriate nodes based on message type."""
            message = state.get("message")
            if not message:
                return "monitor_health"  # Default action
                
            message_type = message.get("type", "health_check")
            
            if message_type == "register_agent":
                return "register_agent"
            elif message_type == "unregister_agent":
                return "unregister_agent"
            elif message_type == "assign_task":
                return "assign_task"
            elif message_type == "health_check":
                return "monitor_health"
            else:
                return "monitor_health"  # Default
                
        # Add edges with conditional routing
        graph.add_edge(START, "process_supervisor_message")
        graph.add_conditional_edges(
            "process_supervisor_message",
            route_message,
            {
                "register_agent": "register_agent",
                "unregister_agent": "unregister_agent", 
                "assign_task": "assign_task",
                "monitor_health": "monitor_health"
            }
        )
        graph.add_edge("register_agent", END)
        graph.add_edge("unregister_agent", END)
        graph.add_edge("assign_task", END)
        graph.add_edge("monitor_health", END)
        
        # Compile the graph
        self.supervisor_graph = graph.compile(checkpointer=self.checkpointer)
        
    def _register_agent_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        LangGraph node for registering a new agent with the supervisor.
        
        Args:
            state: Current state containing agent information
            
        Returns:
            Updated state with registered agent
        """
        try:
            agent_data = state.get("agent_to_register")
            if not agent_data:
                # Create default agent data if none provided
                agent_data = {
                    "name": "Unknown Agent",
                    "capabilities": []
                }
                
            # Create AgentState from provided data
            agent = AgentState(
                agent_id=agent_data.get("agent_id", str(uuid.uuid4())),
                name=agent_data.get("name", "Unknown Agent"),
                capabilities=agent_data.get("capabilities", []),
                status=AgentStatus.AVAILABLE,
                current_task_id=None
            )
            
            # Register the agent
            self.agent_registry[agent.agent_id] = agent
            
            # Update system state
            if "system_state" not in state:
                state["system_state"] = {}
            state["system_state"]["total_agents"] = len(self.agent_registry)
            state["system_state"]["available_agents"] = len([
                a for a in self.agent_registry.values() 
                if a.status == AgentStatus.AVAILABLE
            ])
            
            logger.info(f"Agent {agent.agent_id} ({agent.name}) registered successfully")
            state["registration_result"] = {
                "success": True,
                "agent_id": agent.agent_id,
                "message": f"Agent {agent.name} registered successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to register agent: {str(e)}")
            state["registration_result"] = {
                "success": False,
                "error": str(e)
            }
            
        return state
        
    def _unregister_agent_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        LangGraph node for unregistering an agent from the supervisor.
        
        Args:
            state: Current state containing agent ID to unregister
            
        Returns:
            Updated state with agent removed
        """
        try:
            agent_id = state.get("agent_id_to_unregister")
            if not agent_id:
                logger.error("No agent ID provided for unregistration")
                return state
                
            if agent_id in self.agent_registry:
                agent = self.agent_registry[agent_id]
                del self.agent_registry[agent_id]
                
                # Update system state
                if "system_state" not in state:
                    state["system_state"] = {}
                state["system_state"]["total_agents"] = len(self.agent_registry)
                state["system_state"]["available_agents"] = len([
                    a for a in self.agent_registry.values() 
                    if a.status == AgentStatus.AVAILABLE
                ])
                
                logger.info(f"Agent {agent_id} ({agent.name}) unregistered successfully")
                state["unregistration_result"] = {
                    "success": True,
                    "agent_id": agent_id,
                    "message": f"Agent {agent.name} unregistered successfully"
                }
            else:
                logger.warning(f"Agent {agent_id} not found in registry")
                state["unregistration_result"] = {
                    "success": False,
                    "error": f"Agent {agent_id} not found"
                }
                
        except Exception as e:
            logger.error(f"Failed to unregister agent: {str(e)}")
            state["unregistration_result"] = {
                "success": False,
                "error": str(e)
            }
            
        return state
        
    def _assign_task_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        LangGraph node for assigning tasks to available agents.
        
        Args:
            state: Current state containing task to assign
            
        Returns:
            Updated state with task assignment result
        """
        try:
            task_data = state.get("task_to_assign")
            if not task_data:
                logger.error("No task data provided for assignment")
                return state
                
            # Create Task from provided data
            task = Task(
                task_id=task_data.get("task_id", str(uuid.uuid4())),
                title=task_data.get("title", "Untitled Task"),
                description=task_data.get("description", ""),
                required_capabilities=task_data.get("required_capabilities", []),
                priority=TaskPriority(task_data.get("priority", "medium")),
                status=TaskStatus.PENDING
            )
            
            # Find suitable agent
            suitable_agent = self._find_suitable_agent(task)
            
            if suitable_agent:
                # Assign task to agent
                suitable_agent.status = AgentStatus.BUSY
                suitable_agent.current_task_id = task.task_id
                task.assigned_agent_id = suitable_agent.agent_id
                task.status = TaskStatus.IN_PROGRESS
                task.assign_task(suitable_agent.agent_id)
                
                # Update system state
                if "system_state" not in state:
                    state["system_state"] = {}
                state["system_state"]["available_agents"] = len([
                    a for a in self.agent_registry.values() 
                    if a.status == AgentStatus.AVAILABLE
                ])
                state["system_state"]["busy_agents"] = len([
                    a for a in self.agent_registry.values() 
                    if a.status == AgentStatus.BUSY
                ])
                
                logger.info(f"Task {task.task_id} assigned to agent {suitable_agent.agent_id}")
                state["assignment_result"] = {
                    "success": True,
                    "task_id": task.task_id,
                    "agent_id": suitable_agent.agent_id,
                    "message": f"Task assigned to agent {suitable_agent.name}"
                }
            else:
                # No suitable agent available, add to queue
                self.task_queue.append(task)
                logger.info(f"Task {task.task_id} added to queue - no suitable agent available")
                state["assignment_result"] = {
                    "success": False,
                    "task_id": task.task_id,
                    "message": "No suitable agent available, task queued"
                }
                
        except Exception as e:
            logger.error(f"Failed to assign task: {str(e)}")
            state["assignment_result"] = {
                "success": False,
                "error": str(e)
            }
            
        return state
        
    def _monitor_health_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        LangGraph node for monitoring agent health and availability.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with health monitoring results
        """
        try:
            health_report = {
                "timestamp": datetime.now().isoformat(),
                "total_agents": len(self.agent_registry),
                "available_agents": 0,
                "busy_agents": 0,
                "offline_agents": 0,
                "queued_tasks": len(self.task_queue),
                "agent_details": []
            }
            
            # Check each agent's health
            for agent in self.agent_registry.values():
                if agent.status == AgentStatus.AVAILABLE:
                    health_report["available_agents"] += 1
                elif agent.status == AgentStatus.BUSY:
                    health_report["busy_agents"] += 1
                else:
                    health_report["offline_agents"] += 1
                    
                agent_detail = {
                    "agent_id": agent.agent_id,
                    "name": agent.name,
                    "status": agent.status.value,
                    "capabilities": [cap.value for cap in agent.capabilities],
                    "current_task": agent.current_task_id,
                    "last_updated": agent.last_updated.isoformat()
                }
                health_report["agent_details"].append(agent_detail)
                
            # Update system state
            if "system_state" not in state:
                state["system_state"] = {}
            state["system_state"].update({
                "total_agents": health_report["total_agents"],
                "available_agents": health_report["available_agents"],
                "busy_agents": health_report["busy_agents"],
                "queued_tasks": health_report["queued_tasks"]
            })
            
            state["health_report"] = health_report
            logger.info(f"Health check completed: {health_report['available_agents']} available, "
                       f"{health_report['busy_agents']} busy, {health_report['queued_tasks']} queued tasks")
                       
        except Exception as e:
            logger.error(f"Health monitoring failed: {str(e)}")
            state["health_report"] = {"error": str(e)}
            
        return state
        
    def _process_supervisor_message_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        LangGraph node for processing incoming supervisor messages.
        
        Args:
            state: Current state containing message to process
            
        Returns:
            Updated state with message processing result
        """
        try:
            message_data = state.get("message")
            if not message_data:
                # No message to process, return state as-is
                return state
                
            message_type = message_data.get("type", "general")
            
            # Route message based on type and set up data for next node
            if message_type == "register_agent":
                state["agent_to_register"] = message_data.get("content")
            elif message_type == "unregister_agent":
                content = message_data.get("content", {})
                if isinstance(content, dict):
                    state["agent_id_to_unregister"] = content.get("agent_id")
                else:
                    state["agent_id_to_unregister"] = content
            elif message_type == "assign_task":
                state["task_to_assign"] = message_data.get("content")
            elif message_type == "health_check":
                # Health check will be processed by monitor_health_node
                pass
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
            logger.info(f"Processed supervisor message of type: {message_type}")
            
        except Exception as e:
            logger.error(f"Failed to process supervisor message: {str(e)}")
            state["message_processing_error"] = str(e)
            
        return state
        
    def _find_suitable_agent(self, task: Task) -> Optional[AgentState]:
        """
        Find a suitable agent for the given task based on capabilities and availability.
        
        Args:
            task: Task to find an agent for
            
        Returns:
            Suitable AgentState if found, None otherwise
        """
        for agent in self.agent_registry.values():
            if (agent.status == AgentStatus.AVAILABLE and 
                self._agent_has_required_capabilities(agent, task.required_capabilities)):
                return agent
        return None
        
    def _agent_has_required_capabilities(self, agent: AgentState, 
                                       required_capabilities: List[AgentCapability]) -> bool:
        """
        Check if an agent has all required capabilities for a task.
        
        Args:
            agent: Agent to check
            required_capabilities: List of required capabilities
            
        Returns:
            True if agent has all required capabilities, False otherwise
        """
        if not required_capabilities:
            return True
            
        agent_capabilities = set(agent.capabilities)
        required_set = set(required_capabilities)
        return required_set.issubset(agent_capabilities)
        
    # Public interface methods
    
    def register_agent(self, agent_data: Dict[str, Any], thread_id: str = "supervisor") -> Dict[str, Any]:
        """
        Register a new agent with the supervisor.
        
        Args:
            agent_data: Dictionary containing agent information
            thread_id: Thread ID for state management
            
        Returns:
            Registration result
        """
        initial_state = {
            "message": {
                "type": "register_agent",
                "content": agent_data
            }
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        result = self.supervisor_graph.invoke(initial_state, config)
        
        return result.get("registration_result", {"success": False, "error": "Unknown error"})
        
    def unregister_agent(self, agent_id: str, thread_id: str = "supervisor") -> Dict[str, Any]:
        """
        Unregister an agent from the supervisor.
        
        Args:
            agent_id: ID of agent to unregister
            thread_id: Thread ID for state management
            
        Returns:
            Unregistration result
        """
        initial_state = {
            "message": {
                "type": "unregister_agent",
                "content": {"agent_id": agent_id}
            }
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        result = self.supervisor_graph.invoke(initial_state, config)
        
        return result.get("unregistration_result", {"success": False, "error": "Unknown error"})
        
    def assign_task(self, task_data: Dict[str, Any], thread_id: str = "supervisor") -> Dict[str, Any]:
        """
        Assign a task to an available agent.
        
        Args:
            task_data: Dictionary containing task information
            thread_id: Thread ID for state management
            
        Returns:
            Assignment result
        """
        initial_state = {
            "message": {
                "type": "assign_task",
                "content": task_data
            }
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        result = self.supervisor_graph.invoke(initial_state, config)
        
        return result.get("assignment_result", {"success": False, "error": "Unknown error"})
        
    def get_health_report(self, thread_id: str = "supervisor") -> Dict[str, Any]:
        """
        Get a health report of all registered agents.
        
        Args:
            thread_id: Thread ID for state management
            
        Returns:
            Health report
        """
        initial_state = {
            "message": {
                "type": "health_check",
                "content": {}
            }
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        result = self.supervisor_graph.invoke(initial_state, config)
        
        return result.get("health_report", {"error": "Health check failed"})
        
    def get_agent_registry(self) -> Dict[str, AgentState]:
        """
        Get the current agent registry.
        
        Returns:
            Dictionary mapping agent IDs to AgentState objects
        """
        return self.agent_registry.copy()
        
    def get_task_queue(self) -> List[Task]:
        """
        Get the current task queue.
        
        Returns:
            List of queued tasks
        """
        return self.task_queue.copy()
        
    def mark_task_complete(self, task_id: str, agent_id: str) -> bool:
        """
        Mark a task as complete and free up the assigned agent.
        
        Args:
            task_id: ID of completed task
            agent_id: ID of agent that completed the task
            
        Returns:
            True if task was marked complete, False otherwise
        """
        try:
            if agent_id in self.agent_registry:
                agent = self.agent_registry[agent_id]
                if agent.current_task_id == task_id:
                    agent.status = AgentStatus.AVAILABLE
                    agent.current_task_id = None
                    agent.update_performance(success=True)
                    logger.info(f"Task {task_id} completed by agent {agent_id}")
                    
                    # Try to assign queued tasks
                    self._process_queued_tasks()
                    return True
                    
            logger.warning(f"Task {task_id} completion failed - agent {agent_id} not found or task mismatch")
            return False
            
        except Exception as e:
            logger.error(f"Failed to mark task complete: {str(e)}")
            return False
            
    def _process_queued_tasks(self):
        """Process any queued tasks that can now be assigned."""
        tasks_to_remove = []
        
        for i, task in enumerate(self.task_queue):
            suitable_agent = self._find_suitable_agent(task)
            if suitable_agent:
                # Assign the task
                suitable_agent.status = AgentStatus.BUSY
                suitable_agent.current_task_id = task.task_id
                task.assigned_agent_id = suitable_agent.agent_id
                task.status = TaskStatus.IN_PROGRESS
                task.assign_task(suitable_agent.agent_id)
                
                tasks_to_remove.append(i)
                logger.info(f"Queued task {task.task_id} assigned to agent {suitable_agent.agent_id}")
                
        # Remove assigned tasks from queue (in reverse order to maintain indices)
        for i in reversed(tasks_to_remove):
            del self.task_queue[i]
