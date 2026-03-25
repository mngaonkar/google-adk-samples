from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents.base_agent import BaseAgent
from google.genai import types
from declarative_agent_sdk.utils import read_from_file
from declarative_agent_sdk.constants import DEFAULT_MODEL, MAX_REMOTE_CALLS, SKILLS_DIRECTORY
from declarative_agent_sdk.logging_config import get_logger
from declarative_agent_sdk.token_utils import fit_to_context_window
import asyncio
import uuid
import os
from typing import Optional, Any, Union, List
from pydantic import Field
import json

logger = get_logger(__name__)

class AIAgent(Agent):
    """Extended Agent with convenient initialization and run methods."""
    instruction_file: str = Field(default="", exclude=True)
    input_key_map: dict[str, str] = Field(default_factory=dict, exclude=True)
    tool_registry: Any = Field(default=None, exclude=True)
    context_window: Optional[int] = Field(default=None, exclude=True)
    max_output_tokens: Optional[int] = Field(default=None, exclude=True)
    enable_truncation: bool = Field(default=False, exclude=True)
    truncate_strategy: str = Field(default="end", exclude=True)
    safety_margin: int = Field(default=100, exclude=True)
   
    def __init__(self, 
                 name: str, 
                 instruction_file: str,
                 description: str = '',
                 tools: list | None = None, 
                 skills: List[str] | None = None,
                 input_key_map: dict[str, str] | None = None,
                 output_key: str | None = None,
                 model: Union[str, Any] = DEFAULT_MODEL,
                 context_window: Optional[int] = None,
                 max_output_tokens: Optional[int] = None,
                 enable_truncation: bool = False,
                 truncate_strategy: str = "end",
                 safety_margin: int = 100):
        """
        Initialize the AI Agent with tools, skills, and instructions.
        
        Args:
            name: Agent name (used for identification and logging)
            instruction_file: Path to the main instruction file (markdown format)
            description: Brief description of the agent's purpose
            tools: List of tool names (strings) or tool objects to provide to the agent
            skills: List of skill directory names to auto-discover tools from.
                   Each skill directory should contain:
                   - SKILL.md: Instructions to append to agent's instruction text
                   - scripts/: Folder with Python scripts to register as tools
            input_key_map: Optional mapping of input keys for data transformation
            output_key: Optional key where agent stores structured output in session state
            model: Model name (string) or model object (defaults to DEFAULT_MODEL from constants)
            context_window: Total context window size in tokens (e.g., 20384 for Qwen3-4B)
            max_output_tokens: Tokens reserved for output generation
            enable_truncation: If True, automatically truncate inputs exceeding context window
            truncate_strategy: How to truncate ("start", "end", or "middle")
            safety_margin: Extra tokens to reserve for safety (default: 100)
        
        Workflow:
            1. Reads instruction text from instruction_file
            2. Creates instance-specific tool registry
            3. For each skill directory:
               - Appends SKILL.md content to instructions
               - Auto-discovers and registers tools from scripts/ folder
            4. Resolves tool names to tool objects
            5. Configures automatic function calling with MAX_REMOTE_CALLS limit
            6. Initializes parent Agent class with all configuration
        """
        # Read main instruction file
        # Read main instruction file
        instruction_text = read_from_file(instruction_file) if instruction_file else ''
        
        # Create instance-level tool registry (isolated from global registry)
        # This ensures each agent has its own set of tools without conflicts
        from declarative_agent_sdk.tool_registry import ToolRegistry
        instance_registry = type('InstanceToolRegistry', (ToolRegistry,), {
            '_tools': {},  # Instance-specific tools dict
        })
        
        # Auto-discover tools from skills directories and append SKILL.md content
        if skills:
            for skill_dir in skills:
                skill_dir = os.path.join(SKILLS_DIRECTORY, skill_dir)
                if not os.path.exists(skill_dir):
                    raise FileNotFoundError(f"Skill directory not found: {skill_dir}")
                
                # Append SKILL.md content to instruction text
                # This provides domain-specific knowledge to the agent
                skill_md_path = os.path.join(skill_dir, 'SKILL.md')
                if os.path.exists(skill_md_path):
                    skill_instruction = read_from_file(skill_md_path)
                    instruction_text += f"\n\n# Skill: {os.path.basename(skill_dir)}\n{skill_instruction}"
                    logger.info(f"Appended SKILL.md from {skill_dir}")

                # Auto-discover and register tools from scripts/ folder
                scripts_dir = os.path.join(skill_dir, 'scripts')
                if os.path.exists(scripts_dir):
                    count = instance_registry.register_from_scripts_folder(
                        scripts_dir,
                        prefix=""
                    )
                    logger.info(f"Auto-discovered {count} tools from {scripts_dir}")
        
        # Resolve tool names from YAML to actual tool objects
        # Tools can be specified as strings (tool names) or tool objects
        resolved_tools = []
        if tools:
            for tool_item in tools:
                if isinstance(tool_item, str):
                    # Tool name - resolve from instance registry
                    try:
                        resolved_tools.append(instance_registry.get(tool_item))
                    except ValueError:
                        logger.warning(f"Tool '{tool_item}' not found in instance registry, skipping")
                else:
                    # Already a tool object
                    resolved_tools.append(tool_item)
        
        tools = resolved_tools
        
        # Define automatic function calling config
        # Controls how many rounds of tool calls the agent can make
        afc_config = types.AutomaticFunctionCallingConfig(
            maximum_remote_calls=MAX_REMOTE_CALLS,  # e.g., limit to 5 rounds of tool calls (default is 10)
            # disable=True,          # Optional: fully disable auto-loop if needed
        )

        # Validate that we have instruction text
        # Either from instruction_file or from SKILL.md files
        if not instruction_text:
            raise ValueError("Agent does not have any instruction text. Please provide an instruction_file or ensure SKILL.md files are included in skills directories.")
        
        # Initialize parent Agent class with all configuration
        super().__init__(
            model=model,
            name=name,
            description=description,
            instruction=instruction_text,
            tools=resolved_tools,
            generate_content_config=types.GenerateContentConfig(
                automatic_function_calling=afc_config,
                # Add other Gemini configs if needed: temperature=0.7, max_output_tokens=2048, etc.
            ),
            output_key=output_key
        )
        
        # Set custom fields AFTER parent initialization
        # These are excluded from Pydantic model but stored on the instance
        object.__setattr__(self, 'instruction_file', instruction_file)
        object.__setattr__(self, 'input_key_map', input_key_map or {})
        object.__setattr__(self, 'tool_registry', instance_registry)
        object.__setattr__(self, 'context_window', context_window)
        object.__setattr__(self, 'max_output_tokens', max_output_tokens)
        object.__setattr__(self, 'enable_truncation', enable_truncation)
        object.__setattr__(self, 'truncate_strategy', truncate_strategy)
        object.__setattr__(self, 'safety_margin', safety_margin)

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
        
        # Apply token truncation if configured
        processed_input = input_text
        if self.enable_truncation and self.context_window and self.max_output_tokens:
            logger.info(f"Token truncation enabled for agent '{self.name}'")
            processed_input = fit_to_context_window(
                input_text=input_text,
                max_context_tokens=self.context_window,
                max_output_tokens=self.max_output_tokens,
                model="gpt-4",  # For tokenization
                safety_margin=self.safety_margin,
                truncate_strategy=self.truncate_strategy
            )
        
        # Create content message
        content = types.Content(
            role="user",
            parts=[types.Part(text=processed_input)]
        )
        
        final_response = ""
        
        # Run async loop
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if event.content and event.content.parts:
                if hasattr(event.content.parts[0], 'text'):
                    logger.info(f"EVENT: {event.content.parts[0].text}")
                elif hasattr(event.content.parts[0], 'function_call'):
                    logger.info(f"EVENT: Function call - {event.content.parts[0].function_call}")
                elif hasattr(event.content.parts[0], 'function_response'):
                    logger.info(f"EVENT: Function response - {event.content.parts[0].function_response.name}")
                else:
                    logger.info(f"EVENT: Received content part with unrecognized format: {event.content.parts[0]}")

            
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
