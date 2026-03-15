from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List
from agent_state import AgentState
from toc_agent.agent import toc_agent
from chapter_agent.agent import chapter_agent_parallel
from collation_agent.agent import collation_agent
from dotenv import load_dotenv
import logging
import asyncio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

workflow = StateGraph(AgentState)

workflow.add_node("toc_agent", toc_agent)
workflow.add_node("chapter_agent_parallel", chapter_agent_parallel)
workflow.add_node("collation_agent", collation_agent)
workflow.add_edge(START, "toc_agent")
workflow.add_edge("toc_agent", "chapter_agent_parallel")
workflow.add_edge("chapter_agent_parallel", "collation_agent")
workflow.add_edge("collation_agent", END)

graph = workflow.compile()

async def main():
    initial_state: AgentState = {
        "topic_description": "Write a book on quantum computing.",
        "toc_location": "",
        "chapter_locations": [],
        "reasoning_steps": [],
        "final_content": ""
    }

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

if __name__ == "__main__":
    asyncio.run(main())