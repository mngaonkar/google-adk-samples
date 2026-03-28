from declarative_agent_sdk.agent_logging import setup_logging, get_logger
from declarative_agent_sdk.constants import WORKSPACE_DIRECTORY

setup_logging(level="INFO")
logger = get_logger(__name__)

from declarative_agent_sdk import AgentFactory, AgentRegistry
import os
from declarative_agent_sdk.utils import save_to_file, remove_think_content
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

load_dotenv()

def autoresearch_agent(input: str) -> None:
    agent = AgentFactory.from_yaml_file('configs/autoresearch.yaml')
    AgentRegistry.register(agent, category='autoresearch')
    logger.info("Autoresearch agent initialized and registered.")

    result = agent.run_sync(input)
    logger.debug(f"Autoresearch agent generated response: {result}")

    agent_output_file = os.path.join(WORKSPACE_DIRECTORY, agent.name)

    response = result.get("final_response", "")
    save_to_file(response, agent_output_file)
    logger.info(f"Autoresearch agent response saved to {agent_output_file}")

    cleaned_response = remove_think_content(response)
    logger.info(f"Cleaned Autoresearch agent response:\n{cleaned_response}")
    
    # Display markdown in terminal
    console = Console()
    console.print("\n" + "="*60)
    console.print("[bold cyan]Autoresearch Agent Response:[/bold cyan]")
    console.print("="*60 + "\n")
    console.print(Markdown(cleaned_response))
    console.print("\n" + "="*60)

    return

if __name__ == "__main__":
    test_input = "perform the experiment to test the effect of different learning rates on model convergence for a sample dataset."
    autoresearch_agent(test_input)
