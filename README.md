# AgentWeaver

Multi-agent orchestration system built with LangGraph. Production-ready platform for coordinating AI agents in complex workflows.

## What This System Does

A comprehensive agent management system that handles:
- Multiple AI agents working together
- State persistence with Redis
- Real-time WebSocket updates
- Hierarchical agent communication
- Workflow orchestration and monitoring

## Quick Start

```bash
# Start Redis instance
docker-compose -f docker-compose.redis.yml up -d

# Install dependencies
pip install -r requirements.txt

# Run agent server
python main.py
```

The API runs on http://localhost:8000 with real-time monitoring dashboard.

## Architecture

- **Core**: Agent state management and data models
- **Orchestration**: Supervisor nodes and workflow coordination  
- **Communication**: P2P agent messaging and hierarchical structures
- **API**: FastAPI server with WebSocket support
- **Frontend**: React dashboard for monitoring

## Production Ready

All tests pass, Redis fallback works, and the system handles real workloads reliably.