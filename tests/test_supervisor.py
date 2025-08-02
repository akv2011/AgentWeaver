"""
Unit tests for the Supervisor Node implementation.

Tests the core functionality of the SupervisorNode including:
- Agent registration and unregistration
- Task assignment and queuing
- Health monitoring
- Message processing
"""

import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, patch

from src.supervisor import SupervisorNode
from src.models import (
    AgentState, Task, AgentCapability, AgentStatus, 
    TaskStatus, TaskPriority
)


class TestSupervisorNode:
    """Test suite for SupervisorNode functionality."""
    
    @pytest.fixture
    def supervisor(self):
        """Create a fresh SupervisorNode instance for each test."""
        return SupervisorNode()
        
    @pytest.fixture
    def sample_agent_data(self):
        """Sample agent data for testing."""
        return {
            "agent_id": "test-agent-1",
            "name": "Test Agent",
            "capabilities": [AgentCapability.RESEARCH, AgentCapability.ANALYSIS]
        }
        
    @pytest.fixture
    def sample_task_data(self):
        """Sample task data for testing."""
        return {
            "task_id": "test-task-1",
            "title": "Test Task",
            "description": "A test task for validation",
            "required_capabilities": [AgentCapability.RESEARCH],
            "priority": "high"
        }
        
    def test_supervisor_initialization(self, supervisor):
        """Test that supervisor initializes correctly."""
        assert supervisor.agent_registry == {}
        assert supervisor.task_queue == []
        assert supervisor.system_state is not None
        assert supervisor.supervisor_graph is not None
        assert supervisor.checkpointer is not None
        
    def test_register_agent_success(self, supervisor, sample_agent_data):
        """Test successful agent registration."""
        result = supervisor.register_agent(sample_agent_data)
        
        assert result["success"] is True
        assert result["agent_id"] == "test-agent-1"
        assert "registered successfully" in result["message"]
        
        # Verify agent is in registry
        assert "test-agent-1" in supervisor.agent_registry
        agent = supervisor.agent_registry["test-agent-1"]
        assert agent.name == "Test Agent"
        assert agent.status == AgentStatus.AVAILABLE
        assert AgentCapability.RESEARCH in agent.capabilities
        assert AgentCapability.ANALYSIS in agent.capabilities
        
    def test_register_agent_with_auto_id(self, supervisor):
        """Test agent registration with auto-generated ID."""
        agent_data = {
            "name": "Auto ID Agent",
            "capabilities": [AgentCapability.COORDINATION]
        }
        
        result = supervisor.register_agent(agent_data)
        
        assert result["success"] is True
        assert "agent_id" in result
        
        # Verify agent is registered with generated ID
        agent_id = result["agent_id"]
        assert agent_id in supervisor.agent_registry
        assert supervisor.agent_registry[agent_id].name == "Auto ID Agent"
        
    def test_register_agent_empty_data(self, supervisor):
        """Test agent registration with missing data."""
        result = supervisor.register_agent({})
        
        # Should still succeed with defaults
        assert result["success"] is True
        assert len(supervisor.agent_registry) == 1
        
    def test_unregister_agent_success(self, supervisor, sample_agent_data):
        """Test successful agent unregistration."""
        # First register an agent
        supervisor.register_agent(sample_agent_data)
        assert "test-agent-1" in supervisor.agent_registry
        
        # Then unregister it
        result = supervisor.unregister_agent("test-agent-1")
        
        assert result["success"] is True
        assert result["agent_id"] == "test-agent-1"
        assert "unregistered successfully" in result["message"]
        assert "test-agent-1" not in supervisor.agent_registry
        
    def test_unregister_nonexistent_agent(self, supervisor):
        """Test unregistering an agent that doesn't exist."""
        result = supervisor.unregister_agent("nonexistent-agent")
        
        assert result["success"] is False
        assert "not found" in result["error"]
        
    def test_assign_task_to_available_agent(self, supervisor, sample_agent_data, sample_task_data):
        """Test task assignment to an available agent."""
        # Register an agent first
        supervisor.register_agent(sample_agent_data)
        
        # Assign a task
        result = supervisor.assign_task(sample_task_data)
        
        assert result["success"] is True
        assert result["task_id"] == "test-task-1"
        assert result["agent_id"] == "test-agent-1"
        assert "assigned to agent" in result["message"]
        
        # Verify agent status updated
        agent = supervisor.agent_registry["test-agent-1"]
        assert agent.status == AgentStatus.BUSY
        assert agent.current_task_id == "test-task-1"
        
    def test_assign_task_no_available_agent(self, supervisor, sample_task_data):
        """Test task assignment when no agents are available."""
        result = supervisor.assign_task(sample_task_data)
        
        assert result["success"] is False
        assert "no suitable agent available" in result["message"].lower()
        assert len(supervisor.task_queue) == 1
        assert supervisor.task_queue[0].task_id == "test-task-1"
        
    def test_assign_task_capability_mismatch(self, supervisor, sample_task_data):
        """Test task assignment when agent lacks required capabilities."""
        # Register agent with different capabilities
        agent_data = {
            "agent_id": "limited-agent",
            "name": "Limited Agent",
            "capabilities": [AgentCapability.COORDINATION]  # Different from task requirement
        }
        supervisor.register_agent(agent_data)
        
        # Try to assign task requiring RESEARCH capability
        result = supervisor.assign_task(sample_task_data)
        
        assert result["success"] is False
        assert len(supervisor.task_queue) == 1
        
    def test_assign_task_with_auto_id(self, supervisor, sample_agent_data):
        """Test task assignment with auto-generated task ID."""
        supervisor.register_agent(sample_agent_data)
        
        task_data = {
            "title": "Auto ID Task",
            "description": "Task with auto-generated ID",
            "required_capabilities": [AgentCapability.RESEARCH]
        }
        
        result = supervisor.assign_task(task_data)
        
        assert result["success"] is True
        assert "task_id" in result
        assert result["agent_id"] == "test-agent-1"
        
    def test_health_report_empty_registry(self, supervisor):
        """Test health report with no registered agents."""
        report = supervisor.get_health_report()
        
        assert "error" not in report
        assert report["total_agents"] == 0
        assert report["available_agents"] == 0
        assert report["busy_agents"] == 0
        assert report["queued_tasks"] == 0
        assert report["agent_details"] == []
        
    def test_health_report_with_agents(self, supervisor, sample_agent_data, sample_task_data):
        """Test health report with registered agents."""
        # Register agent and assign task
        supervisor.register_agent(sample_agent_data)
        supervisor.assign_task(sample_task_data)
        
        # Register another available agent
        agent_data_2 = {
            "agent_id": "test-agent-2",
            "name": "Available Agent",
            "capabilities": [AgentCapability.ANALYSIS]
        }
        supervisor.register_agent(agent_data_2)
        
        report = supervisor.get_health_report()
        
        assert report["total_agents"] == 2
        assert report["available_agents"] == 1
        assert report["busy_agents"] == 1
        assert report["queued_tasks"] == 0
        assert len(report["agent_details"]) == 2
        
        # Check agent details
        agent_details = {detail["agent_id"]: detail for detail in report["agent_details"]}
        assert agent_details["test-agent-1"]["status"] == "busy"
        assert agent_details["test-agent-1"]["current_task"] == "test-task-1"
        assert agent_details["test-agent-2"]["status"] == "available"
        assert agent_details["test-agent-2"]["current_task"] is None
        
    def test_mark_task_complete_success(self, supervisor, sample_agent_data, sample_task_data):
        """Test marking a task as complete."""
        # Register agent and assign task
        supervisor.register_agent(sample_agent_data)
        supervisor.assign_task(sample_task_data)
        
        # Verify agent is busy
        agent = supervisor.agent_registry["test-agent-1"]
        assert agent.status == AgentStatus.BUSY
        assert agent.current_task_id == "test-task-1"
        
        # Mark task complete
        result = supervisor.mark_task_complete("test-task-1", "test-agent-1")
        
        assert result is True
        assert agent.status == AgentStatus.AVAILABLE
        assert agent.current_task_id is None
        
    def test_mark_task_complete_wrong_agent(self, supervisor, sample_agent_data, sample_task_data):
        """Test marking a task complete with wrong agent ID."""
        supervisor.register_agent(sample_agent_data)
        supervisor.assign_task(sample_task_data)
        
        result = supervisor.mark_task_complete("test-task-1", "wrong-agent")
        
        assert result is False
        # Agent should still be busy
        agent = supervisor.agent_registry["test-agent-1"]
        assert agent.status == AgentStatus.BUSY
        
    def test_mark_task_complete_wrong_task(self, supervisor, sample_agent_data, sample_task_data):
        """Test marking a task complete with wrong task ID."""
        supervisor.register_agent(sample_agent_data)
        supervisor.assign_task(sample_task_data)
        
        result = supervisor.mark_task_complete("wrong-task", "test-agent-1")
        
        assert result is False
        # Agent should still be busy
        agent = supervisor.agent_registry["test-agent-1"]
        assert agent.status == AgentStatus.BUSY
        
    def test_queued_task_assignment_after_completion(self, supervisor, sample_agent_data):
        """Test that queued tasks get assigned when agents become available."""
        # Register one agent
        supervisor.register_agent(sample_agent_data)
        
        # Assign first task
        task_data_1 = {
            "task_id": "task-1",
            "title": "First Task",
            "required_capabilities": [AgentCapability.RESEARCH]
        }
        result1 = supervisor.assign_task(task_data_1)
        assert result1["success"] is True
        
        # Try to assign second task (should be queued)
        task_data_2 = {
            "task_id": "task-2", 
            "title": "Second Task",
            "required_capabilities": [AgentCapability.RESEARCH]
        }
        result2 = supervisor.assign_task(task_data_2)
        assert result2["success"] is False
        assert len(supervisor.task_queue) == 1
        
        # Complete first task
        supervisor.mark_task_complete("task-1", "test-agent-1")
        
        # Second task should now be assigned
        assert len(supervisor.task_queue) == 0
        agent = supervisor.agent_registry["test-agent-1"]
        assert agent.status == AgentStatus.BUSY
        assert agent.current_task_id == "task-2"
        
    def test_get_agent_registry(self, supervisor, sample_agent_data):
        """Test getting agent registry copy."""
        supervisor.register_agent(sample_agent_data)
        
        registry = supervisor.get_agent_registry()
        
        assert len(registry) == 1
        assert "test-agent-1" in registry
        
        # Verify it's a copy (modifications don't affect original)
        registry.clear()
        assert len(supervisor.agent_registry) == 1
        
    def test_get_task_queue(self, supervisor, sample_task_data):
        """Test getting task queue copy."""
        supervisor.assign_task(sample_task_data)  # Should be queued (no agents)
        
        queue = supervisor.get_task_queue()
        
        assert len(queue) == 1
        assert queue[0].task_id == "test-task-1"
        
        # Verify it's a copy
        queue.clear()
        assert len(supervisor.task_queue) == 1
        
    def test_agent_capability_matching(self, supervisor):
        """Test that agents are matched based on capabilities."""
        # Register agent with specific capabilities
        agent_data = {
            "agent_id": "specialist-agent",
            "name": "Specialist Agent",
            "capabilities": [AgentCapability.RESEARCH, AgentCapability.ANALYSIS]
        }
        supervisor.register_agent(agent_data)
        
        # Task requiring only research - should match
        task_research = {
            "task_id": "research-task",
            "title": "Research Task",
            "required_capabilities": [AgentCapability.RESEARCH]
        }
        result1 = supervisor.assign_task(task_research)
        assert result1["success"] is True
        
        # Complete the task
        supervisor.mark_task_complete("research-task", "specialist-agent")
        
        # Task requiring coordination - should not match
        task_coordination = {
            "task_id": "coordination-task",
            "title": "Coordination Task", 
            "required_capabilities": [AgentCapability.COORDINATION]
        }
        result2 = supervisor.assign_task(task_coordination)
        assert result2["success"] is False
        assert len(supervisor.task_queue) == 1
        
    def test_multiple_required_capabilities(self, supervisor):
        """Test task assignment with multiple required capabilities."""
        # Register agent with multiple capabilities
        agent_data = {
            "agent_id": "multi-agent",
            "name": "Multi-capability Agent",
            "capabilities": [
                AgentCapability.RESEARCH, 
                AgentCapability.ANALYSIS, 
                AgentCapability.COORDINATION
            ]
        }
        supervisor.register_agent(agent_data)
        
        # Task requiring multiple capabilities
        task_data = {
            "task_id": "complex-task",
            "title": "Complex Task",
            "required_capabilities": [
                AgentCapability.RESEARCH, 
                AgentCapability.ANALYSIS
            ]
        }
        
        result = supervisor.assign_task(task_data)
        assert result["success"] is True
        
    def test_task_priority_handling(self, supervisor, sample_agent_data):
        """Test that task priority is preserved during assignment."""
        supervisor.register_agent(sample_agent_data)
        
        task_data = {
            "task_id": "priority-task",
            "title": "High Priority Task",
            "priority": "high",
            "required_capabilities": [AgentCapability.RESEARCH]
        }
        
        supervisor.assign_task(task_data)
        
        # Task should be assigned to agent
        agent = supervisor.agent_registry["test-agent-1"]
        assert agent.status == AgentStatus.BUSY
        assert agent.current_task_id == "priority-task"
