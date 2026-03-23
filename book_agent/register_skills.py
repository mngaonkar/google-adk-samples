"""
Register Skills - Central location for registering all agent skills.

This module registers all available skills/sub-agents in the SkillRegistry
and their associated tools/functions in the ToolRegistry.

SkillRegistry stores skill metadata and directory locations.
ToolRegistry auto-discovers and stores all functions from skill scripts folders.

Import this module early in your application to ensure all skills are registered.
"""

import logging
import yaml
from sdk.skill_registry import SkillRegistry
from sdk.tool_registry import ToolRegistry
from sdk.constants import SKILLS_DIRECTORY
import os

logger = logging.getLogger(__name__)


def register_all_skills() -> None:
    """
    Register all available skills in the SkillRegistry and their tools in ToolRegistry.
    
    This function:
    1. Discovers skills from SKILL.md files in the skills directory
    2. Registers skill metadata in SkillRegistry (directory, description, category)
    3. Auto-discovers and registers all functions from scripts/ folders in ToolRegistry
    4. Manually registers known agent functions in ToolRegistry
    
    Call this function once at application startup to populate both registries.
    """
    logger.info("Registering all skills and tools...")
    
    # Import agent functions to register in ToolRegistry
    from toc_agent.agent import toc_agent
    from chapter_agent.agent import chapter_agent_parallel
    from collation_agent.agent import collation_agent
    
    # Traverse skill folder and register skills dynamically
    # Read SKILL.md file for name and description and register the skill along with skill folder location
    for root, dirs, files in os.walk(SKILLS_DIRECTORY):
        for dir in dirs:
            skill_dir_path = os.path.join(root, dir)
            skill_md_path = os.path.join(skill_dir_path, 'SKILL.md')
            
            if os.path.exists(skill_md_path):
                with open(skill_md_path, 'r') as f:
                    content = f.read()
                    
                    # Parse YAML frontmatter (between --- delimiters)
                    if content.startswith('---'):
                        parts = content.split('---', 2)
                        if len(parts) >= 3:
                            try:
                                # Parse the YAML frontmatter (parts[1])
                                frontmatter = yaml.safe_load(parts[1])
                                
                                skill_name = frontmatter.get('name')
                                skill_desc = frontmatter.get('description')
                                
                                if skill_name and skill_desc:
                                    # Register skill metadata in SkillRegistry
                                    SkillRegistry.register(
                                        skill_name,
                                        directory=skill_dir_path,
                                        description=skill_desc,
                                        category='agent'
                                    )
                                    logger.info(f"✓ Registered skill: {skill_name} (directory: {skill_dir_path})")
                                    
                                    # Auto-discover and register tools from scripts folder
                                    scripts_dir = os.path.join(skill_dir_path, 'scripts')
                                    if os.path.exists(scripts_dir):
                                        count = ToolRegistry.register_from_scripts_folder(
                                            scripts_dir, 
                                            prefix=f""
                                        )
                                        if count > 0:
                                            logger.info(f"  ✓ Registered {count} tools from {scripts_dir}")
                                else:
                                    logger.warning(f"SKILL.md at {skill_md_path} is missing 'name' or 'description' in YAML frontmatter.")
                            except yaml.YAMLError as e:
                                logger.error(f"✗ Failed to parse YAML frontmatter in {skill_md_path}: {e}")
                        else:
                            logger.warning(f"SKILL.md at {skill_md_path} doesn't have proper YAML frontmatter delimiters.")

    # Register agent skills in SkillRegistry (metadata only)
    # SkillRegistry.register(
    #     'toc_agent',
    #     directory='toc_agent',
    #     description='Generate table of contents from topic description',
    #     category='agent'
    # )
    
    # SkillRegistry.register(
    #     'chapter_agent_parallel',
    #     directory='chapter_agent',
    #     description='Generate all book chapters in parallel',
    #     category='agent'
    # )
    
    # SkillRegistry.register(
    #     'collation_agent',
    #     directory='collation_agent',
    #     description='Collate chapters into final PDF book',
    #     category='agent'
    # )
    
    # Register agent functions in ToolRegistry (callables)
    # ToolRegistry.register('toc_agent', toc_agent)
    # ToolRegistry.register('chapter_agent_parallel', chapter_agent_parallel)
    # ToolRegistry.register('collation_agent', collation_agent)
    
    # Auto-discover tools from agent scripts folders
    # for agent_dir in ['toc_agent', 'chapter_agent', 'collation_agent']:
    #     scripts_dir = os.path.join(agent_dir, 'scripts')
    #     if os.path.exists(scripts_dir):
    #         count = ToolRegistry.register_from_scripts_folder(scripts_dir)
    #         if count > 0:
    #             logger.info(f"✓ Registered {count} tools from {scripts_dir}")
    
    logger.info(f"✓ Registered {len(SkillRegistry.list_available())} skills in SkillRegistry")
    logger.info(f"✓ Registered {len(ToolRegistry.list_available())} tools in ToolRegistry")
    
    # Log by category
    by_category = SkillRegistry.list_by_category()
    for category, skills in by_category.items():
        logger.info(f"  {category}: {', '.join(skills)}")


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
