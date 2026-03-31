"""
A2UI Agent - Direct Invocation

This module provides direct (non-A2A) invocation of the A2UI agent.
For A2A protocol support with FastAPI server, see a2a_server.py

Usage:
    python agent.py
    
For A2A invocation:
    python a2a_server.py  # Start the A2A server
    python a2a_client.py  # Test the A2A endpoints
"""

from declarative_agent_sdk.agent_logging import setup_logging, get_logger
from typing import Any

setup_logging(level="INFO")
logger = get_logger(__name__)

from declarative_agent_sdk import AgentFactory, AgentRegistry, AIAgentServer

agent = AgentFactory.from_yaml_file('configs/a2ui_agent.yaml')
AgentRegistry.register(agent, category='ui')
logger.info("A2UI agent initialized and registered.")

server = AIAgentServer(agent, host="0.0.0.0", port=9999)
logger.info("A2UI agent server initialized.")

def a2ui_agent(input: str) -> Any:
    result = agent.run_sync(input)
    logger.debug(f"A2UI agent generated response: {result}")
    return result

def run_once(input: str) -> Any:
    """Run the agent once with the given input and return the result."""
    response = a2ui_agent(input)
    print("\n" + "="*60)
    print("A2UI Agent Response:")
    print("="*60 + "\n")
    print(response)

def run_server():
    """Run the A2UI agent server for A2A protocol support."""
    logger.info("Starting A2UI agent server...")
    server.run()

if __name__ == "__main__":
    test_input = "Create a UI with a welcome message, a list of 3 restaurants with images and ratings, and a button to refresh the list."
    # run_once(test_input)
    run_server()

