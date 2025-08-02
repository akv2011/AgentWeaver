console.log("=== WEBSOCKET DEBUG SCRIPT ===");
console.log("Current time:", new Date().toISOString());

// Check if WebSocket service exists
if (window.WebSocket) {
    console.log("✅ WebSocket API available");
    
    // Connect to the same endpoint the frontend uses
    const ws = new WebSocket('ws://localhost:8000/ws/updates');
    
    ws.onopen = function() {
        console.log("✅ Raw WebSocket connection opened");
        console.log("   readyState:", ws.readyState);
        console.log("   url:", ws.url);
    };
    
    ws.onmessage = function(event) {
        console.log("📥 Raw WebSocket message:", event.data);
        try {
            const parsed = JSON.parse(event.data);
            console.log("   Parsed:", parsed);
        } catch (e) {
            console.log("   Parse error:", e);
        }
    };
    
    ws.onclose = function(event) {
        console.log("❌ Raw WebSocket closed:", event.code, event.reason);
    };
    
    ws.onerror = function(error) {
        console.log("❌ Raw WebSocket error:", error);
    };
    
    // Close after 5 seconds for testing
    setTimeout(() => {
        console.log("🔒 Closing test WebSocket connection");
        ws.close();
    }, 5000);
    
} else {
    console.log("❌ WebSocket API not available");
}
