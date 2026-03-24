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
from sdk.ai_agent import AIAgent
from agent_state import AgentState
from sdk.utils import save_to_file
from sdk.agent_factory import AgentFactory

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

AGENT_NAME = "toc_agent"
INSTRUCTION_FILE_PATH = AGENT_NAME + "/SKILL.md"
TOC_OUTPUT_FILE = "workspace/toc_response.yaml"
OUTPUT_KEY = "toc_agent_response"

agent = AgentFactory.from_yaml_file('toc_agent/configs/toc_agent.yaml')

logger.info("Table of Contents agent initialized.")

def toc_agent(state: AgentState) -> AgentState:
    result = agent.run_sync(state["topic_description"])
    logger.debug(f"TOC agent generated response: {result}")
    save_to_file(result["final_response"], TOC_OUTPUT_FILE)
    logger.info(f"TOC agent response saved to {TOC_OUTPUT_FILE}")
    state["toc_location"] = TOC_OUTPUT_FILE

    return state
