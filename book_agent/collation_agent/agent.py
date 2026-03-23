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
from skills.collation.scripts.create_pdf_file import create_pdf_file
from sdk.tool_registry import ToolRegistry
from sdk.agent_factory import AgentFactory

logger = logging.getLogger(__name__)

AGENT_NAME = "collation_agent"
INSTRUCTION_FILE_PATH = AGENT_NAME + "/SKILL.md"
OUTPUT_PDF_LOCATION = "workspace/collation_response.pdf"

def create_collation_agent(name: str) -> AIAgent:
    ToolRegistry.register("create_pdf_file", create_pdf_file)
    agent = AgentFactory.from_yaml_file('collation_agent/configs/collation_agent.yaml')
    logger.info(f"Collation agent '{name}' created from YAML config.")

    return agent

agent = create_collation_agent("collation_agent")
logger.info("Collation agent initialized.")

def collation_agent(state: AgentState) -> AgentState:
    """Collate chapter content into a single PDF file."""
    chapter_locations = state["chapter_locations"]
    toc_location = state.get("toc_location", "")
    collation_agent = create_collation_agent(name="collation_agent")

    user_prompt = f"""Create a PDF book from the following inputs:
    - toc_location: Table of Contents location: {toc_location}
    - chapter_locations: Chapter markdown files: {chapter_locations}
    
    Use the create_pdf_file tool with both the chapter_locations list and toc_location."""
    
    result = collation_agent.run_sync(user_prompt)
    logger.info(f"Collation agent response: {result}")

    collation_response = result["final_response"]
    save_to_file(collation_response, OUTPUT_PDF_LOCATION)
    state["final_content"] = OUTPUT_PDF_LOCATION
    logger.info(f"Collation agent response saved to {OUTPUT_PDF_LOCATION}")

    return state