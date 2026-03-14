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

from tools import addition_tool
from settings import GEMINI_MODEL, INSTRUCTION_FILE_PATH
from toc_agent.agent import toc_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_instructions() -> str:
    if os.path.exists(INSTRUCTION_FILE_PATH):
        instruction_text = open(INSTRUCTION_FILE_PATH).read()
    else:
        raise FileNotFoundError(f"Instructions file not found at {INSTRUCTION_FILE_PATH}")
    return instruction_text

thinking_config = ThinkingConfig(
    include_thoughts=True,
    thinking_budget=256 # 256 tokens thinking budget
)

planner = PlanReActPlanner()

root_agent = SequentialAgent(
    name='root_agent',
    description='Agent to create a book on user provided topic.',
    sub_agents=[toc_agent]
)
logger.info("Root agent initialized.")

async def main():
    load_dotenv()
    session_service = InMemorySessionService()
    session_id = uuid.uuid4().hex

    await session_service.create_session(
        app_name="book_agent_app",
        user_id="user123",
        session_id=session_id,
    )

    runner = Runner(agent=root_agent, 
                    app_name="book_agent_app",
                    session_service=session_service)
    
    content = types.Content(
        role="user",
        parts=[
            types.Part(text="Create a book on quantum computing")]
    )
    final_response = ""

    async for event in runner.run_async(
        user_id="user123",
        session_id=session_id,
        new_message=content 
    ):
        print(f"RESPONSE: {event.content.parts}")
        if event.is_final_response():
            final_response = event.content.parts[0].text if event.content and event.content.parts else ""
            break
    
    print(f"FINAL RESPONSE: {final_response}")

if __name__ == "__main__":
    asyncio.run(main())