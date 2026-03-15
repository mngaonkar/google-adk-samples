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
from toc_agent.tools import save_toc_to_file

logger = logging.getLogger(__name__)

INSTRUCTION_FILE_PATH = "toc_agent/prompts/instructions.md"
OUTPUT_KEY = "toc_agent_response"

class TOCAgent(Agent):
    def __init__(self, name: str, 
                 description: str,  
                 instruction_file: str, 
                 tools: list,
                 output_key: str,
                 model: str = GEMINI_MODEL):
        instruction_text = read_file_content(instruction_file)

        super().__init__(
            model=model,
            name=name,
            description=description,
            instruction=instruction_text,
            tools=tools,
            output_key=output_key
        )

toc_agent = TOCAgent(
    name='toc_agent',
    description='An agent to create a table of contents for a book based on user provided topic.',
    model=GEMINI_MODEL,
    instruction_file=INSTRUCTION_FILE_PATH,
    tools=[google_search],
    output_key=OUTPUT_KEY
)
logger.info("Table of Contents agent initialized.")