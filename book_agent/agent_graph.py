from typing import Literal
from utils.read_file import read_file_content
from dotenv import load_dotenv
import logging
import asyncio
import os
from declarative_agent_sdk.workflow_registry import WorkflowRegistry
from declarative_agent_sdk.workflow_factory import WorkflowFactory
from declarative_agent_sdk.skill_registry import SkillRegistry
from toc_agent.agent import toc_agent
from chapter_agent.agent import chapter_agent_parallel
from collation_agent.agent import collation_agent
from skills.toc.scripts.validate_yaml import validate_yaml
from declarative_agent_sdk import AIWorkflowServer
from declarative_agent_sdk import AgentState


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

PORT=10004

# Register all skills at startup
SkillRegistry.register_all_from_directory()

def route_after_toc(state: AgentState) -> Literal["chapter_agent_parallel", "toc_agent"]:
    """If TOC YAML is valid, proceed to chapters; otherwise retry toc_agent."""    
    logger.info(f"state in router: {state}")
    toc_location = state.get("agents_output", {}).get("toc_agent", "")
    assert isinstance(toc_location, str), "Expected agent output 'toc_agent' to be a string"

    logger.info(f"Routing after TOC agent. TOC location: {toc_location}")
    if not toc_location or not os.path.exists(toc_location):
        logger.warning("TOC location missing or file not found, re-running toc_agent")
        return "toc_agent"
    try:
        content = read_file_content(toc_location)
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

workflow = WorkflowFactory.from_yaml_file(
        'configs/agents/book_workflow.yaml',
        AgentState
    )

AGENT_VERSION = "v0.1"
RELEASE_DATE = "2026-03-15"
AGENT_NAME = f"Book Agent {AGENT_VERSION} ({RELEASE_DATE})"

async def run_once():
    print("------------------------------------------------")
    print(f"{AGENT_NAME}")
    print("------------------------------------------------")

    while True:
        input_topic = input(f"[{AGENT_NAME}] Enter the topic for the book or 'exit' to quit: ")
        if input_topic.lower() == "exit":
            break

        print(f"[{AGENT_NAME}] Creating the book...")
        initial_state: AgentState = {
            "user_query": input_topic,
            "agents_output": {},
            "final_answer": ""
        }

        graph = workflow.compile()

        final_state = await graph.ainvoke(initial_state)
        print("------------------------------------------------")
        print("Final Content:", final_state["final_answer"])
        print("------------------------------------------------")
        print("TOC Location:", final_state.get("agents_output", {}).get("toc_agent", ""))
        print("------------------------------------------------")
        print("Chapter Locations:", final_state.get("agents_output", {}).get("chapter_agent", []))
        print("------------------------------------------------")
        print("Reasoning Steps:")
        for step in final_state.get("reasoning_steps", []):
            print(step)
        print("------------------------------------------------")

        print(f"[{AGENT_NAME}] Book created successfully.")
        print("------------------------------------------------")


def run_server():
    graph = workflow.compile()
    server = AIWorkflowServer(workflow, graph, host="0.0.0.0", port=PORT)
    logger.info("Book agent server initialized.")
    server.run()


if __name__ == "__main__":
    # asyncio.run(run_once())
    run_server()
