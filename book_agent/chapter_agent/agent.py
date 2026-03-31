from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.genai.types import ThinkingConfig, GenerateContentConfig
from dotenv import load_dotenv
from google.adk.tools import google_search
from google.adk.planners import PlanReActPlanner
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.agents.sequential_agent import SequentialAgent
import os
import asyncio
import uuid
import logging
from utils.read_file import read_file_content
from agent_state import BookAgentState
from declarative_agent_sdk import AIAgent
from declarative_agent_sdk.utils import save_to_file
from declarative_agent_sdk.agent_factory import AgentFactory
from declarative_agent_sdk.agent_registry import AgentRegistry
from declarative_agent_sdk.utils import remove_think_content

logger = logging.getLogger(__name__)

AGENT_NAME = "chapter_agent"
INSTRUCTION_FILE_PATH = AGENT_NAME + "/SKILL.md"

def create_chapter_agent(name: str) -> AIAgent:
    agent = AgentFactory.from_yaml_file('chapter_agent/configs/chapter_agent.yaml')
    AgentRegistry.register(agent, category='chapter')
    logger.info(f"Chapter agent '{name}' created from YAML config.")

    return agent


async def chapter_agent_parallel(state: BookAgentState) -> None:
    """Process all chapters in parallel using async."""
    toc_file = state["agent_output"].get("toc_agent", "")
    assert toc_file, "TOC file location missing in state['agent_output']['toc_agent']"

    toc_content = read_file_content(toc_file)
    logger.info(f"Read TOC content from {toc_file} ({len(toc_content)} characters)")

    # Parse YAML file to get chapter titles
    import yaml
    toc_data = yaml.safe_load(toc_content)
    chapter_titles = toc_data.get("chapters", [])
    logger.info(f"Extracted {len(chapter_titles)} chapter titles from TOC")
    
    async def process_chapter(i: int, chapter: dict) -> tuple[int, str]:
        """Process a single chapter and return its index and file location."""
        logger.info(f"Processing chapter {i}: {chapter}")
        chapter_agent = create_chapter_agent(name=f"chapter_agent_{i}")

        # Read subtopics
        subtopics = chapter.get("subtopics", [])
        subtopic_text = "\n".join(subtopics)
        logger.info(f"Subtopics for chapter {i}: {len(subtopic_text)} characters")
        
        # Run agent asynchronously
        user_prompt = f"title = {chapter.get('title')}\n subtopics = {subtopics}"

        result = await chapter_agent.run(user_prompt)
        chapter_response = result.get("final_response", "")
        chapter_response = remove_think_content(chapter_response)
        logger.info(f"Chapter agent response for '{chapter.get('title')}' received ({len(chapter_response)} characters)")
        
        # Save chapter content
        chapter_file = f"workspace/chapter_{i}_content.md"
        save_to_file(chapter_response, chapter_file)
        logger.info(f"Chapter {i} response saved to {chapter_file}")
        
        return i, chapter_file
    
    # Create tasks for all chapters
    tasks = [
        process_chapter(i, chapter) 
        for i, chapter in enumerate(chapter_titles, start=1)
    ]
    
    # Run all chapters in parallel
    logger.info(f"Starting parallel processing of {len(tasks)} chapters...")
    results = await asyncio.gather(*tasks)
    
    # Sort results by chapter index and store locations
    results.sort(key=lambda x: x[0])
    state["chapter_locations"].extend([file_path for _, file_path in results])
    logger.info(f"All {len(results)} chapters processed successfully") 
