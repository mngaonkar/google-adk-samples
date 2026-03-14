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

toc_agent = Agent(
    model=GEMINI_MODEL,
    name='toc_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    tools=[google_search],
    output_key="toc_response"
)