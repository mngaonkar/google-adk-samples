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
from declarative_agent_sdk.ai_agent import AIAgent
from agent_state import BookAgentState
from declarative_agent_sdk.utils import save_to_file
from declarative_agent_sdk.agent_factory import AgentFactory
from declarative_agent_sdk.constants import WORKSPACE_DIRECTORY
from utils.remove_think_content import remove_think_content

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

agent = AgentFactory.from_yaml_file('toc_agent/configs/toc_agent.yaml')

logger.info("Table of Contents agent initialized.")

def toc_agent(state: BookAgentState) -> BookAgentState:
    result = agent.run_sync(state["topic_description"])
    logger.debug(f"TOC agent generated response: {result}")
    agent_output_file = os.path.join(WORKSPACE_DIRECTORY, agent.name)

    reponse = result.get("final_response", "")
    response = remove_think_content(reponse)
    save_to_file(response, agent_output_file)
    logger.info(f"TOC agent response saved to {agent_output_file}")
    state["toc_location"] = agent_output_file
    state["agent_output"][agent.name] = agent_output_file

    return state
