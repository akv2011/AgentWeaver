"""
Hello World LangGraph example to verify installation and basic functionality.
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator


class State(TypedDict):
    """State definition for the hello world graph."""
    messages: Annotated[list[str], operator.add]
    counter: int


def hello_node(state: State) -> State:
    """A simple node that adds a hello message."""
    return {
        "messages": ["Hello from LangGraph!"],
        "counter": state.get("counter", 0) + 1
    }


def world_node(state: State) -> State:
    """A simple node that adds a world message."""
    return {
        "messages": ["World from AgentWeaver!"],
        "counter": state.get("counter", 0) + 1
    }


def create_hello_world_graph():
    """Create and return a simple hello world graph."""
    # Create the graph
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("hello", hello_node)
    workflow.add_node("world", world_node)
    
    # Set entry point
    workflow.set_entry_point("hello")
    
    # Add edges
    workflow.add_edge("hello", "world")
    workflow.add_edge("world", END)
    
    # Compile the graph
    app = workflow.compile()
    return app


def main():
    """Run the hello world example."""
    print("🚀 Testing LangGraph installation...")
    
    # Create the graph
    app = create_hello_world_graph()
    
    # Run the graph
    initial_state = {"messages": [], "counter": 0}
    result = app.invoke(initial_state)
    
    print("✅ LangGraph test successful!")
    print(f"Messages: {result['messages']}")
    print(f"Counter: {result['counter']}")
    print("📋 All dependencies installed correctly!")


if __name__ == "__main__":
    main()
