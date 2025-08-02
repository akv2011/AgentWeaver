// Add this to the browser console to debug WebSocket status
function debugWebSocketStatus() {
    console.log("=== WebSocket Status Debug ===");
    
    // Check if the debugWebSocket function exists
    if (window.debugWebSocket) {
        console.log("Calling debugWebSocket function...");
        window.debugWebSocket();
    } else {
        console.log("debugWebSocket function not found");
    }
    
    // Check WebSocket service directly
    const service = window.defaultWebSocketService;
    if (service) {
        console.log("WebSocket service status:", service.getConnectionStatus());
        console.log("WebSocket service isConnected:", service.isConnected());
    } else {
        console.log("WebSocket service not found on window");
    }
    
    console.log("========================");
}

// Call it
debugWebSocketStatus();
