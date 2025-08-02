#!/usr/bin/env python3
"""
Simple test to verify imports work correctly.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")
    
    try:
        print("  Importing models...", end=" ")
        from src.models import AgentState, Task, AgentCapability
        print("✅")
        
        print("  Importing base agent...", end=" ")
        from src.agents.base_agent import BaseWorkerAgent
        print("✅")
        
        print("  Importing text analysis agent...", end=" ")
        from src.agents.text_analysis_agent import TextAnalysisAgent
        print("✅")
        
        print("  Importing API interaction agent...", end=" ")
        from src.agents.api_interaction_agent import APIInteractionAgent
        print("✅")
        
        print("  Importing data processing agent...", end=" ")
        from src.agents.data_processing_agent import DataProcessingAgent
        print("✅")
        
        print("  Importing supervisor...", end=" ")
        from src.supervisor import SupervisorNode
        print("✅")
        
        print("  Importing agent integration...", end=" ")
        from src.agent_integration import AgentRegistry
        print("✅")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_agent_creation():
    """Test that agents can be created."""
    print("\nTesting agent creation...")
    
    try:
        from src.agents.text_analysis_agent import TextAnalysisAgent
        from src.agents.api_interaction_agent import APIInteractionAgent
        from src.agents.data_processing_agent import DataProcessingAgent
        
        print("  Creating TextAnalysisAgent...", end=" ")
        text_agent = TextAnalysisAgent("TestTextAgent")
        print(f"✅ (ID: {text_agent.agent_id[:8]}...)")
        
        print("  Creating APIInteractionAgent...", end=" ")
        api_agent = APIInteractionAgent("TestAPIAgent")
        print(f"✅ (ID: {api_agent.agent_id[:8]}...)")
        
        print("  Creating DataProcessingAgent...", end=" ")
        data_agent = DataProcessingAgent("TestDataAgent")
        print(f"✅ (ID: {data_agent.agent_id[:8]}...)")
        
        print("\n🎉 All agents created successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Agent creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 AgentWeaver Simple Import Test\n")
    
    success1 = test_imports()
    if not success1:
        sys.exit(1)
    
    success2 = test_basic_agent_creation()
    if not success2:
        sys.exit(1)
    
    print("\n✨ All tests passed! The worker agents are ready to use.")
    sys.exit(0)
