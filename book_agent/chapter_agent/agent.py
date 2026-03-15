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

logger = logging.getLogger(__name__)

INSTRUCTION_FILE_PATH = "chapter_agent/prompts/instructions.md"

def create_chapter_agent() -> Agent:
    instruction_text = read_file_content(INSTRUCTION_FILE_PATH)

    chapter_agent = Agent(
    model=GEMINI_MODEL,
    name='chapter_agent',
    description='A helpful assistant for user questions.',
    instruction=instruction_text,
    tools=[google_search],
    output_key="chapter_response"
    )

    return chapter_agent

agent = create_chapter_agent()
logger.info("Chapter agent initialized.")

def chapter_agent_parallel(state: AgentState) -> None:
    state["chapter_locations"] = ["file_system/chapter_response.md"]