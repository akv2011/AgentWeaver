"""
Integration tests for the Supervisor Node with LangGraph.

Tests the supervisor's LangGraph integration and end-to-end workflows.
"""

import pytest
import tempfile
import uuid
from pathlib import Path

from src.supervisor import SupervisorNode
from src.models import AgentCapability, AgentStatus, TaskStatus
from langgraph.checkpoint.memory import MemorySaver


class TestSupervisorIntegration:
    """Integration test suite for SupervisorNode with LangGraph."""
    
    @pytest.fixture
    def supervisor_with_checkpointer(self):
        """Create supervisor with persistent checkpointer."""
        checkpointer = MemorySaver()
        return SupervisorNode(checkpointer=checkpointer)
        
    @pytest.fixture
    def sample_agents(self):
        """Sample agent data for integration testing."""
        return [
            {
                "agent_id": "research-agent",
                "name": "Research Specialist",
                "capabilities": [AgentCapability.RESEARCH, AgentCapability.ANALYSIS]
            },
            {
                "agent_id": "coord-agent", 
                "name": "Coordination Specialist",
                "capabilities": [AgentCapability.COORDINATION, AgentCapability.COMMUNICATION]
            },
            {
                "agent_id": "general-agent",
                "name": "General Agent",
                "capabilities": [
                    AgentCapability.RESEARCH, 
                    AgentCapability.ANALYSIS,
                    AgentCapability.COORDINATION,
                    AgentCapability.COMMUNICATION
                ]
            }
        ]
        
    def test_supervisor_langgraph_initialization(self, supervisor_with_checkpointer):
        """Test that supervisor properly initializes LangGraph components."""
        supervisor = supervisor_with_checkpointer
        
        # Verify graph is compiled and ready
        assert supervisor.supervisor_graph is not None
        assert supervisor.checkpointer is not None
        
        # Test that we can invoke the graph with empty state
        result = supervisor.supervisor_graph.invoke(
            {"message": None},
            {"configurable": {"thread_id": "test-init"}}
        )
        
        # Should return state without errors
        assert isinstance(result, dict)
        
    def test_full_agent_lifecycle(self, supervisor_with_checkpointer, sample_agents):
        """Test complete agent lifecycle: register, assign task, complete, unregister."""
        supervisor = supervisor_with_checkpointer
        thread_id = "lifecycle-test"
        
        # 1. Register agent
        agent_data = sample_agents[0]
        reg_result = supervisor.register_agent(agent_data, thread_id)
        
        assert reg_result["success"] is True
        assert reg_result["agent_id"] == "research-agent"
        assert len(supervisor.agent_registry) == 1
        
        # 2. Assign task
        task_data = {
            "task_id": "lifecycle-task",
            "title": "Test Task",
            "description": "Integration test task",
            "required_capabilities": [AgentCapability.RESEARCH],
            "priority": "medium"
        }
        assign_result = supervisor.assign_task(task_data, thread_id)
        
        assert assign_result["success"] is True
        assert assign_result["task_id"] == "lifecycle-task"
        assert assign_result["agent_id"] == "research-agent"
        
        # Verify agent status
        agent = supervisor.agent_registry["research-agent"]
        assert agent.status == AgentStatus.BUSY
        assert agent.current_task_id == "lifecycle-task"
        
        # 3. Complete task
        complete_result = supervisor.mark_task_complete("lifecycle-task", "research-agent")
        assert complete_result is True
        
        # Verify agent is available again
        assert agent.status == AgentStatus.AVAILABLE
        assert agent.current_task_id is None
        
        # 4. Unregister agent
        unreg_result = supervisor.unregister_agent("research-agent", thread_id)
        
        assert unreg_result["success"] is True
        assert len(supervisor.agent_registry) == 0
        
    def test_multi_agent_task_assignment(self, supervisor_with_checkpointer, sample_agents):
        """Test task assignment across multiple agents with different capabilities."""
        supervisor = supervisor_with_checkpointer
        thread_id = "multi-agent-test"
        
        # Register multiple agents
        for agent_data in sample_agents:
            result = supervisor.register_agent(agent_data, thread_id)
            assert result["success"] is True
            
        assert len(supervisor.agent_registry) == 3
        
        # Create tasks requiring different capabilities
        tasks = [
            {
                "task_id": "research-task",
                "title": "Research Task",
                "required_capabilities": [AgentCapability.RESEARCH],
                "priority": "high"
            },
            {
                "task_id": "coordination-task",
                "title": "Coordination Task", 
                "required_capabilities": [AgentCapability.COORDINATION],
                "priority": "medium"
            },
            {
                "task_id": "complex-task",
                "title": "Complex Task",
                "required_capabilities": [
                    AgentCapability.RESEARCH,
                    AgentCapability.COORDINATION
                ],
                "priority": "low"
            }
        ]
        
        assignment_results = []
        for task in tasks:
            result = supervisor.assign_task(task, thread_id)
            assignment_results.append(result)
            
        # All tasks should be assigned (all agents have required capabilities)
        for result in assignment_results:
            assert result["success"] is True
            
        # Verify all agents are busy
        busy_agents = [a for a in supervisor.agent_registry.values() 
                      if a.status == AgentStatus.BUSY]
        assert len(busy_agents) == 3
        
    def test_task_queuing_and_reassignment(self, supervisor_with_checkpointer):
        """Test task queuing when no suitable agents are available."""
        supervisor = supervisor_with_checkpointer
        thread_id = "queue-test"
        
        # Register one agent
        agent_data = {
            "agent_id": "single-agent",
            "name": "Single Agent",
            "capabilities": [AgentCapability.RESEARCH]
        }
        supervisor.register_agent(agent_data, thread_id)
        
        # Assign first task (should succeed)
        task1 = {
            "task_id": "task-1",
            "title": "First Task",
            "required_capabilities": [AgentCapability.RESEARCH]
        }
        result1 = supervisor.assign_task(task1, thread_id)
        assert result1["success"] is True
        
        # Assign second task (should be queued)
        task2 = {
            "task_id": "task-2",
            "title": "Second Task", 
            "required_capabilities": [AgentCapability.RESEARCH]
        }
        result2 = supervisor.assign_task(task2, thread_id)
        assert result2["success"] is False
        assert "queued" in result2["message"]
        assert len(supervisor.task_queue) == 1
        
        # Complete first task
        supervisor.mark_task_complete("task-1", "single-agent")
        
        # Second task should now be automatically assigned
        assert len(supervisor.task_queue) == 0
        agent = supervisor.agent_registry["single-agent"]
        assert agent.status == AgentStatus.BUSY
        assert agent.current_task_id == "task-2"
        
    def test_health_monitoring_with_state_persistence(self, supervisor_with_checkpointer, sample_agents):
        """Test health monitoring with LangGraph state persistence."""
        supervisor = supervisor_with_checkpointer
        thread_id = "health-test"
        
        # Register agents and assign some tasks
        for i, agent_data in enumerate(sample_agents[:2]):
            supervisor.register_agent(agent_data, thread_id)
            
            if i == 0:  # Assign task to first agent
                task_data = {
                    "task_id": f"health-task-{i}",
                    "title": f"Health Test Task {i}",
                    "required_capabilities": agent_data["capabilities"][:1]
                }
                supervisor.assign_task(task_data, thread_id)
                
        # Get health report
        health_report = supervisor.get_health_report(thread_id)
        
        assert "error" not in health_report
        assert health_report["total_agents"] == 2
        assert health_report["available_agents"] == 1
        assert health_report["busy_agents"] == 1
        assert health_report["queued_tasks"] == 0
        
        # Verify agent details
        agent_details = health_report["agent_details"]
        assert len(agent_details) == 2
        
        busy_agent = next(a for a in agent_details if a["status"] == "busy")
        available_agent = next(a for a in agent_details if a["status"] == "available")
        
        assert busy_agent["current_task"] is not None
        assert available_agent["current_task"] is None
        
    def test_concurrent_operations_with_different_threads(self, supervisor_with_checkpointer):
        """Test concurrent operations using different thread IDs."""
        supervisor = supervisor_with_checkpointer
        
        # Operations on thread 1
        thread1_agent = {
            "agent_id": "thread1-agent",
            "name": "Thread 1 Agent", 
            "capabilities": [AgentCapability.RESEARCH]
        }
        result1 = supervisor.register_agent(thread1_agent, "thread-1")
        assert result1["success"] is True
        
        # Operations on thread 2
        thread2_agent = {
            "agent_id": "thread2-agent",
            "name": "Thread 2 Agent",
            "capabilities": [AgentCapability.COORDINATION]
        }
        result2 = supervisor.register_agent(thread2_agent, "thread-2")
        assert result2["success"] is True
        
        # Both agents should be registered
        assert len(supervisor.agent_registry) == 2
        assert "thread1-agent" in supervisor.agent_registry
        assert "thread2-agent" in supervisor.agent_registry
        
        # Get health reports from different threads
        health1 = supervisor.get_health_report("thread-1")
        health2 = supervisor.get_health_report("thread-2")
        
        # Both should see the same system state
        assert health1["total_agents"] == health2["total_agents"] == 2
        assert health1["available_agents"] == health2["available_agents"] == 2
        
    def test_error_handling_in_langgraph_workflow(self, supervisor_with_checkpointer):
        """Test error handling within LangGraph workflow."""
        supervisor = supervisor_with_checkpointer
        thread_id = "error-test"
        
        # Test registration with malformed data
        result = supervisor.register_agent(None, thread_id)
        
        # Should handle gracefully 
        assert isinstance(result, dict)
        # The specific error handling depends on implementation
        
        # Test unregistering non-existent agent
        unreg_result = supervisor.unregister_agent("non-existent", thread_id)
        assert unreg_result["success"] is False
        assert "not found" in unreg_result["error"]
        
    def test_state_graph_execution_order(self, supervisor_with_checkpointer):
        """Test that LangGraph nodes execute in correct order."""
        supervisor = supervisor_with_checkpointer
        thread_id = "execution-order-test"
        
        # Register agent
        agent_data = {
            "agent_id": "order-test-agent",
            "name": "Order Test Agent",
            "capabilities": [AgentCapability.RESEARCH]
        }
        
        # Use the LangGraph interface directly
        initial_state = {
            "message": {
                "type": "register_agent",
                "content": agent_data
            }
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        result = supervisor.supervisor_graph.invoke(initial_state, config)
        
        # Verify the workflow executed properly
        assert "registration_result" in result
        assert result["registration_result"]["success"] is True
        assert len(supervisor.agent_registry) == 1
        
    def test_supervisor_message_routing(self, supervisor_with_checkpointer):
        """Test that supervisor correctly routes different message types."""
        supervisor = supervisor_with_checkpointer
        thread_id = "routing-test"
        
        # Test each message type through the supervisor
        test_cases = [
            {
                "message_type": "register_agent",
                "content": {
                    "agent_id": "routing-agent",
                    "name": "Routing Test Agent",
                    "capabilities": [AgentCapability.ANALYSIS]
                },
                "expected_key": "registration_result"
            },
            {
                "message_type": "health_check",
                "content": {},
                "expected_key": "health_report"
            }
        ]
        
        for test_case in test_cases:
            initial_state = {
                "message": {
                    "type": test_case["message_type"],
                    "content": test_case["content"]
                }
            }
            
            config = {"configurable": {"thread_id": thread_id}}
            result = supervisor.supervisor_graph.invoke(initial_state, config)
            
            assert test_case["expected_key"] in result
            
    def test_performance_tracking_integration(self, supervisor_with_checkpointer):
        """Test that agent performance is tracked through task completion."""
        supervisor = supervisor_with_checkpointer
        thread_id = "performance-test"
        
        # Register agent
        agent_data = {
            "agent_id": "perf-agent",
            "name": "Performance Agent",
            "capabilities": [AgentCapability.RESEARCH]
        }
        supervisor.register_agent(agent_data, thread_id)
        
        # Get initial performance
        agent = supervisor.agent_registry["perf-agent"]
        initial_completed = agent.tasks_completed
        initial_success_rate = agent.success_rate
        
        # Assign and complete a task
        task_data = {
            "task_id": "perf-task",
            "title": "Performance Task",
            "required_capabilities": [AgentCapability.RESEARCH]
        }
        supervisor.assign_task(task_data, thread_id)
        supervisor.mark_task_complete("perf-task", "perf-agent")
        
        # Verify performance was updated
        assert agent.tasks_completed > initial_completed
        # Success rate should be updated (may be same if already 1.0)
        assert agent.success_rate >= initial_success_rate
