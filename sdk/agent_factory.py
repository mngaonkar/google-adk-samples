"""
Agent Factory - Create AIAgent instances from YAML configuration files.

This module provides a factory pattern to instantiate AIAgent objects
from YAML definitions, making agent configuration more maintainable
and declarative.
"""

import yaml
from typing import Any, Dict, List, Optional
from pathlib import Path
from sdk.ai_agent import AIAgent
from sdk.constants import DEFAULT_MODEL
from sdk.tool_registry import ToolRegistry
from sdk.model_factory import ModelFactory
from sdk.logging_config import get_logger

logger = get_logger(__name__)


class AgentFactory:
    """Factory class to create AIAgent instances from YAML configuration."""
    
    @staticmethod
    def from_yaml_file(yaml_file_path: str) -> AIAgent:
        """
        Create an AIAgent from a YAML configuration file.
        
        Args:
            yaml_file_path: Path to the YAML configuration file
            
        Returns:
            AIAgent instance configured according to the YAML file
            
        Example YAML format (Google Gemini):
            name: toc_agent
            description: An agent to create a table of contents for a book
            instruction_file: toc_agent/SKILL.md
            skills:
              - skills/toc
              - skills/chapter
            tools:
              - google_search
              - toc_validate_yaml  # Auto-discovered from skills/toc/scripts
            output_key: toc_agent_response
            model: gemini-2.0-flash-exp  # optional, defaults to DEFAULT_MODEL
            
        Example YAML format (vLLM):
            name: vllm_agent
            description: Agent using local vLLM server
            instruction_file: agent/instructions.md
            model: Qwen/Qwen3-4B-Thinking-2507-FP8
            provider: vllm
            endpoint:
              url: http://10.0.0.147:8000/v1
        """
        yaml_path = Path(yaml_file_path)
        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_file_path}")
        
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        
        return AgentFactory.from_dict(config)
    
    @staticmethod
    def from_dict(config: Dict[str, Any]) -> AIAgent:
        """
        Create an AIAgent from a configuration dictionary.
        
        Args:
            config: Dictionary containing agent configuration
                   Required: name, instruction_file
                   Optional: description, skills, tools, output_key, model, 
                            provider, endpoint
            
        Returns:
            AIAgent instance configured according to the dictionary
        """
        # Extract required fields
        name = config.get('name')
        if not name:
            raise ValueError("Agent 'name' is required in configuration")
        
        instruction_file = config.get('instruction_file')
        if not instruction_file:
            logger.warning(f"Agent '{name}' has no instruction_file specified, will use instruction from skills if available")
        
        # Extract optional fields with defaults
        description = config.get('description', '')
        output_key = config.get('output_key', None)
        model_name = config.get('model', DEFAULT_MODEL)
        skills = config.get('skills', None)
        provider = config.get('provider', None)
        endpoint_config = config.get('endpoint', None)
        
        # Extract endpoint URL if endpoint configuration exists
        endpoint_url = None
        if endpoint_config and isinstance(endpoint_config, dict):
            endpoint_url = endpoint_config.get('url')
        
        # Create model object using ModelFactory
        model = ModelFactory.create_model(
            model_name=model_name,
            provider=provider,
            endpoint_url=endpoint_url
        )
        logger.debug(f"Created model for agent '{name}': {model}")
        
        # Process tools - tool names can be resolved from global registry or instance registry
        # Instance registry automatically discovers from skills directories
        tool_names = config.get('tools', [])
        tools = []
        if tool_names:
            try:
                tools = ToolRegistry.get_multiple(tool_names)
            except ValueError as e:
                # It's okay if tools aren't in global registry - they may be auto-discovered from skills
                logger.info(f"Some tools for agent '{name}' will be resolved from skills: {e}")
                # Pass tool names as-is and let AIAgent resolve from its instance registry
                tools = tool_names
        
        # Create and return the agent
        logger.info(f"Creating agent '{name}' from configuration")
        agent = AIAgent(
            name=name,
            description=description,
            instruction_file=instruction_file if instruction_file is not None else '',
            tools=tools,
            output_key=output_key,
            model=model,
            skills=skills
        )
        
        return agent
    
    @staticmethod
    def from_yaml_string(yaml_string: str) -> AIAgent:
        """
        Create an AIAgent from a YAML string.
        
        Args:
            yaml_string: YAML configuration as a string
            
        Returns:
            AIAgent instance configured according to the YAML string
        """
        config = yaml.safe_load(yaml_string)
        return AgentFactory.from_dict(config)

