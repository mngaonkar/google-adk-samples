from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv
import os
import asyncio
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_current_time():
    """Tool to get the current time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    tools=[get_current_time],
)

async def main():
    load_dotenv()
    session_service = InMemorySessionService()
    session_id = uuid.uuid4().hex

    await session_service.create_session(
        app_name="basic_agent_app",
        user_id="user123",
        session_id=session_id,
    )

    runner = Runner(agent=root_agent, 
                    app_name="basic_agent_app",
                    session_service=session_service)
    
    content = types.Content(
        role="user",
        parts=[
            types.Part(text="What is the current time?")]
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