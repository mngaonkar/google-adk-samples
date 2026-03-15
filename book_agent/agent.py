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
from toc_agent.tools import save_toc_to_file

from tools import addition_tool
from settings import GEMINI_MODEL, INSTRUCTION_FILE_PATH
from toc_agent.agent import agent as toc_agent

# Configure logging with both console and file handlers
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# File handler
file_handler = logging.FileHandler(f"{log_dir}/book_agent.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler, file_handler]
)

logger = logging.getLogger(__name__)

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

    # Run the agent loop
    async for event in runner.run_async(
        user_id="user123",
        session_id=session_id,
        new_message=content 
    ):
        logger.info(f"RESPONSE: {event.author}")
        
        # Get response from event content directly
        if event.author == "toc_agent" and event.content and event.content.parts:
            toc_response = event.content.parts[0].text
            assert toc_response is not None, "TOC response is None"

            logger.info(f"TOC agent response received: {len(toc_response)} characters")
            save_toc_to_file(toc_response, "file_system/toc_response.md")

        if event.is_final_response():
            final_response = event.content.parts[0].text if event.content and event.content.parts else ""
            break
    
    logger.info(f"FINAL RESPONSE: {final_response}")
    
    # Access session state after the loop completes
    session = await session_service.get_session(
        app_name="book_agent_app",
        user_id="user123",
        session_id=session_id
    )
    toc_from_state = session.state.get('toc_agent_response')
    logger.info(f"TOC from session state: {toc_from_state is not None}")
    
    
    

if __name__ == "__main__":
    asyncio.run(main())