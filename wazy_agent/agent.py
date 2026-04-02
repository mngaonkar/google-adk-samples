from declarative_agent_sdk.agent_logging import setup_logging, get_logger

setup_logging(level="INFO")
logger = get_logger(__name__)

from declarative_agent_sdk import AgentFactory, AgentRegistry, AIAgentServer
import os
from declarative_agent_sdk.utils import save_to_file, remove_think_content
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

load_dotenv()

WORKSPACE_DIRECTORY = "workspace"
PORT=10004 # hard-coded in UI side, need a fix

def wazy_agent(input: str) -> None:
    agent = AgentFactory.from_yaml_file('configs/wazy_agent.yaml')
    AgentRegistry.register(agent, category='travel')
    logger.info("Wazy agent initialized and registered.")

    result = agent.run_sync(input)
    logger.debug(f"Wazy agent generated response: {result}")

    try:
        if not os.path.exists(WORKSPACE_DIRECTORY):
            os.makedirs(WORKSPACE_DIRECTORY)
    except Exception as e:
        logger.error(f"Failed to create output directory {WORKSPACE_DIRECTORY}: {e}")
        raise

    agent_output_file = os.path.join(WORKSPACE_DIRECTORY, agent.name)

    response = result.get("final_response", "")
    save_to_file(response, agent_output_file)
    logger.info(f"Wazy agent response saved to {agent_output_file}")

    cleaned_response = remove_think_content(response)
    logger.info(f"Cleaned Wazy agent response:\n{cleaned_response}")
    
    # Display markdown in terminal
    console = Console()
    console.print("\n" + "="*60)
    console.print("[bold cyan]Wazy Agent Response:[/bold cyan]")
    console.print("="*60 + "\n")
    console.print(Markdown(cleaned_response))
    console.print("\n" + "="*60)

    return

def run_server():
    agent = AgentFactory.from_yaml_file('configs/wazy_agent.yaml')
    AgentRegistry.register(agent, category='travel')
    logger.info("Wazy agent initialized and registered.")

    server = AIAgentServer(agent, host="0.0.0.0", port=PORT)
    logger.info("Wazy agent server initialized.")
    server.run()

def run_once(input: str) -> None:
    response = wazy_agent(input)
    print("\n" + "="*60)
    print("Wazy Agent Response:")
    print("="*60 + "\n")
    print(response)

if __name__ == "__main__":
    test_input = "Plan a road trip from San Francisco to Los Angeles with stops every 2 hours."
    # run_once(test_input)
    run_server()
