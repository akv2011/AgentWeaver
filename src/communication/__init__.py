"""
Communication Components
=======================

This package contains components for peer-to-peer communication,
hierarchical workflows, and agent integration.
"""

from .p2p_communication import P2PCommunicationManager
from .agent_integration import AgentRegistry
from .hierarchical_workflow import HierarchicalWorkflowOrchestrator

__all__ = [
    "P2PCommunicationManager", "AgentRegistry", 
    "HierarchicalWorkflowOrchestrator"
]
