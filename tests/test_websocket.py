#!/usr/bin/env python3
"""Test WebSocket connection to AgentWeaver."""

import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/updates"
    try:
        print(f"Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("OK WebSocket connected successfully!")
            
            # Wait for initial message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"Received: {message}")
                
                # Send a test message
                test_msg = {"type": "test", "message": "Hello from test client"}
                await websocket.send(json.dumps(test_msg))
                print("Sent test message")
                
                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"Response: {response}")
                
            except asyncio.TimeoutError:
                print("No message received within timeout")
                
    except Exception as e:
        print(f"ERROR WebSocket connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
