from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents.base_agent import BaseAgent
from google.genai import types
from sdk.utils import read_from_file
from sdk.constants import GEMINI_MODEL
import asyncio
import uuid
import logging
from typing import Optional, Any
from pydantic import Field

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIAgent(Agent):
    """Extended Agent with convenient initialization and run methods."""
    instruction_file: str = Field(default="", exclude=True)
    input_key_map: dict[str, str] = Field(default_factory=dict, exclude=True)
   
    def __init__(self, 
                 name: str, 
                 instruction_file: str,
                 description: str = '',
                 tools: list | None = None, 
                 input_key_map: dict[str, str] | None = None,
                 output_key: str | None = None,
                 model: str = GEMINI_MODEL):

        instruction_text = read_from_file(instruction_file) if instruction_file else ''
        tools = tools or []
        
        super().__init__(
            model=model,
            name=name,
            description=description,
            instruction=instruction_text,
            tools=tools,
            output_key=output_key
        )
        
        # Set custom fields AFTER parent initialization
        object.__setattr__(self, 'instruction_file', instruction_file)
        object.__setattr__(self, 'input_key_map', input_key_map or {})

    async def run(self, 
                  input_text: str, 
                  app_name: Optional[str] = None, 
                  user_id: str = "user123") -> dict[str, Any]:
        """
        Run the agent with the given input.
        
        Args:
            input_text: The input query or prompt for the agent
            app_name: Optional app name (defaults to agent name)
            user_id: Optional user ID (defaults to "user123")
            
        Returns:
            Dictionary containing:
                - final_response: The agent's final response text
                - session_id: The session ID used
                - output_key_data: Data stored in output_key (if configured)
        """
        app_name = app_name or self.name
        session_service = InMemorySessionService()
        session_id = uuid.uuid4().hex
        
        # Create session
        await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )
        
        # Create runner
        runner = Runner(
            agent=self,
            app_name=app_name,
            session_service=session_service
        )
        
        # Create content message
        content = types.Content(
            role="user",
            parts=[types.Part(text=input_text)]
        )
        
        final_response = ""
        
        # Run async loop
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            logger.info(f"EVENT: {event}")
            
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text
                break
        
        # Get output_key data if configured
        output_key_data = None
        if self.output_key:
            session = await session_service.get_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id
            )
            if session:
                output_key_data = session.state.get(self.output_key)
        
        return {
            "final_response": final_response,
            "session_id": session_id,
            "output_key_data": output_key_data
        }
    
    def run_sync(self, 
                 input_text: str, 
                 app_name: Optional[str] = None, 
                 user_id: str = "user123") -> dict[str, Any]:
        """
        Synchronous wrapper for the run method.
        
        Args:
            input_text: The input query or prompt for the agent
            app_name: Optional app name (defaults to agent name)
            user_id: Optional user ID (defaults to "user123")
            
        Returns:
            Dictionary containing final_response, session_id, and output_key_data
        """
        return asyncio.run(self.run(input_text, app_name, user_id))
