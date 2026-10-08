#!/usr/bin/env python3
"""
Simple script to test WebSocket connections and count them.
"""

import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket_connection():
    """Test a single WebSocket connection."""
    uri = "ws://localhost:8000/ws/updates"
    
    try:
        print(f"Connecting to {uri}")
        
        async with websockets.connect(uri) as websocket:
            print("OK Connected successfully!")
            
            # Wait for initial message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"Received: {data.get('type', 'unknown')}")
            except asyncio.TimeoutError:
                print("No initial message received (timeout)")
            
            print("Closing connection...")
            
    except Exception as e:
        print(f"ERROR Connection failed: {e}")

async def main():
    """Test WebSocket connection."""
    print("Testing WebSocket Connection")
    print("="*50)
    
    await test_websocket_connection()
    
    print("="*50)
    print("OK Test complete!")

if __name__ == "__main__":
    asyncio.run(main())
