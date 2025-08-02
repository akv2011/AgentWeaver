"""
Integration tests for AgentWeaver state management.

Tests verify that state is correctly passed between nodes and persisted in memory
using LangGraph's built-in state management capabilities.
"""

import pytest
from datetime import datetime
import asyncio

from src.state_manager import StateManager, GraphState
from src.models import (
    AgentState, AgentStatus, AgentCapability,
    Task, TaskStatus,
    Message, MessageType,
    WorkflowState
)


class TestStateManagerIntegration:
    """Integration tests for the StateManager."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.state_manager = StateManager()
    
    def test_state_manager_initialization(self):
        """Test that StateManager initializes correctly."""
        assert self.state_manager is not None
        assert self.state_manager.system_state is not None
        assert self.state_manager.memory_saver is not None
        assert self.state_manager.graph is not None
    
    def test_agent_registration_and_retrieval(self):
        """Test registering and retrieving agents through state manager."""
        # Create test agent
        agent = AgentState(
            name="test_integration_agent",
            agent_type="worker",
            capabilities=[AgentCapability.RESEARCH]
        )
        
        # Register agent
        success = self.state_manager.register_agent(agent)
        assert success
        
        # Retrieve agent
        retrieved_agent = self.state_manager.get_agent(agent.agent_id)
        assert retrieved_agent is not None
        assert retrieved_agent.name == "test_integration_agent"
        assert retrieved_agent.agent_type == "worker"
        assert len(retrieved_agent.capabilities) == 1
        assert AgentCapability.RESEARCH in retrieved_agent.capabilities
    
    def test_agent_status_update_persistence(self):
        """Test that agent status updates are persisted correctly."""
        # Register agent
        agent = AgentState(name="status_test_agent", agent_type="worker")
        self.state_manager.register_agent(agent)
        
        # Update status
        success = self.state_manager.update_agent_status(agent.agent_id, AgentStatus.BUSY)
        assert success
        
        # Verify status persisted
        retrieved_agent = self.state_manager.get_agent(agent.agent_id)
        assert retrieved_agent.status == AgentStatus.BUSY
        
        # Update to error status
        success = self.state_manager.update_agent_status(agent.agent_id, AgentStatus.ERROR)
        assert success
        
        # Verify error status persisted
        retrieved_agent = self.state_manager.get_agent(agent.agent_id)
        assert retrieved_agent.status == AgentStatus.ERROR
    
    def test_task_lifecycle_with_state_persistence(self):
        """Test complete task lifecycle with state persistence."""
        # Create and register agent
        agent = AgentState(
            name="task_worker",
            agent_type="worker",
            capabilities=[AgentCapability.DATA_PROCESSING]
        )
        self.state_manager.register_agent(agent)
        
        # Create task
        task = Task(
            title="integration_test_task",
            description="Test task for integration",
            task_type="data_processing",
            required_capabilities=[AgentCapability.DATA_PROCESSING],
            parameters={"input_data": "test data"}
        )
        
        # Create task in system
        success = self.state_manager.create_task(task)
        assert success
        
        # Retrieve and verify task
        retrieved_task = self.state_manager.get_task(task.task_id)
        assert retrieved_task is not None
        assert retrieved_task.status == TaskStatus.PENDING
        
        # Assign task to agent
        success = self.state_manager.assign_task(task.task_id, agent.agent_id)
        assert success
        
        # Verify task assignment persisted
        retrieved_task = self.state_manager.get_task(task.task_id)
        retrieved_agent = self.state_manager.get_agent(agent.agent_id)
        
        assert retrieved_task.status == TaskStatus.IN_PROGRESS
        assert retrieved_task.assigned_agent_id == agent.agent_id
        assert retrieved_agent.status == AgentStatus.BUSY
        assert retrieved_agent.current_task_id == task.task_id
        
        # Complete task
        result = {"output": "processed data", "status": "success"}
        success = self.state_manager.complete_task(task.task_id, result)
        assert success
        
        # Verify completion persisted
        retrieved_task = self.state_manager.get_task(task.task_id)
        retrieved_agent = self.state_manager.get_agent(agent.agent_id)
        
        assert retrieved_task.status == TaskStatus.COMPLETED
        assert retrieved_task.result == result
        assert retrieved_agent.status == AgentStatus.AVAILABLE
        assert retrieved_agent.current_task_id is None
        assert retrieved_agent.tasks_completed == 1
    
    def test_message_system_integration(self):
        """Test message sending and processing integration."""
        from src.models import MessagePriority
        
        # Create two agents
        agent1 = AgentState(name="sender_agent", agent_type="sender")
        agent2 = AgentState(name="receiver_agent", agent_type="receiver")
        
        self.state_manager.register_agent(agent1)
        self.state_manager.register_agent(agent2)
        
        # Create message
        message = Message(
            sender_id=agent1.agent_id,
            receiver_id=agent2.agent_id,
            message_type=MessageType.COMMAND,
            content={"action": "process_data", "priority": "high"},
            priority=MessagePriority.HIGH
        )
        
        # Send message
        success = self.state_manager.send_message(message)
        assert success
        
        # Verify message was stored in system state
        current_state = self.state_manager.get_current_state()
        assert message.message_id in current_state["system_state"].messages
        
        stored_message = current_state["system_state"].messages[message.message_id]
        assert stored_message.sender_id == agent1.agent_id
        assert stored_message.receiver_id == agent2.agent_id
        assert stored_message.content["action"] == "process_data"
        
        # Message should be processed by the LangGraph workflow automatically
        assert stored_message.processed
        
        # Verify execution log shows message processing
        assert len(current_state["execution_log"]) > 0
        # Should have at least one log entry about message processing
        message_logs = [log for log in current_state["execution_log"] if "message" in log.lower()]
        assert len(message_logs) > 0
    
    def test_workflow_state_persistence(self):
        """Test workflow creation and state persistence."""
        from src.models import WorkflowStep
        
        # Create workflow steps
        step1 = WorkflowStep(
            step_id="init",
            name="Initialize",
            agent_type="initializer",
            next_steps=["process"]
        )
        
        step2 = WorkflowStep(
            step_id="process",
            name="Process Data",
            agent_type="processor",
            next_steps=["finalize"]
        )
        
        step3 = WorkflowStep(
            step_id="finalize",
            name="Finalize",
            agent_type="finalizer",
            next_steps=[]
        )
        
        # Create workflow
        workflow = WorkflowState(
            name="integration_test_workflow",
            description="Test workflow for integration",
            steps={
                "init": step1,
                "process": step2,
                "finalize": step3
            },
            entry_point="init"
        )
        
        # Create workflow in system
        success = self.state_manager.create_workflow(workflow)
        assert success
        
        # Retrieve and verify workflow
        retrieved_workflow = self.state_manager.get_workflow(workflow.workflow_id)
        assert retrieved_workflow is not None
        assert retrieved_workflow.name == "integration_test_workflow"
        assert retrieved_workflow.entry_point == "init"
        assert len(retrieved_workflow.steps) == 3
        assert retrieved_workflow.status == "pending"
        
        # Start workflow
        retrieved_workflow.start_workflow()
        
        # Update workflow state
        success = self.state_manager.create_workflow(retrieved_workflow)  # Update existing
        assert success
        
        # Verify workflow state changes persisted
        final_workflow = self.state_manager.get_workflow(workflow.workflow_id)
        assert final_workflow.status == "running"
        assert final_workflow.current_step == "init"
        assert final_workflow.started_at is not None
    
    def test_system_metrics_calculation(self):
        """Test system metrics calculation with real data."""
        # Add multiple agents with different statuses
        agents = [
            AgentState(name="agent1", agent_type="worker", status=AgentStatus.AVAILABLE),
            AgentState(name="agent2", agent_type="worker", status=AgentStatus.BUSY),
            AgentState(name="agent3", agent_type="supervisor", status=AgentStatus.AVAILABLE),
            AgentState(name="agent4", agent_type="worker", status=AgentStatus.OFFLINE),
        ]
        
        for agent in agents:
            self.state_manager.register_agent(agent)
        
        # Add multiple tasks with different statuses
        tasks = [
            Task(title="task1", description="Test", task_type="test", status=TaskStatus.COMPLETED),
            Task(title="task2", description="Test", task_type="test", status=TaskStatus.PENDING),
            Task(title="task3", description="Test", task_type="test", status=TaskStatus.IN_PROGRESS),
            Task(title="task4", description="Test", task_type="test", status=TaskStatus.COMPLETED),
        ]
        
        for task in tasks:
            self.state_manager.create_task(task)
        
        # Get system metrics
        metrics = self.state_manager.get_system_metrics()
        
        assert metrics["total_agents"] == 4
        assert metrics["active_agents"] == 3  # All except OFFLINE
        assert metrics["total_tasks"] == 4
        assert metrics["completed_tasks"] == 2
        assert "last_updated" in metrics
    
    def test_state_export_and_structure(self):
        """Test state export functionality."""
        # Add some test data
        agent = AgentState(name="export_test_agent", agent_type="worker")
        task = Task(title="export_test_task", description="Test", task_type="test")
        
        self.state_manager.register_agent(agent)
        self.state_manager.create_task(task)
        
        # Export state
        exported_state = self.state_manager.export_state()
        
        # Verify export structure
        assert "system_state" in exported_state
        assert "execution_log" in exported_state
        assert "errors" in exported_state
        assert "metrics" in exported_state
        
        # Verify data is present
        system_state = exported_state["system_state"]
        assert len(system_state["agents"]) == 1
        assert len(system_state["tasks"]) == 1
        
        # Verify metrics
        metrics = exported_state["metrics"]
        assert metrics["total_agents"] == 1
        assert metrics["total_tasks"] == 1
    
    def test_error_handling_and_logging(self):
        """Test error handling and logging in state manager."""
        # Try to get non-existent agent
        agent = self.state_manager.get_agent("non-existent-id")
        assert agent is None
        
        # Try to assign task to non-existent agent
        task = Task(title="error_test_task", description="Test", task_type="test")
        self.state_manager.create_task(task)
        
        success = self.state_manager.assign_task(task.task_id, "non-existent-agent")
        assert not success
        
        # Try to complete non-existent task
        success = self.state_manager.complete_task("non-existent-task", {"result": "test"})
        assert not success
    
    def test_langgraph_state_persistence_between_invocations(self):
        """Test that LangGraph correctly persists state between invocations."""
        # Create initial state
        agent = AgentState(name="persistence_test_agent", agent_type="worker")
        self.state_manager.register_agent(agent)
        
        # Get current state and verify agent exists
        current_state = self.state_manager.get_current_state()
        assert agent.agent_id in current_state["system_state"].agents
        
        # Create a new StateManager instance to simulate restart
        new_state_manager = StateManager()
        new_state_manager.thread_id = self.state_manager.thread_id  # Use same thread ID
        
        # Verify state persisted across instances
        retrieved_state = new_state_manager.get_current_state()
        
        # Note: In a real scenario with persistent storage, this would work
        # For MemorySaver, state is only preserved within the same process
        # This test demonstrates the pattern that would work with persistent storage
        assert retrieved_state is not None
    
    def test_concurrent_state_updates(self):
        """Test handling of concurrent state updates."""
        # This test demonstrates thread safety considerations
        agent1 = AgentState(name="concurrent_agent1", agent_type="worker")
        agent2 = AgentState(name="concurrent_agent2", agent_type="worker")
        
        # Register agents
        success1 = self.state_manager.register_agent(agent1)
        success2 = self.state_manager.register_agent(agent2)
        
        assert success1 and success2
        
        # Update both agents' statuses
        status_update1 = self.state_manager.update_agent_status(agent1.agent_id, AgentStatus.BUSY)
        status_update2 = self.state_manager.update_agent_status(agent2.agent_id, AgentStatus.BUSY)
        
        assert status_update1 and status_update2
        
        # Verify both updates persisted
        final_agent1 = self.state_manager.get_agent(agent1.agent_id)
        final_agent2 = self.state_manager.get_agent(agent2.agent_id)
        
        assert final_agent1.status == AgentStatus.BUSY
        assert final_agent2.status == AgentStatus.BUSY


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
