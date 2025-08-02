"""
Unit tests for AgentWeaver data models.

Tests validate correct data model behavior, validation, and serialization.
"""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
import json

from src.models import (
    AgentState, AgentStatus, AgentCapability,
    Task, TaskStatus,
    Message, MessageType,
    WorkflowState, WorkflowStep,
    SystemState
)


class TestAgentCapability:
    """Tests for AgentCapability enum."""
    
    def test_create_capability(self):
        """Test using capability enum values."""
        capability = AgentCapability.RESEARCH
        
        assert capability == "research"
        assert capability.value == "research"
    
    def test_capability_with_parameters(self):
        """Test different capability types."""
        capabilities = [
            AgentCapability.RESEARCH,
            AgentCapability.ANALYSIS,
            AgentCapability.COORDINATION,
            AgentCapability.COMMUNICATION,
            AgentCapability.DATA_PROCESSING,
            AgentCapability.PLANNING,
            AgentCapability.EXECUTION
        ]
        
        assert len(capabilities) == 7
        assert AgentCapability.RESEARCH in capabilities
        assert AgentCapability.DATA_PROCESSING in capabilities
    
    def test_capability_serialization(self):
        """Test capability enum serialization."""
        capability = AgentCapability.DATA_PROCESSING
        
        # Test string representation
        assert str(capability) == "AgentCapability.DATA_PROCESSING"
        assert capability.value == "data_processing"
        
        # Test that it can be used in lists
        capabilities = [AgentCapability.RESEARCH, AgentCapability.ANALYSIS]
        assert len(capabilities) == 2


class TestAgentState:
    """Tests for AgentState model."""
    
    def test_create_agent_minimal(self):
        """Test creating an agent with minimal required fields."""
        agent = AgentState(
            name="test_agent",
            agent_type="worker"
        )
        
        assert agent.name == "test_agent"
        assert agent.agent_type == "worker"
        assert agent.status == AgentStatus.AVAILABLE
        assert agent.agent_id is not None
        assert len(agent.capabilities) == 0
    
    def test_create_agent_full(self):
        """Test creating an agent with all fields."""
        capabilities = [
            AgentCapability.RESEARCH,
            AgentCapability.ANALYSIS
        ]
        
        agent = AgentState(
            name="full_agent",
            agent_type="supervisor",
            status=AgentStatus.BUSY,
            capabilities=capabilities,
            current_task_id="task123",
            max_concurrent_tasks=3,
            timeout_seconds=600
        )
        
        assert agent.name == "full_agent"
        assert agent.agent_type == "supervisor"
        assert agent.status == AgentStatus.BUSY
        assert len(agent.capabilities) == 2
        assert AgentCapability.RESEARCH in agent.capabilities
        assert AgentCapability.ANALYSIS in agent.capabilities
        assert agent.current_task_id == "task123"
        assert agent.max_concurrent_tasks == 3
    
    def test_agent_performance_update(self):
        """Test updating agent performance metrics."""
        agent = AgentState(name="perf_agent", agent_type="worker")
        
        # Test successful task
        agent.update_performance(10.5, True)
        assert agent.tasks_completed == 1
        assert agent.tasks_failed == 0
        assert agent.average_execution_time == 10.5
        
        # Test failed task
        agent.update_performance(5.0, False)
        assert agent.tasks_completed == 1
        assert agent.tasks_failed == 1
        assert agent.average_execution_time == 7.75  # (10.5 + 5.0) / 2
    
    def test_agent_serialization(self):
        """Test agent JSON serialization."""
        agent = AgentState(
            name="serialize_agent",
            agent_type="worker",
            context={"key": "value"}
        )
        
        json_data = agent.model_dump_json()
        parsed = json.loads(json_data)
        
        assert parsed["name"] == "serialize_agent"
        assert parsed["context"]["key"] == "value"
        assert "last_activity" in parsed


class TestMessage:
    """Tests for Message model."""
    
    def test_create_message(self):
        """Test creating a basic message."""
        message = Message(
            sender_id="agent1",
            receiver_id="agent2",
            message_type=MessageType.COMMAND,
            content={"action": "process", "data": "test"}
        )
        
        assert message.sender_id == "agent1"
        assert message.receiver_id == "agent2"
        assert message.message_type == MessageType.COMMAND
        assert message.content["action"] == "process"
        assert not message.delivered
        assert not message.processed
    
    def test_message_priority_validation(self):
        """Test message priority validation."""
        from src.models import MessagePriority
        
        # Valid priority
        message = Message(
            sender_id="agent1",
            receiver_id="agent2",
            message_type=MessageType.STATUS,
            content={},
            priority=MessagePriority.HIGH
        )
        assert message.priority == MessagePriority.HIGH
        
        # Test different priority levels
        message_low = Message(
            sender_id="agent1",
            receiver_id="agent2",
            message_type=MessageType.STATUS,
            content={},
            priority=MessagePriority.LOW
        )
        assert message_low.priority == MessagePriority.LOW
    
    def test_message_with_expiration(self):
        """Test message with expiration time."""
        expires_at = datetime.utcnow() + timedelta(hours=1)
        message = Message(
            sender_id="agent1",
            receiver_id="agent2",
            message_type=MessageType.DATA,
            content={"data": "expires"},
            expires_at=expires_at
        )
        
        assert message.expires_at == expires_at


class TestTask:
    """Tests for Task model."""
    
    def test_create_task(self):
        """Test creating a basic task."""
        task = Task(
            title="test_task",
            description="A test task",
            task_type="processing",
            required_capabilities=[AgentCapability.DATA_PROCESSING],
            parameters={"input": "test data"}
        )
        
        assert task.title == "test_task"
        assert task.status == TaskStatus.PENDING
        assert AgentCapability.DATA_PROCESSING in task.required_capabilities
        assert task.parameters["input"] == "test data"
    
    def test_task_lifecycle(self):
        """Test task lifecycle methods."""
        task = Task(
            title="lifecycle_task",
            description="Test lifecycle",
            task_type="test"
        )
        
        # Start task
        task.start_task("agent123")
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.assigned_agent_id == "agent123"
        assert task.started_at is not None
        
        # Complete task
        result = {"output": "completed", "score": 95}
        task.complete_task(result)
        assert task.status == TaskStatus.COMPLETED
        assert task.result == result
        assert task.completed_at is not None
    
    def test_task_failure(self):
        """Test task failure handling."""
        task = Task(title="fail_task", description="Test failure", task_type="test")
        
        task.start_task("agent123")
        task.fail_task("Processing error occurred")
        
        assert task.status == TaskStatus.FAILED
        assert task.error_message == "Processing error occurred"
        assert task.completed_at is not None
    
    def test_task_dependencies(self):
        """Test task dependency handling."""
        task = Task(
            title="dependent_task",
            description="Has dependencies",
            task_type="processing",
            depends_on=["task1", "task2"],
            blocks=["task3"]
        )
        
        assert "task1" in task.depends_on
        assert "task2" in task.depends_on
        assert "task3" in task.blocks


class TestWorkflowState:
    """Tests for WorkflowState model."""
    
    def test_create_workflow(self):
        """Test creating a basic workflow."""
        step1 = WorkflowStep(
            step_id="step1",
            name="Initial Step",
            agent_type="processor",
            next_steps=["step2"]
        )
        
        workflow = WorkflowState(
            name="test_workflow",
            description="A test workflow",
            steps={"step1": step1},
            entry_point="step1"
        )
        
        assert workflow.name == "test_workflow"
        assert workflow.entry_point == "step1"
        assert "step1" in workflow.steps
        assert workflow.status == "pending"
    
    def test_workflow_lifecycle(self):
        """Test workflow execution lifecycle."""
        workflow = WorkflowState(
            name="lifecycle_workflow",
            description="Test lifecycle",
            entry_point="start"
        )
        
        # Start workflow
        workflow.start_workflow()
        assert workflow.status == "running"
        assert workflow.started_at is not None
        assert workflow.current_step == "start"
        
        # Complete step
        result = {"step_output": "success"}
        workflow.complete_step("start", result)
        assert "start" in workflow.completed_steps
        assert len(workflow.execution_history) == 1
        assert workflow.execution_history[0]["status"] == "completed"
    
    def test_workflow_step_failure(self):
        """Test workflow step failure handling."""
        workflow = WorkflowState(
            name="failure_workflow",
            description="Test failure",
            entry_point="start"
        )
        
        workflow.start_workflow()
        workflow.fail_step("start", "Step failed due to error")
        
        assert "start" in workflow.failed_steps
        assert len(workflow.execution_history) == 1
        assert workflow.execution_history[0]["status"] == "failed"
        assert "error" in workflow.execution_history[0]


class TestSystemState:
    """Tests for SystemState model."""
    
    def test_create_system_state(self):
        """Test creating system state."""
        system = SystemState()
        
        assert len(system.agents) == 0
        assert len(system.workflows) == 0
        assert len(system.tasks) == 0
        assert system.system_id is not None
    
    def test_system_metrics_update(self):
        """Test system metrics calculation."""
        system = SystemState()
        
        # Add some agents
        agent1 = AgentState(name="agent1", agent_type="worker", status=AgentStatus.AVAILABLE)
        agent2 = AgentState(name="agent2", agent_type="worker", status=AgentStatus.BUSY)
        agent3 = AgentState(name="agent3", agent_type="worker", status=AgentStatus.OFFLINE)
        
        system.agents[agent1.agent_id] = agent1
        system.agents[agent2.agent_id] = agent2
        system.agents[agent3.agent_id] = agent3
        
        # Add some tasks
        task1 = Task(title="task1", description="Test", task_type="test", status=TaskStatus.COMPLETED)
        task2 = Task(title="task2", description="Test", task_type="test", status=TaskStatus.PENDING)
        
        system.tasks[task1.task_id] = task1
        system.tasks[task2.task_id] = task2
        
        # Update metrics
        system.update_metrics()
        
        assert system.total_agents == 3
        assert system.active_agents == 2  # AVAILABLE and BUSY, not OFFLINE
        assert system.total_tasks == 2
        assert system.completed_tasks == 1
    
    def test_system_state_serialization(self):
        """Test system state JSON serialization."""
        system = SystemState()
        
        # Add an agent
        agent = AgentState(name="test_agent", agent_type="worker")
        system.agents[agent.agent_id] = agent
        
        # Add a task
        task = Task(title="test_task", description="Test", task_type="test")
        system.tasks[task.task_id] = task
        
        # Serialize to JSON
        json_data = system.model_dump_json()
        parsed = json.loads(json_data)
        
        assert "agents" in parsed
        assert "tasks" in parsed
        assert "system_id" in parsed
        assert len(parsed["agents"]) == 1
        assert len(parsed["tasks"]) == 1


if __name__ == "__main__":
    pytest.main([__file__])
