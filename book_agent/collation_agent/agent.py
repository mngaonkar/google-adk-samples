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
from collation_agent.tools import create_pdf_file

logger = logging.getLogger(__name__)

INSTRUCTION_FILE_PATH = "collation_agent/prompts/instructions.md"
OUTPUT_PDF_LOCATION = "file_system/collation_response.pdf"

def create_collation_agent(name: str) -> AIAgent:
    return AIAgent(
        name=name,
        description='An agent to create single PDF file for a book based on chapter content provided for the book.',
        instruction_file=INSTRUCTION_FILE_PATH,
        tools=[create_pdf_file],
        output_key="collation_response",
        model=GEMINI_MODEL
    )

agent = create_collation_agent("collation_agent")
logger.info("Collation agent initialized.")

def collation_agent(state: AgentState) -> AgentState:
    """Collate chapter content into a single PDF file."""
    chapter_locations = state["chapter_locations"]
    collation_agent = create_collation_agent(name="collation_agent")

    user_prompt = f"Create a PDF book from the list of markdown files provided: {chapter_locations}"
    result = collation_agent.run_sync(user_prompt)
    logger.info(f"Collation agent response: {result}")

    collation_response = result["final_response"]
    save_to_file(collation_response, OUTPUT_PDF_LOCATION)
    state["collation_location"] = OUTPUT_PDF_LOCATION
    logger.info(f"Collation agent response saved to {OUTPUT_PDF_LOCATION}")

    return state