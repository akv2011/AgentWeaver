#!/usr/bin/env python3
"""
Simple demo trigger using requests (no async needed)
"""

import requests
import time

def trigger_demo_workflow():
    """Trigger a demo workflow via HTTP request"""
    try:
        print("Triggering demo workflow...")
        
        response = requests.post("http://localhost:8000/api/test/demo-workflow")
        
        if response.status_code == 200:
            result = response.json()
            print(f"OK {result['message']}")
            print(f"   Workflow ID: {result['workflow_id']}")
            print(f"   {result['check_dashboard']}")
            print()
            print("Watch your dashboard for real-time updates!")
            print("   - Agent statuses will change")
            print("   - Workflow progress will update")
            print("   - Real agents will replace mock data")
        else:
            print(f"ERROR Failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"ERROR Error: {e}")

if __name__ == "__main__":
    trigger_demo_workflow()
