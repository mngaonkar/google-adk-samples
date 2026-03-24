from typing import Literal
from agent_state import BookAgentState
from utils.read_file import read_file_content
from dotenv import load_dotenv
import logging
import asyncio
import os
from sdk.workflow_registry import WorkflowRegistry
from sdk.workflow_factory import WorkflowFactory
from sdk.tool_registry import ToolRegistry
from register_skills import register_all_skills
from toc_agent.agent import toc_agent
from chapter_agent.agent import chapter_agent_parallel
from collation_agent.agent import collation_agent


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Register all skills at startup
register_all_skills()

def route_after_toc(state: BookAgentState) -> Literal["chapter_agent_parallel", "toc_agent"]:
    """If TOC YAML is valid, proceed to chapters; otherwise retry toc_agent."""    
    toc_location = state.get("toc_location") or ""
    if not toc_location or not os.path.exists(toc_location):
        logger.warning("TOC location missing or file not found, re-running toc_agent")
        return "toc_agent"
    try:
        content = read_file_content(toc_location)
        # Get validate_yaml from ToolRegistry
        validate_yaml = ToolRegistry.get('validate_yaml')
        if validate_yaml(content):
            logger.info("TOC YAML validated successfully, proceeding to chapter_agent_parallel")
            return "chapter_agent_parallel"
        else:
            logger.warning("TOC YAML validation failed, re-running toc_agent")
    except Exception as e:
        logger.warning("Failed to read or validate TOC YAML: %s, re-running toc_agent", e)
    return "toc_agent"


# Register workflow functions from ToolRegistry
WorkflowRegistry.register("toc_agent", toc_agent)
WorkflowRegistry.register("chapter_agent_parallel", chapter_agent_parallel)
WorkflowRegistry.register("collation_agent", collation_agent)
WorkflowRegistry.register("route_after_toc", route_after_toc)

graph = WorkflowFactory.compile_from_yaml(
        'configs/agents/book_workflow.yaml',
        BookAgentState
    )


AGENT_VERSION = "v0.1"
RELEASE_DATE = "2026-03-15"
AGENT_NAME = f"Book Agent {AGENT_VERSION} ({RELEASE_DATE})"

async def main():
    print("------------------------------------------------")
    print(f"{AGENT_NAME}")
    print("------------------------------------------------")

    while True:
        input_topic = input(f"[{AGENT_NAME}] Enter the topic for the book or 'exit' to quit: ")
        if input_topic.lower() == "exit":
            break

        initial_state: BookAgentState = {
            "agent_output": {},
            "topic_description": input_topic,
            "toc_location": "",
            "chapter_locations": [],
            "reasoning_steps": [],
            "final_content": ""
        }

        print(f"[{AGENT_NAME}] Creating the book...")

        final_state = await graph.ainvoke(initial_state)
        print("------------------------------------------------")
        print("Final Content:", final_state["final_content"])
        print("------------------------------------------------")
        print("TOC Location:", final_state["toc_location"])
        print("------------------------------------------------")
        print("Chapter Locations:", final_state["chapter_locations"])
        print("------------------------------------------------")
        print("Reasoning Steps:")
        for step in final_state["reasoning_steps"]:
            print(step)
        print("------------------------------------------------")

        print(f"[{AGENT_NAME}] Book created successfully.")
        print("------------------------------------------------")

if __name__ == "__main__":
    asyncio.run(main())
