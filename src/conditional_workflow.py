"""
Advanced Conditional Workflow Implementation for AgentWeaver.

This module implements conditional routing and failure handling capabilities,
enabling dynamic workflow paths based on content analysis and automatic
rerouting on agent failures.
"""

from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime
import uuid
import logging
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .core.models import Task, TaskStatus, AgentCapability
from .agents import TextAnalysisAgent, APIInteractionAgent, DataProcessingAgent
from .core.redis_config import get_redis_saver, redis_manager

logger = logging.getLogger(__name__)


class ConditionalWorkflowState(BaseModel):
    """
    Enhanced state schema for conditional workflows with routing support.
    
    This extends the basic workflow state to support conditional routing,
    agent failure detection, and dynamic path selection.
    """
    
    # Workflow identification
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_name: str = "Advanced Conditional Workflow"
    
    # Input data
    initial_input: Dict[str, Any] = Field(default_factory=dict)
    
    # Step tracking
    current_step: str = "start"
    completed_steps: List[str] = Field(default_factory=list)
    step_results: Dict[str, Any] = Field(default_factory=dict)
    
    # Agent data flow
    analysis_result: Optional[Dict[str, Any]] = None  # Results from content analysis
    route_data: Dict[str, Any] = Field(default_factory=dict)  # Data specific to routing paths
    final_result: Optional[Dict[str, Any]] = None
    
    # Conditional routing fields
    sentiment_score: Optional[float] = None  # For sentiment-based routing
    content_type: Optional[str] = None  # For content-type-based routing
    analysis_confidence: Optional[float] = None  # For confidence-based routing
    routing_decision: Optional[str] = None  # The chosen routing path
    
    # Error handling and failure detection
    error_occurred: bool = False
    error_message: Optional[str] = None
    error_step: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    
    # Agent failure management
    failed_agent_id: Optional[str] = None
    required_capability: Optional[str] = None
    backup_agent_used: bool = False
    reroute_count: int = 0
    max_reroutes: int = 3
    
    # Execution tracking
    routing_history: List[Dict[str, Any]] = Field(default_factory=list)
    agent_execution_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    workflow_start_time: datetime = Field(default_factory=datetime.utcnow)
    workflow_end_time: Optional[datetime] = None
    total_execution_time: Optional[float] = None
    
    # Status tracking
    status: str = "running"  # running, completed, failed, rerouted
    
    class Config:
        extra = "forbid"
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConditionalRouter:
    """
    Conditional router for dynamic workflow path selection.
    
    This class contains the logic for analyzing workflow state and determining
    the next node to execute based on content analysis results.
    """
    
    def __init__(self):
        """Initialize the conditional router."""
        self.routing_rules = {
            'sentiment_based': self._route_by_sentiment,
            'content_type_based': self._route_by_content_type,
            'confidence_based': self._route_by_confidence,
            'error_based': self._route_by_error_status
        }
        
        logger.info("Conditional router initialized with routing rules")
    
    def route(self, state: Dict[str, Any], routing_type: str = 'sentiment_based') -> str:
        """
        Determine the next node based on state analysis.
        
        Args:
            state: Current workflow state
            routing_type: Type of routing logic to apply
            
        Returns:
            String identifier for the next node to execute
        """
        try:
            # Log routing attempt
            logger.info(f"Routing decision requested: type={routing_type}")
            
            # Check for error condition first
            if state.get("error_occurred"):
                return self._route_by_error_status(state)
            
            # Apply the requested routing logic
            routing_func = self.routing_rules.get(routing_type, self._route_by_sentiment)
            decision = routing_func(state)
            
            # Update routing history
            routing_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "routing_type": routing_type,
                "decision": decision,
                "state_snapshot": {
                    "sentiment_score": state.get("sentiment_score"),
                    "content_type": state.get("content_type"),
                    "analysis_confidence": state.get("analysis_confidence"),
                    "error_occurred": state.get("error_occurred")
                }
            }
            
            if "routing_history" not in state:
                state["routing_history"] = []
            state["routing_history"].append(routing_entry)
            state["routing_decision"] = decision
            
            logger.info(f"Routing decision: {decision} (type: {routing_type})")
            return decision
            
        except Exception as e:
            logger.error(f"Routing failed: {str(e)}")
            # Only set error state if it's not already set (to prevent infinite loops)
            if not state.get("error_occurred"):
                state["error_occurred"] = True
                state["error_message"] = f"Routing failed: {str(e)}"
            return "error_handler"
    
    def _route_by_sentiment(self, state: Dict[str, Any]) -> str:
        """
        Route based on sentiment analysis results.
        
        Args:
            state: Current workflow state
            
        Returns:
            Next node identifier based on sentiment
        """
        sentiment_score = state.get("sentiment_score")
        
        # Handle missing or None sentiment score
        if sentiment_score is None:
            sentiment_score = 0.0
        
        if sentiment_score >= 0.7:
            return "positive_sentiment_processor"
        elif sentiment_score <= -0.3:
            return "negative_sentiment_processor"
        else:
            return "neutral_sentiment_processor"
    
    def _route_by_content_type(self, state: Dict[str, Any]) -> str:
        """
        Route based on content type analysis.
        
        Args:
            state: Current workflow state
            
        Returns:
            Next node identifier based on content type
        """
        content_type = state.get("content_type", "unknown")
        
        if content_type == "technical":
            return "technical_analysis_agent"
        elif content_type == "marketing":
            return "marketing_analysis_agent"
        elif content_type == "customer_feedback":
            return "feedback_analysis_agent"
        else:
            return "general_analysis_agent"
    
    def _route_by_confidence(self, state: Dict[str, Any]) -> str:
        """
        Route based on analysis confidence levels.
        
        Args:
            state: Current workflow state
            
        Returns:
            Next node identifier based on confidence
        """
        confidence = state.get("analysis_confidence")
        
        # Handle missing or None confidence
        if confidence is None:
            confidence = 0.0
        
        if confidence >= 0.9:
            return "high_confidence_processor"
        elif confidence >= 0.6:
            return "medium_confidence_processor"
        else:
            return "manual_review_processor"
    
    def _route_by_error_status(self, state: Dict[str, Any]) -> str:
        """
        Route based on error conditions and failure recovery.
        
        Args:
            state: Current workflow state
            
        Returns:
            Next node identifier for error handling
        """
        if state.get("failed_agent_id") and state.get("reroute_count", 0) < state.get("max_reroutes", 3):
            return "agent_failure_recovery"
        else:
            return "error_handler"


class AgentFailureManager:
    """
    Manages agent failure detection and automatic rerouting.
    
    This class handles the logic for detecting agent failures,
    finding backup agents, and rerouting tasks automatically.
    """
    
    def __init__(self, agent_registry: Dict[str, Any]):
        """
        Initialize the failure manager.
        
        Args:
            agent_registry: Registry of available agents by capability
        """
        self.agent_registry = agent_registry
        self.failure_history = []
        
        logger.info("Agent failure manager initialized")
    
    def detect_failure(self, state: Dict[str, Any], agent_id: str, 
                      exception: Exception) -> Dict[str, Any]:
        """
        Detect and record agent failure.
        
        Args:
            state: Current workflow state
            agent_id: ID of the failed agent
            exception: The exception that caused the failure
            
        Returns:
            Updated state with failure information
        """
        failure_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "error_type": type(exception).__name__,
            "error_message": str(exception),
            "step": state.get("current_step")
        }
        
        self.failure_history.append(failure_entry)
        
        # Update state with failure information
        state["error_occurred"] = True
        state["failed_agent_id"] = agent_id
        state["error_message"] = f"Agent {agent_id} failed: {str(exception)}"
        state["error_details"] = failure_entry
        
        # Determine required capability for rerouting
        state["required_capability"] = self._determine_required_capability(agent_id)
        
        logger.error(f"Agent failure detected: {agent_id} - {str(exception)}")
        return state
    
    def find_backup_agent(self, state: Dict[str, Any]) -> Optional[str]:
        """
        Find a backup agent with the required capability.
        
        Args:
            state: Current workflow state
            
        Returns:
            ID of backup agent or None if none available
        """
        required_capability = state.get("required_capability")
        failed_agent_id = state.get("failed_agent_id")
        
        if not required_capability:
            return None
        
        # Find agents with the required capability
        available_agents = self.agent_registry.get(required_capability, [])
        
        # Filter out the failed agent
        backup_agents = [agent for agent in available_agents if agent != failed_agent_id]
        
        if backup_agents:
            backup_agent = backup_agents[0]  # Use first available backup
            logger.info(f"Backup agent found: {backup_agent} for capability {required_capability}")
            return backup_agent
        
        logger.warning(f"No backup agent available for capability {required_capability}")
        return None
    
    def _determine_required_capability(self, agent_id: str) -> Optional[str]:
        """
        Determine the required capability based on the failed agent.
        
        Args:
            agent_id: ID of the failed agent
            
        Returns:
            Required capability string
        """
        # This is a simplified mapping - in practice, you'd query the agent registry
        agent_capability_map = {
            "text_analyzer": "text_analysis",
            "api_client": "api_interaction", 
            "data_processor": "data_processing"
        }
        
        return agent_capability_map.get(agent_id)


class ConditionalWorkflowOrchestrator:
    """
    Orchestrates conditional workflows with dynamic routing and failure handling.
    
    This class manages the execution of workflows that can dynamically choose
    different paths based on content analysis and automatically recover from failures.
    """
    
    def __init__(self, checkpointer=None, use_redis: bool = True):
        """
        Initialize the Conditional Workflow Orchestrator.
        
        Args:
            checkpointer: Optional checkpointer for state persistence
            use_redis: Whether to use Redis for persistent state (default: True)
        """
        # Initialize persistent state management
        if use_redis and checkpointer is None:
            try:
                self.checkpointer = get_redis_saver()
                connection_info = redis_manager.get_connection_info()
                if connection_info['connected']:
                    logger.info("Using Redis for persistent state management")
                else:
                    logger.warning("Redis not connected, using memory fallback")
            except Exception as e:
                logger.error(f"Failed to initialize Redis, using memory fallback: {str(e)}")
                self.checkpointer = MemorySaver()
        else:
            self.checkpointer = checkpointer or MemorySaver()
            if isinstance(self.checkpointer, MemorySaver):
                logger.info("Using in-memory state management")
        self.worker_agents = self._initialize_worker_agents()
        self.agent_registry = self._build_agent_registry()
        self.router = ConditionalRouter()
        self.failure_manager = AgentFailureManager(self.agent_registry)
        self.workflow_graph = None
        self._setup_conditional_workflow_graph()
        
        logger.info("Conditional Workflow Orchestrator initialized")
    
    def _initialize_worker_agents(self) -> Dict[str, Any]:
        """
        Initialize the worker agents for the conditional workflow.
        
        Returns:
            Dictionary of initialized worker agents
        """
        return {
            # Primary agents
            "text_analyzer": TextAnalysisAgent("ConditionalTextAnalyzer"),
            "api_client": APIInteractionAgent("ConditionalAPIClient"),
            "data_processor": DataProcessingAgent("ConditionalDataProcessor"),
            
            # Backup agents for failure recovery
            "backup_text_analyzer": TextAnalysisAgent("BackupTextAnalyzer"),
            "backup_api_client": APIInteractionAgent("BackupAPIClient"),
            "backup_data_processor": DataProcessingAgent("BackupDataProcessor"),
            
            # Specialized routing agents
            "positive_processor": DataProcessingAgent("PositiveSentimentProcessor"),
            "negative_processor": DataProcessingAgent("NegativeSentimentProcessor"),
            "neutral_processor": DataProcessingAgent("NeutralSentimentProcessor")
        }
    
    def _build_agent_registry(self) -> Dict[str, List[str]]:
        """
        Build a registry of agents organized by capability.
        
        Returns:
            Registry mapping capabilities to agent IDs
        """
        return {
            "text_analysis": ["text_analyzer", "backup_text_analyzer"],
            "api_interaction": ["api_client", "backup_api_client"],
            "data_processing": ["data_processor", "backup_data_processor", 
                              "positive_processor", "negative_processor", "neutral_processor"]
        }
    
    def _setup_conditional_workflow_graph(self):
        """Set up the conditional workflow graph with dynamic routing."""
        # Create the graph with ConditionalWorkflowState
        graph = StateGraph(dict)  # Using dict for LangGraph compatibility
        
        # Add workflow nodes
        graph.add_node("supervisor", self._supervisor_node)
        graph.add_node("content_analyzer", self._content_analyzer_node)
        graph.add_node("conditional_router", self._conditional_router_node)
        
        # Sentiment-based processing nodes
        graph.add_node("positive_sentiment_processor", self._positive_sentiment_processor_node)
        graph.add_node("negative_sentiment_processor", self._negative_sentiment_processor_node)
        graph.add_node("neutral_sentiment_processor", self._neutral_sentiment_processor_node)
        
        # Failure recovery nodes
        graph.add_node("agent_failure_recovery", self._agent_failure_recovery_node)
        graph.add_node("error_handler", self._error_handler_node)
        graph.add_node("workflow_finalizer", self._workflow_finalizer_node)
        
        # Define edges
        graph.add_edge(START, "supervisor")
        graph.add_edge("supervisor", "content_analyzer")
        
        # Conditional routing from content analyzer
        def route_from_content_analyzer(state: Dict[str, Any]) -> str:
            """Route from content analyzer to conditional router or error handler."""
            if state.get("error_occurred"):
                return "error_handler"
            return "conditional_router"
        
        graph.add_conditional_edges(
            "content_analyzer",
            route_from_content_analyzer,
            {
                "conditional_router": "conditional_router",
                "error_handler": "error_handler"
            }
        )
        
        # Dynamic routing based on sentiment analysis
        def dynamic_sentiment_router(state: Dict[str, Any]) -> str:
            """Dynamic router for sentiment-based workflow paths."""
            return self.router.route(state, 'sentiment_based')
        
        graph.add_conditional_edges(
            "conditional_router",
            dynamic_sentiment_router,
            {
                "positive_sentiment_processor": "positive_sentiment_processor",
                "negative_sentiment_processor": "negative_sentiment_processor", 
                "neutral_sentiment_processor": "neutral_sentiment_processor",
                "agent_failure_recovery": "agent_failure_recovery",
                "error_handler": "error_handler"
            }
        )
        
        # Route sentiment processors to finalizer or error handler
        def route_to_finalizer(state: Dict[str, Any]) -> str:
            return "error_handler" if state.get("error_occurred") else "workflow_finalizer"
        
        # Route after error handler - to recovery or finalizer
        def route_after_error_handler(state: Dict[str, Any]) -> str:
            """Decide where to route after error handling."""
            failed_agent_id = state.get("failed_agent_id")
            reroute_count = state.get("reroute_count", 0)
            max_reroutes = state.get("max_reroutes", 3)
            
            # Only attempt recovery if we have a failed agent and haven't exceeded max reroutes
            if (failed_agent_id and 
                reroute_count < max_reroutes and 
                not state.get("critical_error", False)):
                return "agent_failure_recovery"
            else:
                return "workflow_finalizer"
        
        for processor in ["positive_sentiment_processor", "negative_sentiment_processor", "neutral_sentiment_processor"]:
            graph.add_conditional_edges(
                processor,
                route_to_finalizer,
                {
                    "workflow_finalizer": "workflow_finalizer",
                    "error_handler": "error_handler"
                }
            )
        
        # Failure recovery routing
        def route_from_recovery(state: Dict[str, Any]) -> str:
            """Route from failure recovery back to retry with backup agent or handle final failure."""
            if state.get("backup_agent_used") and not state.get("error_occurred"):
                # Backup agent assigned successfully, retry the failed operation
                failed_step = state.get("error_step")
                if failed_step == "content_analyzer":
                    return "content_analyzer"  # Retry content analysis with backup
                elif failed_step in ["positive_sentiment_processor", "negative_sentiment_processor", "neutral_sentiment_processor"]:
                    return "conditional_router"  # Retry routing to sentiment processor
                else:
                    return "conditional_router"  # Default retry point
            else:
                return "error_handler"  # No backup available or recovery failed
        
        graph.add_conditional_edges(
            "agent_failure_recovery",
            route_from_recovery,
            {
                "content_analyzer": "content_analyzer",
                "conditional_router": "conditional_router",
                "error_handler": "error_handler"
            }
        )
        
        # End points
        graph.add_edge("error_handler", "workflow_finalizer")
        graph.add_edge("agent_failure_recovery", "workflow_finalizer")
        graph.add_edge("workflow_finalizer", END)
        
        # Compile the graph
        self.workflow_graph = graph.compile(checkpointer=self.checkpointer)
        
        logger.info("Conditional workflow graph compiled successfully")
    
    def _supervisor_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Supervisor node for conditional workflow initialization.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with initialization
        """
        try:
            logger.info("Supervisor: Initializing conditional workflow")
            
            # Initialize workflow tracking
            state["current_step"] = "supervisor"
            state["completed_steps"] = []
            state["step_results"] = {}
            state["workflow_start_time"] = datetime.utcnow().isoformat()
            state["status"] = "running"
            state["error_occurred"] = False
            state["routing_history"] = []
            state["agent_execution_history"] = []
            state["reroute_count"] = 0
            
            # Validate input
            if not state.get("initial_input"):
                raise ValueError("No initial input provided for conditional workflow")
            
            # Add supervisor completion
            state["completed_steps"].append("supervisor")
            state["step_results"]["supervisor"] = {
                "action": "conditional_workflow_initialization",
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info("Supervisor: Conditional workflow initialized successfully")
            
        except Exception as e:
            logger.error(f"Supervisor: Initialization failed - {str(e)}")
            state["error_occurred"] = True
            state["error_message"] = f"Supervisor initialization failed: {str(e)}"
            state["error_step"] = "supervisor"
            state["status"] = "failed"
            if "workflow_start_time" not in state:
                state["workflow_start_time"] = datetime.utcnow().isoformat()
        
        return state
    
    def _content_analyzer_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Content analyzer node that performs sentiment and content analysis.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with analysis results for routing
        """
        try:
            is_retry = state.get("backup_agent_used", False) and state.get("error_step") == "content_analyzer"
            agent_type = "backup" if is_retry else "primary"
            
            logger.info(f"Content Analyzer: Starting {agent_type} analysis for routing")
            state["current_step"] = "content_analyzer"
            
            # Get input data
            input_data = state.get("initial_input", {})
            text_content = input_data.get("text", "")
            
            if not text_content:
                raise ValueError("No text content provided for analysis")
            
            # Create task for enhanced text analysis
            task = Task(
                task_id=f"content_analysis_{state.get('workflow_id', 'unknown')}",
                title="Conditional Workflow: Content Analysis",
                task_type="text_analysis",
                parameters={
                    "text": text_content,
                    "analysis_type": "summarize"  # Use supported analysis type
                }
            )
            
            # Execute analysis with the assigned agent (primary or backup)
            text_agent = self.worker_agents["text_analyzer"]
            result = text_agent.execute(task, state)
            
            if result.get("error"):
                raise Exception(result["error"])
            
            # Extract routing information from analysis
            state["analysis_result"] = result
            
            # Extract sentiment for routing (mock implementation - would be extracted from real analysis)
            if "sentiment" in text_content.lower():
                if "positive" in text_content.lower() or "excellent" in text_content.lower():
                    state["sentiment_score"] = 0.8
                elif "negative" in text_content.lower() or "terrible" in text_content.lower():
                    state["sentiment_score"] = -0.6
                else:
                    state["sentiment_score"] = 0.1
            else:
                # Default sentiment analysis based on text characteristics
                if "good" in text_content.lower() or "great" in text_content.lower() or "excellent" in text_content.lower():
                    state["sentiment_score"] = 0.75
                elif "bad" in text_content.lower() or "poor" in text_content.lower() or "terrible" in text_content.lower():
                    state["sentiment_score"] = -0.5
                else:
                    state["sentiment_score"] = 0.0
            
            # Determine content type for routing
            if "technical" in text_content.lower() or "api" in text_content.lower():
                state["content_type"] = "technical"
            elif "customer" in text_content.lower() or "feedback" in text_content.lower():
                state["content_type"] = "customer_feedback"
            elif "marketing" in text_content.lower() or "campaign" in text_content.lower():
                state["content_type"] = "marketing"
            else:
                state["content_type"] = "general"
            
            # Set analysis confidence
            state["analysis_confidence"] = 0.85  # Mock confidence score
            
            # Store results
            state["completed_steps"].append("content_analyzer")
            state["step_results"]["content_analyzer"] = {
                "agent": f"text_analyzer ({agent_type})",
                "result": result,
                "sentiment_score": state["sentiment_score"],
                "content_type": state["content_type"],
                "confidence": state["analysis_confidence"],
                "status": "completed",
                "is_retry": is_retry,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Content Analyzer: {agent_type.title()} analysis completed - sentiment: {state['sentiment_score']}, type: {state['content_type']}")
            
        except Exception as e:
            logger.error(f"Content Analyzer: Analysis failed - {str(e)}")
            # Only detect failure if this isn't already a retry attempt
            if not state.get("backup_agent_used", False):
                state = self.failure_manager.detect_failure(state, "text_analyzer", e)
            else:
                # Backup agent also failed
                state["error_occurred"] = True
                state["error_message"] = f"Backup content analysis failed: {str(e)}"
                state["error_step"] = "content_analyzer"
                state["error_details"] = {"exception_type": type(e).__name__, "backup_failure": True}
                state["status"] = "failed"
        
        return state
    
    def _conditional_router_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conditional router node that determines the next processing path.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with routing decision
        """
        try:
            logger.info("Conditional Router: Determining processing path")
            state["current_step"] = "conditional_router"
            
            # The actual routing decision is made by the graph's conditional edges
            # This node just logs the decision and updates state
            
            routing_info = {
                "sentiment_score": state.get("sentiment_score"),
                "content_type": state.get("content_type"),
                "analysis_confidence": state.get("analysis_confidence"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            state["completed_steps"].append("conditional_router")
            state["step_results"]["conditional_router"] = {
                "action": "routing_decision",
                "routing_info": routing_info,
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info("Conditional Router: Routing decision logged")
            
        except Exception as e:
            logger.error(f"Conditional Router: Routing failed - {str(e)}")
            state["error_occurred"] = True
            state["error_message"] = f"Conditional routing failed: {str(e)}"
            state["error_step"] = "conditional_router"
        
        return state
    
    def _positive_sentiment_processor_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process positive sentiment content."""
        return self._sentiment_processor_node(state, "positive")
    
    def _negative_sentiment_processor_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process negative sentiment content."""
        return self._sentiment_processor_node(state, "negative")
    
    def _neutral_sentiment_processor_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process neutral sentiment content."""
        return self._sentiment_processor_node(state, "neutral")
    
    def _sentiment_processor_node(self, state: Dict[str, Any], sentiment: str) -> Dict[str, Any]:
        """
        Generic sentiment processor node.
        
        Args:
            state: Current workflow state
            sentiment: Type of sentiment being processed
            
        Returns:
            Updated state with sentiment-specific processing results
        """
        try:
            logger.info(f"Sentiment Processor: Processing {sentiment} sentiment content")
            state["current_step"] = f"{sentiment}_sentiment_processor"
            
            # Initialize route_data if not present
            if "route_data" not in state:
                state["route_data"] = {}
            
            # Get analysis data
            analysis_result = state.get("analysis_result", {})
            sentiment_score = state.get("sentiment_score", 0.0)
            
            # Create sentiment-specific task with simulated data
            task = Task(
                task_id=f"{sentiment}_processing_{state.get('workflow_id', 'unknown')}",
                title=f"Conditional Workflow: {sentiment.title()} Sentiment Processing",
                task_type="data_processing",
                parameters={
                    "data": [1, 2, 3, 4, 5],  # Provide sample data for processing
                    "operation": "calculate_statistics"
                }
            )
            
            # Execute sentiment-specific processing
            processor_agent = self.worker_agents[f"{sentiment}_processor"]
            result = processor_agent.execute(task, state)
            
            # Create comprehensive result
            final_result = {
                "workflow_summary": {
                    "content_analysis": analysis_result,
                    "sentiment_classification": {
                        "sentiment": sentiment,
                        "score": sentiment_score,
                        "confidence": state.get("analysis_confidence", 0.0)
                    },
                    "sentiment_processing": result
                },
                "routing_metadata": {
                    "routing_decision": sentiment,
                    "routing_history": state.get("routing_history", []),
                    "agent_execution_history": state.get("agent_execution_history", [])
                },
                "workflow_metadata": {
                    "workflow_id": state.get("workflow_id"),
                    "sentiment_path": sentiment,
                    "processing_timestamp": datetime.utcnow().isoformat()
                }
            }
            
            # Store results
            state["final_result"] = final_result
            state["route_data"][sentiment] = result
            state["completed_steps"].append(f"{sentiment}_sentiment_processor")
            state["step_results"][f"{sentiment}_sentiment_processor"] = {
                "agent": f"{sentiment}_processor",
                "result": result,
                "sentiment": sentiment,
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Sentiment Processor: {sentiment.title()} sentiment processing completed")
            
        except Exception as e:
            logger.error(f"Sentiment Processor: {sentiment} processing failed - {str(e)}")
            state["error_occurred"] = True
            state["error_message"] = f"{sentiment.title()} sentiment processing failed: {str(e)}"
            state["error_step"] = f"{sentiment}_sentiment_processor"
            state["error_details"] = {"exception_type": type(e).__name__, "sentiment": sentiment}
            state["status"] = "failed"
        
        return state
    
    def _agent_failure_recovery_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle agent failure recovery and rerouting.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with recovery results
        """
        try:
            logger.info("Agent Failure Recovery: Attempting to recover from agent failure")
            state["current_step"] = "agent_failure_recovery"
            
            failed_agent_id = state.get("failed_agent_id")
            failed_step = state.get("error_step")
            reroute_count = state.get("reroute_count", 0)
            max_reroutes = state.get("max_reroutes", 3)
            
            if reroute_count >= max_reroutes:
                raise Exception(f"Maximum reroute attempts ({max_reroutes}) exceeded")
            
            # Find backup agent
            backup_agent_id = self.failure_manager.find_backup_agent(state)
            
            if backup_agent_id:
                # Update agent registry to use backup agent for retry
                self._reassign_agent_for_retry(failed_agent_id, backup_agent_id, failed_step)
                
                state["backup_agent_used"] = True
                state["reroute_count"] = reroute_count + 1
                state["error_occurred"] = False  # Clear error to enable retry
                state["status"] = "rerouted"  # Reset status from failed to indicate recovery
                
                # Clear the failed step from completed steps to allow retry
                if failed_step and f"{failed_step}" in state.get("completed_steps", []):
                    state["completed_steps"].remove(failed_step)
                
                # Remove failed step results to allow fresh execution
                if failed_step and failed_step in state.get("step_results", {}):
                    state["step_results"][failed_step + "_failed"] = state["step_results"].pop(failed_step)
                
                recovery_info = {
                    "failed_agent": failed_agent_id,
                    "backup_agent": backup_agent_id,
                    "reroute_attempt": reroute_count + 1,
                    "retry_step": failed_step,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                state["completed_steps"].append("agent_failure_recovery")
                state["step_results"]["agent_failure_recovery"] = {
                    "action": "backup_agent_assigned_for_retry",
                    "recovery_info": recovery_info,
                    "status": "completed",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                logger.info(f"Agent Failure Recovery: Backup agent {backup_agent_id} assigned for retry of {failed_step}")
            else:
                raise Exception("No backup agent available for recovery")
            
        except Exception as e:
            logger.error(f"Agent Failure Recovery: Recovery failed - {str(e)}")
            state["error_occurred"] = True
            state["error_message"] = f"Agent failure recovery failed: {str(e)}"
            state["error_step"] = "agent_failure_recovery"
            state["backup_agent_used"] = False
            state["status"] = "failed"
        
        return state
    
    def _reassign_agent_for_retry(self, failed_agent_id: str, backup_agent_id: str, failed_step: str):
        """
        Temporarily reassign the backup agent to replace the failed agent.
        
        Args:
            failed_agent_id: ID of the failed agent
            backup_agent_id: ID of the backup agent
            failed_step: The step that failed
        """
        # Store original agent reference
        if not hasattr(self, '_original_agents'):
            self._original_agents = {}
        
        if failed_agent_id not in self._original_agents:
            self._original_agents[failed_agent_id] = self.worker_agents[failed_agent_id]
        
        # Temporarily replace failed agent with backup agent
        self.worker_agents[failed_agent_id] = self.worker_agents[backup_agent_id]
        
        logger.info(f"Temporarily reassigned {backup_agent_id} to handle {failed_agent_id} tasks")
    
    def _restore_original_agents(self):
        """Restore original agent assignments after retry."""
        if hasattr(self, '_original_agents'):
            for agent_id, original_agent in self._original_agents.items():
                self.worker_agents[agent_id] = original_agent
            self._original_agents.clear()
            logger.info("Original agent assignments restored")
    
    def _error_handler_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle errors in the conditional workflow.
        
        Args:
            state: Current workflow state with error information
            
        Returns:
            Updated state with error handling results
        """
        try:
            logger.error("Error Handler: Processing conditional workflow error")
            
            error_summary = {
                "error_step": state.get("error_step"),
                "error_message": state.get("error_message"),
                "error_details": state.get("error_details", {}),
                "failed_agent_id": state.get("failed_agent_id"),
                "reroute_count": state.get("reroute_count", 0),
                "backup_agent_used": state.get("backup_agent_used", False),
                "completed_steps": state.get("completed_steps", []),
                "routing_history": state.get("routing_history", []),
                "partial_results": state.get("step_results", {}),
                "error_timestamp": datetime.utcnow().isoformat()
            }
            
            state["final_result"] = {
                "workflow_status": "failed",
                "error_summary": error_summary,
                "partial_data": {
                    "analysis_result": state.get("analysis_result"),
                    "route_data": state.get("route_data", {})
                }
            }
            
            state["status"] = "failed"
            logger.error("Error Handler: Conditional workflow error processing completed")
            
        except Exception as e:
            logger.critical(f"Error Handler: Critical failure in error handling - {str(e)}")
            state["error_message"] = f"Critical error handling failure: {str(e)}"
        
        return state
    
    def _workflow_finalizer_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Finalize the conditional workflow and calculate metrics.
        
        Args:
            state: Current workflow state
            
        Returns:
            Final state with completion metrics
        """
        try:
            logger.info("Workflow Finalizer: Completing conditional workflow execution")
            
            # Calculate timing
            start_time_str = state.get("workflow_start_time")
            if start_time_str:
                start_time = datetime.fromisoformat(start_time_str)
                end_time = datetime.utcnow()
                execution_time = (end_time - start_time).total_seconds()
                
                state["workflow_end_time"] = end_time.isoformat()
                state["total_execution_time"] = execution_time
            else:
                state["workflow_end_time"] = datetime.utcnow().isoformat()
                state["total_execution_time"] = 0.0
                execution_time = 0.0
            
            # Set final status if not already failed
            if state.get("status") not in ["failed"]:
                state["status"] = "completed"
            
            # Ensure routing_decision is preserved in the final state
            if "routing_decision" not in state and state.get("routing_history"):
                # Get the most recent routing decision
                latest_routing = state["routing_history"][-1]
                state["routing_decision"] = latest_routing.get("decision")
            
            # Add completion summary to final result
            if state.get("final_result"):
                state["final_result"]["execution_metrics"] = {
                    "total_execution_time": execution_time,
                    "steps_completed": len(state.get("completed_steps", [])),
                    "workflow_status": state["status"],
                    "routing_decisions": len(state.get("routing_history", [])),
                    "agent_failures": state.get("reroute_count", 0),
                    "backup_agents_used": state.get("backup_agent_used", False)
                }
            
            logger.info(f"Workflow Finalizer: Conditional workflow {state['status']} in {execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Workflow Finalizer: Finalization failed - {str(e)}")
            state["error_occurred"] = True
            state["error_message"] = f"Workflow finalization failed: {str(e)}"
            if "workflow_end_time" not in state:
                state["workflow_end_time"] = datetime.utcnow().isoformat()
            if "total_execution_time" not in state:
                state["total_execution_time"] = 0.0
        
        return state
    
    def execute_workflow(self, input_data: Dict[str, Any], 
                        thread_id: str = "conditional_workflow") -> Dict[str, Any]:
        """
        Execute the complete conditional workflow.
        
        Args:
            input_data: Input data for the workflow
            thread_id: Thread ID for state management
            
        Returns:
            Final workflow results
        """
        try:
            initial_state = {
                "initial_input": input_data,
                "workflow_id": str(uuid.uuid4()),
                "workflow_name": "Advanced Conditional Workflow"
            }
            
            config = {"configurable": {"thread_id": thread_id}}
            final_state = self.workflow_graph.invoke(initial_state, config)
            
            return final_state
            
        except Exception as e:
            logger.error(f"Conditional workflow execution failed: {str(e)}")
            return {
                "status": "critical_failure",
                "error_message": f"Conditional workflow execution failed: {str(e)}",
                "final_result": None
            }
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """
        Get the current status of the conditional workflow orchestrator.
        
        Returns:
            Status information
        """
        return {
            "orchestrator_active": True,
            "workflow_graph_compiled": self.workflow_graph is not None,
            "available_agents": len(self.worker_agents),
            "agent_registry": self.agent_registry,
            "failure_history": len(self.failure_manager.failure_history),
            "routing_capabilities": list(self.router.routing_rules.keys()),
            "agent_status": {
                name: "available"  # Simplified status
                for name in self.worker_agents.keys()
            }
        }
