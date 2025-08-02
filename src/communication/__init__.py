"""
Communication Components
=======================

This package contains components for peer-to-peer communication,
hierarchical workflows, and agent integration.
"""

from .p2p_communication import P2PCommunicationNode
from .agent_integration import AgentIntegrationService
from .hierarchical_workflow import HierarchicalWorkflowManager

__all__ = [
    "P2PCommunicationNode", "AgentIntegrationService", 
    "HierarchicalWorkflowManager"
]
