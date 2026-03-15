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
from settings import GEMINI_MODEL
from utils.read_file import read_file_content
from agent_state import AgentState
from sdk.ai_agent import AIAgent
from sdk.utils import save_to_file

logger = logging.getLogger(__name__)

INSTRUCTION_FILE_PATH = "chapter_agent/prompts/instructions.md"

def create_chapter_agent(name: str) -> AIAgent:
    return AIAgent(
        name=name,
        description='An agent to create chapter content for a book based on subtopics provided for the chapter.',
        instruction_file=INSTRUCTION_FILE_PATH,
        tools=[google_search],
        output_key="chapter_agent_response",
        model=GEMINI_MODEL
    )

async def chapter_agent_parallel(state: AgentState) -> None:
    """Process all chapters in parallel using async."""
    toc_file = state["toc_location"]
    toc_content = read_file_content(toc_file)
    logger.info(f"Read TOC content from {toc_file} ({len(toc_content)} characters)")

    # Parse YAML file to get chapter titles
    import yaml
    toc_data = yaml.safe_load(toc_content)
    chapter_titles = toc_data.get("chapters", [])
    logger.info(f"Extracted {len(chapter_titles)} chapter titles from TOC")
    
    async def process_chapter(i: int, title: dict) -> tuple[int, str]:
        """Process a single chapter and return its index and file location."""
        logger.info(f"Processing chapter {i}: {title}")
        chapter_agent = create_chapter_agent(name=f"chapter_agent_{i}")

        # Read subtopics
        subtopics = title.get("subtopics", [])
        subtopic_text = "\n".join(subtopics)
        logger.info(f"Subtopics for chapter {i}: {len(subtopic_text)} characters")
        
        # Run agent asynchronously
        result = await chapter_agent.run(subtopic_text)
        chapter_response = result.get("final_response", "")
        logger.info(f"Chapter agent response for '{title}' received ({len(chapter_response)} characters)")
        
        # Save chapter content
        chapter_file = f"file_system/chapter_{i}_content.md"
        save_to_file(chapter_response, chapter_file)
        logger.info(f"Chapter {i} response saved to {chapter_file}")
        
        return i, chapter_file
    
    # Create tasks for all chapters
    tasks = [
        process_chapter(i, title) 
        for i, title in enumerate(chapter_titles, start=1)
    ]
    
    # Run all chapters in parallel
    logger.info(f"Starting parallel processing of {len(tasks)} chapters...")
    results = await asyncio.gather(*tasks)
    
    # Sort results by chapter index and store locations
    results.sort(key=lambda x: x[0])
    state["chapter_locations"].extend([file_path for _, file_path in results])
    logger.info(f"All {len(results)} chapters processed successfully") 
