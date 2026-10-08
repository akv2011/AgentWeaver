#!/usr/bin/env python3
"""
Simple AgentWeaver demo that triggers real dashboard updates
"""

import requests
import time

def trigger_dashboard_demo():
    """Trigger demo workflows to see dashboard updates"""
    print("AgentWeaver Dashboard Demo")
    print("=" * 50)
    print("This demo will trigger real workflows to update your dashboard!")
    print()
    
    try:
        # Trigger multiple demo workflows to show dashboard activity
        for i in range(3):
            print(f"Triggering demo workflow #{i+1}...")
            
            response = requests.post("http://localhost:8000/api/test/demo-workflow")
            
            if response.status_code == 200:
                result = response.json()
                print(f"OK {result['message']}")
                print(f"   Workflow ID: {result['workflow_id']}")
                
                if i < 2:  # Don't wait after the last one
                    print("   Waiting 8 seconds before next workflow...")
                    time.sleep(8)  # Wait for workflow to complete
                    print()
            else:
                print(f"ERROR Failed: {response.status_code}")
                break
                
        print()
        print("Demo completed! Your dashboard should show:")
        print("   OK Agent status changes (idle → busy → idle)")
        print("   OK Workflow progress updates")
        print("   OK Real-time WebSocket connectivity")
        print("   OK Live agent data instead of mock data")
        print()
        print("Check your browser at http://localhost:3000")
        
    except requests.exceptions.ConnectionError:
        print("ERROR Could not connect to AgentWeaver server!")
        print("   Make sure the server is running: python main.py")
    except Exception as e:
        print(f"ERROR Error: {e}")

if __name__ == "__main__":
    trigger_dashboard_demo()
