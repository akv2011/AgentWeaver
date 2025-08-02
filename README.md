# AgentWeaver

I built this multi-agent orchestration system to solve the complexity of coordinating multiple AI agents in real-world applications. After working with various agent frameworks, I wanted something that could handle enterprise-level workflows while remaining simple to use.

## What I Created

This system represents my solution to several key challenges I encountered:
- **Agent Coordination**: Managing multiple AI agents that need to work together on complex tasks
- **State Management**: Persistent storage with Redis that survives restarts and crashes
- **Real-time Monitoring**: Live dashboard to see what your agents are actually doing
- **Scalable Architecture**: From simple linear workflows to complex hierarchical structures
- **Production Reliability**: Built to handle real workloads, not just demos

## Getting Started

I've made setup as straightforward as possible:

```bash
# Start Redis (required for state persistence)
docker-compose -f docker-compose.redis.yml up -d

# Install dependencies
pip install -r requirements.txt

# Launch the system
python main.py
```

Your agent dashboard will be available at http://localhost:8000

## System Architecture

I designed this with modularity in mind:

- **Core Engine**: Handles agent lifecycle and state management
- **Orchestration Layer**: Supervisor nodes that coordinate workflows
- **Communication System**: P2P messaging and hierarchical agent structures
- **REST API**: FastAPI backend with WebSocket support for real-time updates
- **React Frontend**: Clean dashboard for monitoring and debugging

## Why I Built This

After working with existing frameworks, I found they either lacked production features or were too complex for practical use. AgentWeaver bridges that gap - it's enterprise-ready but doesn't require a PhD to understand.

The system has been tested extensively and handles real production workloads reliably.