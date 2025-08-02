"""
Peer-to-Peer Communication System for AgentWeaver

This module implements direct agent-to-agent communication patterns,
enabling collaborative workflows and hierarchical agent structures.
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid
import logging

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of inter-agent messages."""
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    DELEGATION = "delegation"
    REPORT = "report"
    COLLABORATION = "collaboration"
    ERROR = "error"
    STATUS_UPDATE = "status_update"


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class AgentMessage(BaseModel):
    """
    Structured message for inter-agent communication.
    
    This model defines the standard format for messages exchanged
    between agents in peer-to-peer and hierarchical workflows.
    """
    
    # Message identification
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: Optional[str] = None  # For tracking related messages
    
    # Routing information
    sender_id: str
    recipient_id: str  # Can be specific agent or "broadcast"
    reply_to: Optional[str] = None  # For response messages
    
    # Message metadata
    message_type: MessageType
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    # Message content
    subject: str
    content: Dict[str, Any] = Field(default_factory=dict)
    attachments: Dict[str, Any] = Field(default_factory=dict)
    
    # Processing metadata
    requires_response: bool = False
    expected_response_time: Optional[float] = None  # seconds
    processed: bool = False
    response_sent: bool = False
    
    class Config:
        extra = "forbid"
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def create_response(self, sender_id: str, content: Dict[str, Any], 
                       subject: Optional[str] = None) -> 'AgentMessage':
        """
        Create a response message to this message.
        
        Args:
            sender_id: ID of the responding agent
            content: Response content
            subject: Optional custom subject
            
        Returns:
            New AgentMessage as a response
        """
        return AgentMessage(
            sender_id=sender_id,
            recipient_id=self.sender_id,
            reply_to=self.message_id,
            conversation_id=self.conversation_id or self.message_id,
            message_type=MessageType.RESPONSE,
            subject=subject or f"Re: {self.subject}",
            content=content,
            priority=self.priority
        )


class MessageQueue(BaseModel):
    """
    Message queue for an agent.
    
    Manages incoming and outgoing messages for peer-to-peer communication.
    """
    
    agent_id: str
    inbox: List[AgentMessage] = Field(default_factory=list)
    outbox: List[AgentMessage] = Field(default_factory=list)
    processed_messages: List[str] = Field(default_factory=list)  # Message IDs
    
    def add_incoming_message(self, message: AgentMessage):
        """Add a message to the inbox."""
        if message.message_id not in self.processed_messages:
            self.inbox.append(message)
            logger.info(f"Agent {self.agent_id} received message from {message.sender_id}: {message.subject}")
    
    def add_outgoing_message(self, message: AgentMessage):
        """Add a message to the outbox."""
        self.outbox.append(message)
        logger.info(f"Agent {self.agent_id} sending message to {message.recipient_id}: {message.subject}")
    
    def get_unprocessed_messages(self, message_type: Optional[MessageType] = None) -> List[AgentMessage]:
        """Get unprocessed messages, optionally filtered by type."""
        messages = [msg for msg in self.inbox if not msg.processed]
        
        if message_type:
            messages = [msg for msg in messages if msg.message_type == message_type]
        
        # Sort by priority and timestamp
        priority_order = {
            MessagePriority.URGENT: 0,
            MessagePriority.HIGH: 1,
            MessagePriority.NORMAL: 2,
            MessagePriority.LOW: 3
        }
        
        messages.sort(key=lambda m: (priority_order[m.priority], m.timestamp))
        return messages
    
    def mark_processed(self, message_id: str):
        """Mark a message as processed."""
        for message in self.inbox:
            if message.message_id == message_id:
                message.processed = True
                self.processed_messages.append(message_id)
                break


class P2PCommunicationManager:
    """
    Manages peer-to-peer communication between agents.
    
    This class handles message routing, delivery, and coordination
    for direct agent-to-agent communication patterns.
    """
    
    def __init__(self):
        """Initialize the P2P communication manager."""
        self.agent_queues: Dict[str, MessageQueue] = {}
        self.message_history: List[AgentMessage] = []
        self.conversation_threads: Dict[str, List[str]] = {}  # conversation_id -> message_ids
        
        logger.info("P2P Communication Manager initialized")
    
    def register_agent(self, agent_id: str):
        """Register an agent for P2P communication."""
        if agent_id not in self.agent_queues:
            self.agent_queues[agent_id] = MessageQueue(agent_id=agent_id)
            logger.info(f"Agent {agent_id} registered for P2P communication")
    
    def send_message(self, message: AgentMessage) -> bool:
        """
        Send a message from one agent to another.
        
        Args:
            message: The message to send
            
        Returns:
            True if message was delivered, False otherwise
        """
        try:
            # Ensure sender is registered
            self.register_agent(message.sender_id)
            
            # Handle broadcast messages
            if message.recipient_id == "broadcast":
                return self._broadcast_message(message)
            
            # Ensure recipient is registered
            self.register_agent(message.recipient_id)
            
            # Add to sender's outbox
            sender_queue = self.agent_queues[message.sender_id]
            sender_queue.add_outgoing_message(message)
            
            # Add to recipient's inbox
            recipient_queue = self.agent_queues[message.recipient_id]
            recipient_queue.add_incoming_message(message)
            
            # Track message history
            self.message_history.append(message)
            
            # Track conversation thread
            conversation_id = message.conversation_id or message.message_id
            if conversation_id not in self.conversation_threads:
                self.conversation_threads[conversation_id] = []
            self.conversation_threads[conversation_id].append(message.message_id)
            
            logger.info(f"Message delivered: {message.sender_id} -> {message.recipient_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            return False
    
    def _broadcast_message(self, message: AgentMessage) -> bool:
        """Send a message to all registered agents."""
        success_count = 0
        
        for agent_id in self.agent_queues.keys():
            if agent_id != message.sender_id:  # Don't send to sender
                # Create individual message for each recipient
                individual_message = AgentMessage(
                    sender_id=message.sender_id,
                    recipient_id=agent_id,
                    message_type=message.message_type,
                    priority=message.priority,
                    subject=message.subject,
                    content=message.content,
                    conversation_id=message.conversation_id
                )
                
                if self.send_message(individual_message):
                    success_count += 1
        
        logger.info(f"Broadcast message sent to {success_count} agents")
        return success_count > 0
    
    def get_messages_for_agent(self, agent_id: str, 
                              message_type: Optional[MessageType] = None) -> List[AgentMessage]:
        """Get unprocessed messages for an agent."""
        if agent_id not in self.agent_queues:
            self.register_agent(agent_id)
        
        queue = self.agent_queues[agent_id]
        return queue.get_unprocessed_messages(message_type)
    
    def mark_message_processed(self, agent_id: str, message_id: str):
        """Mark a message as processed by an agent."""
        if agent_id in self.agent_queues:
            self.agent_queues[agent_id].mark_processed(message_id)
    
    def get_conversation_history(self, conversation_id: str) -> List[AgentMessage]:
        """Get all messages in a conversation thread."""
        if conversation_id not in self.conversation_threads:
            return []
        
        message_ids = self.conversation_threads[conversation_id]
        messages = [msg for msg in self.message_history if msg.message_id in message_ids]
        messages.sort(key=lambda m: m.timestamp)
        
        return messages
    
    def get_communication_stats(self) -> Dict[str, Any]:
        """Get statistics about P2P communication."""
        total_messages = len(self.message_history)
        active_conversations = len(self.conversation_threads)
        
        # Count messages by type
        message_type_counts = {}
        for msg in self.message_history:
            msg_type = msg.message_type.value
            message_type_counts[msg_type] = message_type_counts.get(msg_type, 0) + 1
        
        # Count messages by agent
        agent_message_counts = {}
        for agent_id, queue in self.agent_queues.items():
            agent_message_counts[agent_id] = {
                'sent': len(queue.outbox),
                'received': len(queue.inbox),
                'processed': len(queue.processed_messages)
            }
        
        return {
            'total_messages': total_messages,
            'active_conversations': active_conversations,
            'registered_agents': len(self.agent_queues),
            'message_types': message_type_counts,
            'agent_stats': agent_message_counts
        }


class CollaborationProtocol:
    """
    Protocol for structured agent collaboration.
    
    Defines standard patterns for agents to work together
    on complex tasks requiring coordination.
    """
    
    @staticmethod
    def create_collaboration_request(sender_id: str, recipient_id: str,
                                   task_description: str, task_data: Dict[str, Any],
                                   collaboration_type: str = "parallel") -> AgentMessage:
        """
        Create a collaboration request message.
        
        Args:
            sender_id: ID of the requesting agent
            recipient_id: ID of the target collaborator
            task_description: Description of the collaboration task
            task_data: Data needed for the task
            collaboration_type: Type of collaboration (parallel, sequential, etc.)
            
        Returns:
            AgentMessage for collaboration request
        """
        return AgentMessage(
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=MessageType.COLLABORATION,
            priority=MessagePriority.HIGH,
            subject=f"Collaboration Request: {task_description}",
            content={
                "collaboration_type": collaboration_type,
                "task_description": task_description,
                "task_data": task_data,
                "collaboration_id": str(uuid.uuid4())
            },
            requires_response=True,
            expected_response_time=30.0
        )
    
    @staticmethod
    def create_delegation_message(supervisor_id: str, subordinate_id: str,
                                task_title: str, task_parameters: Dict[str, Any],
                                deadline: Optional[datetime] = None) -> AgentMessage:
        """
        Create a task delegation message.
        
        Args:
            supervisor_id: ID of the delegating supervisor
            subordinate_id: ID of the subordinate agent
            task_title: Title of the delegated task
            task_parameters: Parameters for the task
            deadline: Optional deadline for completion
            
        Returns:
            AgentMessage for task delegation
        """
        content = {
            "task_title": task_title,
            "task_parameters": task_parameters,
            "delegation_id": str(uuid.uuid4()),
            "delegation_timestamp": datetime.utcnow().isoformat()
        }
        
        if deadline:
            content["deadline"] = deadline.isoformat()
        
        return AgentMessage(
            sender_id=supervisor_id,
            recipient_id=subordinate_id,
            message_type=MessageType.DELEGATION,
            priority=MessagePriority.HIGH,
            subject=f"Task Delegation: {task_title}",
            content=content,
            requires_response=True,
            expected_response_time=60.0
        )
    
    @staticmethod
    def create_status_report(agent_id: str, supervisor_id: str,
                           task_id: str, status: str, 
                           progress_data: Dict[str, Any]) -> AgentMessage:
        """
        Create a status report message.
        
        Args:
            agent_id: ID of the reporting agent
            supervisor_id: ID of the supervisor
            task_id: ID of the task being reported on
            status: Current status (in_progress, completed, blocked, etc.)
            progress_data: Detailed progress information
            
        Returns:
            AgentMessage for status report
        """
        return AgentMessage(
            sender_id=agent_id,
            recipient_id=supervisor_id,
            message_type=MessageType.REPORT,
            priority=MessagePriority.NORMAL,
            subject=f"Status Report: {task_id}",
            content={
                "task_id": task_id,
                "status": status,
                "progress_data": progress_data,
                "report_timestamp": datetime.utcnow().isoformat()
            }
        )


# Global P2P communication manager instance
p2p_manager = P2PCommunicationManager()


def get_p2p_manager() -> P2PCommunicationManager:
    """Get the global P2P communication manager."""
    return p2p_manager


def send_agent_message(message: AgentMessage) -> bool:
    """
    Send a message using the global P2P manager.
    
    Args:
        message: The message to send
        
    Returns:
        True if sent successfully, False otherwise
    """
    return p2p_manager.send_message(message)


def get_agent_messages(agent_id: str, message_type: Optional[MessageType] = None) -> List[AgentMessage]:
    """
    Get unprocessed messages for an agent.
    
    Args:
        agent_id: ID of the agent
        message_type: Optional filter by message type
        
    Returns:
        List of unprocessed messages
    """
    return p2p_manager.get_messages_for_agent(agent_id, message_type)
