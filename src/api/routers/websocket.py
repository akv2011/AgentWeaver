"""
WebSocket Router

WebSocket endpoints for real-time updates and communication.
"""

import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse

from src.services.websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/ws", tags=["WebSocket"])

# Global WebSocket manager instance
ws_manager: Optional[WebSocketManager] = None


def get_websocket_manager() -> WebSocketManager:
    """Get the global WebSocket manager instance."""
    global ws_manager
    if ws_manager is None:
        # This will be set from the main app
        from main import app
        ws_manager = app.state.ws_manager
    return ws_manager


@router.websocket("/updates")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None, description="Unique client identifier"),
    filters: Optional[str] = Query(None, description="Comma-separated event filters")
):
    """
    WebSocket endpoint for real-time updates.
    
    Clients can connect to this endpoint to receive real-time updates about:
    - Agent status changes
    - Workflow progress updates
    - System notifications
    - Error events
    - Performance metrics
    
    Query Parameters:
    - client_id: Optional unique identifier for the client
    - filters: Comma-separated list of event types to subscribe to
      (agent_updates, workflow_updates, system_notifications, error_events, all)
    """
    manager = get_websocket_manager()
    
    # Parse filters
    subscription_filters = []
    if filters:
        subscription_filters = [f.strip() for f in filters.split(",")]
    
    # Prepare client info
    client_info = {
        "client_id": client_id or f"client_{id(websocket)}",
        "subscription_filters": subscription_filters,
        "connected_at": datetime.now().isoformat(),
        "user_agent": websocket.headers.get("user-agent", "unknown"),
        "origin": websocket.headers.get("origin", "unknown")
    }
    
    try:
        # Accept the WebSocket connection
        await manager.connect(websocket, client_info)
        logger.info(f"WebSocket client connected: {client_info['client_id']}")
        
        # Send initial system status
        await manager.send_to_client(websocket, {
            "type": "system_status",
            "message": "Connected to AgentWeaver real-time updates",
            "system_info": {
                "version": "1.0.0",
                "active_connections": len(manager.active_connections),
                "available_events": [
                    "agent_updates",
                    "workflow_updates", 
                    "system_notifications",
                    "error_events",
                    "performance_metrics"
                ]
            },
            "client_info": client_info
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                logger.debug(f"Received message from {client_info['client_id']}: {message}")
                
                # Handle different message types
                await handle_client_message(websocket, message, manager)
                
            except WebSocketDisconnect:
                # Client disconnected, exit the loop
                logger.info(f"Client {client_info['client_id']} disconnected during message receive")
                break
            except json.JSONDecodeError:
                try:
                    await manager.send_to_client(websocket, {
                        "type": "error",
                        "message": "Invalid JSON format",
                        "timestamp": datetime.now().isoformat()
                    })
                except:
                    # Connection might be closed
                    break
            except Exception as e:
                logger.error(f"Error processing client message: {e}")
                try:
                    await manager.send_to_client(websocket, {
                        "type": "error", 
                        "message": f"Error processing message: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    })
                except:
                    # Connection might be closed
                    break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {client_info['client_id']}")
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        await manager.disconnect(websocket)


async def handle_client_message(websocket: WebSocket, message: Dict[str, Any], manager: WebSocketManager):
    """Handle incoming messages from WebSocket clients."""
    try:
        message_type = message.get("type", "unknown")
        
        if message_type == "ping":
            # Respond to ping with pong
            await manager.send_to_client(websocket, {
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            })
            
        elif message_type == "subscribe":
            # Update subscription filters
            filters = message.get("filters", [])
            if websocket in manager.connection_info:
                manager.connection_info[websocket]["subscription_filters"] = filters
                await manager.send_to_client(websocket, {
                    "type": "subscription_updated",
                    "filters": filters,
                    "message": f"Subscribed to {len(filters)} event types",
                    "timestamp": datetime.now().isoformat()
                })
            
        elif message_type == "get_stats":
            # Send connection statistics
            stats = manager.get_connection_stats()
            await manager.send_to_client(websocket, {
                "type": "connection_stats",
                "stats": stats,
                "timestamp": datetime.now().isoformat()
            })
            
        elif message_type == "get_system_status":
            # Send current system status
            await manager.send_to_client(websocket, {
                "type": "system_status",
                "status": {
                    "active_connections": len(manager.active_connections),
                    "server_time": datetime.now().isoformat(),
                    "uptime": "unknown",  # TODO: Calculate actual uptime
                    "version": "1.0.0"
                },
                "timestamp": datetime.now().isoformat()
            })
            
        else:
            # Unknown message type
            await manager.send_to_client(websocket, {
                "type": "error",
                "message": f"Unknown message type: {message_type}",
                "supported_types": ["ping", "subscribe", "get_stats", "get_system_status"],
                "timestamp": datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error handling client message: {e}")
        await manager.send_to_client(websocket, {
            "type": "error",
            "message": f"Error handling message: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })


@router.get("/test", response_class=HTMLResponse)
async def websocket_test_page():
    """
    Simple HTML page for testing WebSocket connections.
    
    This endpoint returns a basic HTML page that can be used to test
    the WebSocket functionality during development.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AgentWeaver WebSocket Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
            .connected { background-color: #d4edda; color: #155724; }
            .disconnected { background-color: #f8d7da; color: #721c24; }
            .message { background-color: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 3px; font-family: monospace; }
            button { padding: 10px 20px; margin: 5px; background-color: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; }
            button:hover { background-color: #0056b3; }
            button:disabled { background-color: #6c757d; cursor: not-allowed; }
            input { padding: 8px; margin: 5px; border: 1px solid #ccc; border-radius: 3px; }
            #messages { height: 300px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AgentWeaver WebSocket Test</h1>
            
            <div id="status" class="status disconnected">
                Status: Disconnected
            </div>
            
            <div>
                <input type="text" id="clientId" placeholder="Client ID (optional)" />
                <input type="text" id="filters" placeholder="Filters (comma-separated)" value="all" />
                <button onclick="connect()">Connect</button>
                <button onclick="disconnect()">Disconnect</button>
            </div>
            
            <div>
                <h3>Send Test Messages:</h3>
                <button onclick="sendPing()">Send Ping</button>
                <button onclick="getStats()">Get Stats</button>
                <button onclick="getSystemStatus()">Get System Status</button>
                <button onclick="sendCustomMessage()">Send Custom Message</button>
            </div>
            
            <div>
                <h3>Messages:</h3>
                <div id="messages"></div>
                <button onclick="clearMessages()">Clear Messages</button>
            </div>
        </div>

        <script>
            let ws = null;
            
            function connect() {
                const clientId = document.getElementById('clientId').value;
                const filters = document.getElementById('filters').value;
                
                let url = 'ws://localhost:8000/ws/updates';
                const params = new URLSearchParams();
                if (clientId) params.append('client_id', clientId);
                if (filters) params.append('filters', filters);
                if (params.toString()) url += '?' + params.toString();
                
                ws = new WebSocket(url);
                
                ws.onopen = function(event) {
                    updateStatus('Connected', true);
                    addMessage('Connected to WebSocket', 'info');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    addMessage('Received: ' + JSON.stringify(data, null, 2), 'received');
                };
                
                ws.onclose = function(event) {
                    updateStatus('Disconnected', false);
                    addMessage('WebSocket connection closed', 'info');
                };
                
                ws.onerror = function(error) {
                    addMessage('WebSocket error: ' + error, 'error');
                };
            }
            
            function disconnect() {
                if (ws) {
                    ws.close();
                    ws = null;
                }
            }
            
            function sendPing() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const message = { type: 'ping' };
                    ws.send(JSON.stringify(message));
                    addMessage('Sent: ' + JSON.stringify(message), 'sent');
                }
            }
            
            function getStats() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const message = { type: 'get_stats' };
                    ws.send(JSON.stringify(message));
                    addMessage('Sent: ' + JSON.stringify(message), 'sent');
                }
            }
            
            function getSystemStatus() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const message = { type: 'get_system_status' };
                    ws.send(JSON.stringify(message));
                    addMessage('Sent: ' + JSON.stringify(message), 'sent');
                }
            }
            
            function sendCustomMessage() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const message = { 
                        type: 'custom',
                        data: 'Hello from test client',
                        timestamp: new Date().toISOString()
                    };
                    ws.send(JSON.stringify(message));
                    addMessage('Sent: ' + JSON.stringify(message), 'sent');
                }
            }
            
            function updateStatus(status, connected) {
                const statusEl = document.getElementById('status');
                statusEl.textContent = 'Status: ' + status;
                statusEl.className = 'status ' + (connected ? 'connected' : 'disconnected');
            }
            
            function addMessage(message, type) {
                const messagesEl = document.getElementById('messages');
                const messageEl = document.createElement('div');
                messageEl.className = 'message';
                messageEl.innerHTML = '<strong>' + new Date().toLocaleTimeString() + '</strong> [' + type + '] ' + message;
                messagesEl.appendChild(messageEl);
                messagesEl.scrollTop = messagesEl.scrollHeight;
            }
            
            function clearMessages() {
                document.getElementById('messages').innerHTML = '';
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.get("/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics.
    
    Returns information about active WebSocket connections and usage metrics.
    """
    try:
        manager = get_websocket_manager()
        stats = manager.get_connection_stats()
        
        return {
            "websocket_stats": stats,
            "timestamp": datetime.now().isoformat(),
            "server_info": {
                "version": "1.0.0",
                "uptime": "unknown"  # TODO: Calculate actual uptime
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting WebSocket stats: {e}")
        return {
            "error": f"Failed to get WebSocket stats: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


# Helper functions for broadcasting updates (to be used by other parts of the system)
async def broadcast_agent_update(agent_id: str, status: str, details: Dict[str, Any] = None):
    """Broadcast an agent status update to all connected WebSocket clients."""
    try:
        manager = get_websocket_manager()
        await manager.send_agent_update(agent_id, status, details)
        logger.debug(f"Broadcasted agent update: {agent_id} -> {status}")
    except Exception as e:
        logger.error(f"Error broadcasting agent update: {e}")


async def broadcast_workflow_update(workflow_id: str, status: str, step: str = None, details: Dict[str, Any] = None):
    """Broadcast a workflow progress update to all connected WebSocket clients."""
    try:
        manager = get_websocket_manager()
        await manager.send_workflow_update(workflow_id, status, step, details)
        logger.debug(f"Broadcasted workflow update: {workflow_id} -> {status}")
    except Exception as e:
        logger.error(f"Error broadcasting workflow update: {e}")


async def broadcast_system_notification(notification_type: str, message: str, level: str = "info"):
    """Broadcast a system notification to all connected WebSocket clients."""
    try:
        manager = get_websocket_manager()
        await manager.send_system_notification(notification_type, message, level)
        logger.debug(f"Broadcasted system notification: {notification_type}")
    except Exception as e:
        logger.error(f"Error broadcasting system notification: {e}")
