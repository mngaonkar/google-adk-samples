from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Literal
from agent_state import AgentState
from toc_agent.agent import toc_agent
from toc_agent.scripts.validate_yaml import validate_yaml
from chapter_agent.agent import chapter_agent_parallel
from collation_agent.agent import collation_agent
from utils.read_file import read_file_content
from dotenv import load_dotenv
import logging
import asyncio
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

def route_after_toc(state: AgentState) -> Literal["chapter_agent_parallel", "toc_agent"]:
    """If TOC YAML is valid, proceed to chapters; otherwise retry toc_agent."""
    toc_location = state.get("toc_location") or ""
    if not toc_location or not os.path.exists(toc_location):
        logger.warning("TOC location missing or file not found, re-running toc_agent")
        return "toc_agent"
    try:
        content = read_file_content(toc_location)
        if validate_yaml(content):
            return "chapter_agent_parallel"
    except Exception as e:
        logger.warning("Failed to read or validate TOC YAML: %s, re-running toc_agent", e)
    return "toc_agent"


workflow = StateGraph(AgentState)

workflow.add_node("toc_agent", toc_agent)
workflow.add_node("chapter_agent_parallel", chapter_agent_parallel)
workflow.add_node("collation_agent", collation_agent)
workflow.add_edge(START, "toc_agent")
workflow.add_conditional_edges("toc_agent", route_after_toc)
workflow.add_edge("chapter_agent_parallel", "collation_agent")
workflow.add_edge("collation_agent", END)

graph = workflow.compile()

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

        initial_state: AgentState = {
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
