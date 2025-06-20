# Make sure the google-adk package is installed and the import path is correct.
# If the package is not installed, run: pip install google-adk

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv
import os
import asyncio
import uuid
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

APP_NAME = "lite_llm_app"
USER_ID = "user123"

async def run_async_query(query: str, runner: Runner, user_id: str, session_id: str) -> str:
    """Run an asynchronous query using the LiteLLM agent."""
    content = types.Content(
        role="user",
        parts=[
            types.Part(text=query)]
    )
    final_response = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                text = event.content.parts[0].text
                final_response = isinstance(text, str) and text or ""
            elif event.actions and event.actions.escalate:
                final_response = "Escalation required."
            break

    return final_response

async def main():
    load_dotenv()

    agent = Agent(
        name=APP_NAME,
        description="A simple agent that uses LiteLLM for basic tasks.",
        model=os.getenv("MODEL_NAME"),
        instruction="Perform basic tasks using LiteLLM.",
        tools=[]  # Add any tools if needed
    )

    logger.info("Agent initialized with the following configuration:")
    logger.info(f"Name: {agent.name}")

    session_service = InMemorySessionService()

    # Create session
    session_id = uuid.uuid4().hex
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )
    logger.info(f"Created session with ID: {session_id}")

    # Create a runner
    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service
    )

    # Run the agent
    response = await run_async_query(
        query="What is the capital of USA?",
        runner=runner,
        user_id=USER_ID,
        session_id=session_id
    )
    logger.info(f"Response from agent: {response}")

if __name__ == "__main__":
    asyncio.run(main())