"""
AgentWeaver Backend API

FastAPI application providing REST and WebSocket endpoints for monitoring
and controlling AgentWeaver w# Include routers
from src.api.routers import agents, workflows, websocket

app.include_router(agents.router)
app.include_router(workflows.router)
app.include_router(websocket.router)ows.
"""

import sys
import os
from contextlib import asynccontextmanager
from typing import Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Add src to path for imports
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.orchestration.supervisor import SupervisorNode
from src.core.redis_config import RedisConnectionManager
from src.api.models import SystemStatusResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown tasks."""
    # Startup
    logger.info("Starting AgentWeaver API server...")
    
    # Initialize Redis connection manager
    app.state.redis_manager = RedisConnectionManager()
    logger.info("Redis connection manager initialized")
    
    # Initialize supervisor
    app.state.supervisor = SupervisorNode()
    logger.info("Supervisor initialized")
    
    # Initialize WebSocket connection manager
    from src.services.websocket_manager import WebSocketManager
    from src.services.websocket_integration import integration_service
    app.state.ws_manager = WebSocketManager()
    
    # Connect integration service to WebSocket manager
    integration_service.set_websocket_manager(app.state.ws_manager)
    
    logger.info("WebSocket manager and integration service initialized")
    
    logger.info("AgentWeaver API server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AgentWeaver API server...")
    
    # Cleanup connections
    if hasattr(app.state, 'ws_manager'):
        await app.state.ws_manager.disconnect_all()
        logger.info("WebSocket connections closed")
    
    logger.info("AgentWeaver API server shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="AgentWeaver Backend API",
    description="REST and WebSocket APIs for monitoring and controlling AgentWeaver workflows",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint returning basic API information."""
    return {
        "message": "AgentWeaver Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"], response_model=SystemStatusResponse)
async def health_check():
    """Health check endpoint to verify server status."""
    try:
        # Check Redis connection
        redis_status = "connected" if app.state.redis_manager.test_connection() else "disconnected"
        
        # Check supervisor status
        supervisor_status = "initialized" if hasattr(app.state, 'supervisor') else "not_initialized"
        
        # Check WebSocket manager
        ws_status = "initialized" if hasattr(app.state, 'ws_manager') else "not_initialized"
        ws_connections = len(app.state.ws_manager.active_connections) if hasattr(app.state, 'ws_manager') else 0
        
        return SystemStatusResponse(
            status="healthy",
            uptime=0.0,  # TODO: Calculate actual uptime
            version="1.0.0",
            timestamp=datetime.now(),
            services={
                "redis": redis_status,
                "supervisor": supervisor_status,
                "websocket_manager": ws_status
            },
            metrics={
                "active_websocket_connections": ws_connections,
                "active_agents": 0,  # TODO: Get from supervisor
                "running_workflows": 0  # TODO: Get from supervisor
            }
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


# Include routers
from src.api.routers import agents, workflows, websocket

app.include_router(agents.router)
app.include_router(workflows.router)
app.include_router(websocket.router)

@app.get("/api/info", tags=["Info"])
async def api_info():
    """Get API information and available endpoints."""
    return {
        "api": "AgentWeaver Backend API",
        "version": "1.0.0",
        "endpoints": {
            "agents": "/agents - List and manage agents",
            "workflows": "/workflows - Control workflow execution", 
            "websocket": "/ws/updates - Real-time updates"
        },
        "status": "ready"
    }


if __name__ == "__main__":
    # Run the server directly
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
