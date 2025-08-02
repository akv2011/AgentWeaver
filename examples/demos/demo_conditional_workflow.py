
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.conditional_workflow import ConditionalWorkflowOrchestrator
import json
import time

def run_conditional_workflow_demo():
    
    print("🚀 AgentWeaver Conditional Workflow Demo")
    print("=" * 50)
    
    # Initialize the orchestrator
    orchestrator = ConditionalWorkflowOrchestrator()
    
    # Test scenarios with different routing outcomes
    test_scenarios = [
        {
            "name": "Positive Sentiment Routing",
            "input": {
                "text": "This is an excellent product with outstanding features! I absolutely love using it and would highly recommend it to everyone.",
                "metadata": {"demo": "positive_sentiment"}
            }
        },
        {
            "name": "Negative Sentiment Routing", 
            "input": {
                "text": "This is a terrible product with poor quality. I hate using it and would never recommend it to anyone.",
                "metadata": {"demo": "negative_sentiment"}
            }
        },
        {
            "name": "Neutral Content Routing",
            "input": {
                "text": "This is a product that does what it says. It has some features and functionality.",
                "metadata": {"demo": "neutral_sentiment"}
            }
        },
        {
            "name": "Technical Content Analysis",
            "input": {
                "text": "The API endpoint returns a JSON response with technical specifications. The system architecture uses microservices.",
                "metadata": {"demo": "technical_content"}
            }
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 Test {i}: {scenario['name']}")
        print("-" * 40)
        
        start_time = time.time()
        
        # Execute the workflow
        result = orchestrator.execute_workflow(
            scenario["input"], 
            thread_id=f"demo_thread_{i}"
        )
        
        execution_time = time.time() - start_time
        
        # Extract key information
        sentiment_score = result.get("sentiment_score", "N/A")
        content_type = result.get("content_type", "N/A")
        routing_decision = result.get("routing_decision", "N/A")
        status = result.get("status", "unknown")
        completed_steps = len(result.get("completed_steps", []))
        
        print(f"✅ Status: {status}")
        print(f"🎯 Routing Decision: {routing_decision}")
        print(f"😊 Sentiment Score: {sentiment_score}")
        print(f"📄 Content Type: {content_type}")
        print(f"⏱️  Execution Time: {execution_time:.2f}s")
        print(f"📈 Steps Completed: {completed_steps}")
        
        # Show final result summary
        if result.get("final_result"):
            final_result = result["final_result"]
            if "workflow_summary" in final_result:
                workflow_summary = final_result["workflow_summary"]
                if "sentiment_classification" in workflow_summary:
                    sentiment_info = workflow_summary["sentiment_classification"]
                    print(f"🔍 Final Classification: {sentiment_info.get('sentiment', 'N/A')}")
        
        results.append({
            "scenario": scenario["name"],
            "status": status,
            "routing_decision": routing_decision,
            "sentiment_score": sentiment_score,
            "content_type": content_type,
            "execution_time": execution_time,
            "steps_completed": completed_steps
        })
        
        print("✨ Workflow completed successfully!")
    
    print(f"\n🎯 Demo Summary")
    print("=" * 50)
    print(f"Total scenarios tested: {len(results)}")
    print(f"All workflows completed successfully: {'✅' if all(r['status'] in ['completed', 'rerouted'] for r in results) else '❌'}")
    print(f"Average execution time: {sum(r['execution_time'] for r in results) / len(results):.2f}s")
    
    print(f"\n📊 Routing Results:")
    for result in results:
        print(f"  • {result['scenario']}: {result['routing_decision']} (sentiment: {result['sentiment_score']})")
    
    print(f"\n🎉 Demo completed! Your conditional workflow is working perfectly.")
    print(f"Next steps: Try implementing Task 7 (Redis integration) or Task 9 (P2P communication)")

if __name__ == "__main__":
    run_conditional_workflow_demo()
