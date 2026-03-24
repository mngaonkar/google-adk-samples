"""
Register Skills - Central location for registering all agent skills.

This module provides a convenience wrapper around SkillRegistry.register_all_from_directory()
for backward compatibility. New code should import directly from SDK:

    from sdk import SkillRegistry
    SkillRegistry.register_all_from_directory('skills/')
"""

import logging
from sdk.skill_registry import SkillRegistry
from sdk.tool_registry import ToolRegistry
from sdk.constants import SKILLS_DIRECTORY

logger = logging.getLogger(__name__)


def register_all_skills(skills_directory: str = SKILLS_DIRECTORY) -> None:
    """
    Register all available skills in the SkillRegistry and their tools in ToolRegistry.
    
    This is a convenience wrapper around SkillRegistry.register_all_from_directory().
    See SDK documentation for details.
    
    Args:
        skills_directory: Base directory for skill folders (default from constants)
    """
    SkillRegistry.register_all_from_directory(skills_directory)


def register_router_functions() -> None:
    """
    Register router functions in ToolRegistry.
    
    Router functions are used for conditional edges in workflows.
    """
    # Import locally to avoid circular dependencies
    from agent_graph import route_after_toc
    
    ToolRegistry.register('route_after_toc', route_after_toc)
    
    logger.info("✓ Registered router functions in ToolRegistry")


# Auto-register when module is imported
# Commented out to allow manual control - uncomment if you want auto-registration
# register_all_skills()
