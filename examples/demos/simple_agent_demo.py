#!/usr/bin/env python3
"""
Simple AgentWeaver demo to show real agents in action
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def run_simple_agent_demo():
    print("AgentWeaver Real Agents Demo")
    print("=" * 50)
    
    try:
        from src.linear_workflow import LinearWorkflowOrchestrator
        
        # Initialize the orchestrator
        print("Initializing workflow orchestrator...")
        orchestrator = LinearWorkflowOrchestrator()
        
        # Check orchestrator status
        status = orchestrator.get_workflow_status()
        print(f"OK Orchestrator ready: {status['available_agents']} agents available")
        print(f"   Agents: {list(status['agent_status'].keys())}")
        print()
        
        # Fixed demo data with all required fields
        demo_input = {
            "text": "This is a comprehensive customer review analysis for our Q1 2024 feedback. The feedback shows positive sentiment overall with customers praising our new features and improved user interface. However, some concerns were raised about response times and billing clarity.",
            "numbers": [87, 92, 89, 94, 91, 88, 95, 90, 93, 86, 89, 92],  # Customer satisfaction scores
            "metadata": {
                "source": "customer_feedback_q1_2024",
                "domain": "product_analysis", 
                "priority": "high",
                "analyst": "demo_system"
            }
        }
        
        print("Demo Input Summary:")
        print(f"   • Text length: {len(demo_input['text'])} characters")
        print(f"   • Satisfaction scores: {len(demo_input['numbers'])} data points")
        print(f"   • Average score: {sum(demo_input['numbers'])/len(demo_input['numbers']):.1f}%")
        print()
        
        # Execute the workflow
        print("Executing linear workflow...")
        print("   Step 1: Text Analysis → Step 2: Data Enrichment → Step 3: Statistical Processing")
        print()
        
        start_time = datetime.utcnow()
        result = orchestrator.execute_workflow(demo_input, "demo_workflow_2024")
        end_time = datetime.utcnow()
        
        execution_time = (end_time - start_time).total_seconds()
        
        print(f" Workflow completed in {execution_time:.2f} seconds")
        print()
        
        # Display results
        if result.get("status") == "completed":
            print("OK Workflow executed successfully!")
            
            final_result = result.get("final_result", {})
            if final_result:
                print("Final Results:")
                
                # Show what each step produced
                if "step1_data" in final_result:
                    step1 = final_result["step1_data"]
                    print(f"   • Text Analysis: {step1.get('sentiment', 'N/A')} sentiment detected")
                    if "word_count" in step1:
                        print(f"     Word count: {step1['word_count']}")
                
                if "step2_data" in final_result:
                    step2 = final_result["step2_data"]
                    print(f"   • Data Enrichment: Added {len(step2.get('enrichments', []))} enrichments")
                
                if "step3_data" in final_result:
                    step3 = final_result["step3_data"]
                    print(f"   • Statistical Analysis: {step3.get('summary', 'Processing completed')}")
                
                # Show execution metrics
                execution_metrics = final_result.get("execution_metrics", {})
                if execution_metrics:
                    print(f"   • Total steps completed: {execution_metrics.get('steps_completed', 0)}")
                    print(f"   • Workflow execution time: {execution_metrics.get('total_execution_time', 0):.2f}s")
                    print(f"   • Final status: {execution_metrics.get('workflow_status', 'unknown')}")
            
            print()
            print("This demonstrates:")
            print("   • Real agent coordination (not mock data!)")
            print("   • Multi-step workflow execution")
            print("   • Agent state management")
            print("   • Data flow between agents")
            
        else:
            print("ERROR Workflow failed!")
            print(f"   Error: {result.get('error_message', 'Unknown error')}")
            print(f"   Failed at step: {result.get('error_step', 'Unknown step')}")
        
    except ImportError as e:
        print(f"ERROR Could not import workflow orchestrator: {e}")
        print("   Make sure you're in the AgentWeaver directory")
    except Exception as e:
        print(f"ERROR Demo failed: {e}")

if __name__ == "__main__":
    run_simple_agent_demo()
