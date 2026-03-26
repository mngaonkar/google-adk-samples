from declarative_agent_sdk.logging_config import setup_logging, get_logger

setup_logging(level="INFO")
logger = get_logger(__name__)

from declarative_agent_sdk.tool_registry import ToolRegistry
from declarative_agent_sdk import AgentFactory
import os
from declarative_agent_sdk.utils import save_to_file
from dotenv import load_dotenv

load_dotenv()

WORKSPACE_DIRECTORY = "workspace"

def music_agent(input: str) -> None:
    agent = AgentFactory.from_yaml_file('configs/music_agent.yaml')
    logger.info("Music agent initialized.")

    result = agent.run_sync(input)
    logger.debug(f"Music agent generated response: {result}")

    try:
        if not os.path.exists(WORKSPACE_DIRECTORY):
            os.makedirs(WORKSPACE_DIRECTORY)
    except Exception as e:
        logger.error(f"Failed to create output directory {WORKSPACE_DIRECTORY}: {e}")
        raise

    agent_output_file = os.path.join(WORKSPACE_DIRECTORY, agent.name)

    response = result.get("final_response", "")
    save_to_file(response, agent_output_file)
    logger.info(f"Music agent response saved to {agent_output_file}")

    return

if __name__ == "__main__":
    test_input = "Generate a 2 min song from current political news from internet as lyrics."
    music_agent(test_input)
