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
from sdk.ai_agent import AIAgent
from agent_state import AgentState
from sdk.utils import save_to_file

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

INSTRUCTION_FILE_PATH = "toc_agent/prompts/instructions.md"
TOC_OUTPUT_FILE = "file_system/toc_response.yaml"
OUTPUT_KEY = "toc_agent_response"

agent = AIAgent(
    name='toc_agent',
    description='An agent to create a table of contents for a book based on user provided topic.',
    instruction_file=INSTRUCTION_FILE_PATH,
    tools=[google_search],
    output_key=OUTPUT_KEY,
    model=GEMINI_MODEL
)
logger.info("Table of Contents agent initialized.")

def toc_agent(state: AgentState) -> AgentState:
    result = agent.run_sync(state["topic_description"])
    save_to_file(result["final_response"], TOC_OUTPUT_FILE)
    logger.info(f"TOC agent response saved to {TOC_OUTPUT_FILE}")
    state["toc_location"] = TOC_OUTPUT_FILE

    return state