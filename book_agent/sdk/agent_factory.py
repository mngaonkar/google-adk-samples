"""
Agent Factory - Create AIAgent instances from YAML configuration files.

This module provides a factory pattern to instantiate AIAgent objects
from YAML definitions, making agent configuration more maintainable
and declarative.
"""

import yaml
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path
from sdk.ai_agent import AIAgent
from sdk.constants import GEMINI_MODEL
from sdk.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


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
            
        Example YAML format:
            name: toc_agent
            description: An agent to create a table of contents for a book
            instruction_file: toc_agent/SKILL.md
            tools:
              - google_search
            output_key: toc_agent_response
            model: gemini-2.0-flash-exp  # optional, defaults to GEMINI_MODEL
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
            
        Returns:
            AIAgent instance configured according to the dictionary
        """
        # Extract required fields
        name = config.get('name')
        if not name:
            raise ValueError("Agent 'name' is required in configuration")
        
        instruction_file = config.get('instruction_file')
        if not instruction_file:
            raise ValueError("Agent 'instruction_file' is required in configuration")
        
        # Extract optional fields with defaults
        description = config.get('description', '')
        output_key = config.get('output_key', None)
        model = config.get('model', GEMINI_MODEL)
        
        # Process tools
        tool_names = config.get('tools', [])
        tools = []
        if tool_names:
            try:
                tools = ToolRegistry.get_multiple(tool_names)
            except ValueError as e:
                logger.error(f"Error resolving tools for agent '{name}': {e}")
                raise
        
        # Create and return the agent
        logger.info(f"Creating agent '{name}' from configuration")
        agent = AIAgent(
            name=name,
            description=description,
            instruction_file=instruction_file,
            tools=tools,
            output_key=output_key,
            model=model
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

