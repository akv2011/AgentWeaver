# AgentWeaver Project Structure

This document describes the organized structure of the AgentWeaver project after cleanup and reorganization.

## Directory Structure

```
AgentWeaver/
├── src/                           # Main source code
│   ├── core/                      # Core components
│   │   ├── models.py             # Data models and enums
│   │   ├── state_manager.py      # State management
│   │   ├── redis_config.py       # Redis configuration
│   │   └── __init__.py
│   ├── orchestration/            # Orchestration and supervision
│   │   ├── supervisor.py         # Basic supervisor
│   │   ├── enhanced_supervisor.py # Enhanced supervisor
│   │   ├── swarm_supervisor.py   # Swarm orchestration
│   │   ├── parallel_execution_nodes.py # Parallel execution
│   │   └── __init__.py
│   ├── communication/            # Agent communication
│   │   ├── p2p_communication.py  # Peer-to-peer communication
│   │   ├── agent_integration.py  # Agent integration services
│   │   ├── hierarchical_workflow.py # Hierarchical workflows
│   │   └── __init__.py
│   ├── agents/                   # Worker agents
│   │   ├── base_agent.py
│   │   ├── text_analysis_agent.py
│   │   ├── data_processing_agent.py
│   │   ├── api_interaction_agent.py
│   │   └── concurrent_worker_adapter.py
│   ├── workflows/                # Workflow definitions
│   ├── api/                      # API layer
│   ├── services/                 # Business services
│   ├── config/                   # Configuration
│   ├── linear_workflow.py        # Linear workflow implementation
│   ├── conditional_workflow.py   # Conditional workflow implementation
│   └── __init__.py               # Main package exports
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── ...
├── api/                          # FastAPI backend
├── frontend/                     # React frontend
├── examples/                     # Examples and demos
│   └── demos/                    # Demo scripts
│       ├── hello_world.py
│       └── simple_test.py
├── docs/                         # Documentation
├── data/                         # Data files
├── logs/                         # Log files
├── config/                       # Configuration files
├── main.py                       # Main application entry point
├── setup.py                      # Package setup
├── requirements.txt              # Dependencies
├── Dockerfile                    # Docker configuration
├── docker-compose.redis.yml      # Redis Docker compose
├── README.md                     # Project documentation
└── PROJECT_SETUP.md              # Setup instructions
```

## Key Changes Made

### Files Removed
- All `__pycache__/` directories (Python cache)
- `.pytest_cache/` directory
- Empty `scripts/` directory

### Files Moved
- `hello_world.py` → `examples/demos/`
- `simple_test.py` → `examples/demos/`
- `models.py` → `src/core/`
- `state_manager.py` → `src/core/`
- `redis_config.py` → `src/core/`
- `supervisor.py` → `src/orchestration/`
- `enhanced_supervisor.py` → `src/orchestration/`
- `swarm_supervisor.py` → `src/orchestration/`
- `parallel_execution_nodes.py` → `src/orchestration/`
- `p2p_communication.py` → `src/communication/`
- `agent_integration.py` → `src/communication/`
- `hierarchical_workflow.py` → `src/communication/`

### New Directories Created
- `src/core/` - Core data models and state management
- `src/orchestration/` - Supervision and parallel execution
- `src/communication/` - Agent communication patterns

### Package Structure
Each new directory has proper `__init__.py` files with appropriate exports, making the codebase more modular and easier to import.

## Import Changes

With the new structure, imports should be updated to:

```python
# Core components
from src.core import AgentState, Task, Message, StateManager

# Orchestration
from src.orchestration import SupervisorNode, SwarmSupervisorNode
from src.orchestration import ParallelForkNode, ParallelWorkerNode

# Communication
from src.communication import P2PCommunicationNode, AgentIntegrationService

# Or use the main package imports
from src import SupervisorNode, ParallelForkNode, AgentState
```

This organization provides:
- **Better separation of concerns**
- **Cleaner import structure**
- **Easier navigation and maintenance**
- **Logical grouping of related functionality**
- **Reduced clutter in the root and src directories**
