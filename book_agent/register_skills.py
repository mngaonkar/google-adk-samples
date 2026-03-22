"""
Register Skills - Central location for registering all agent skills.

This module imports and registers all available skills/sub-agents in the
SkillRegistry, making them available throughout the application without
tight coupling via direct imports.

Import this module early in your application to ensure all skills are registered.
"""

import logging
from sdk.skill_registry import SkillRegistry

logger = logging.getLogger(__name__)


def register_all_skills() -> None:
    """
    Register all available skills in the SkillRegistry.
    
    This function imports and registers:
    - Agent skills (toc_agent, chapter_agent, collation_agent)
    - Validation skills (validate_yaml)
    - Router functions (route_after_toc)
    
    Call this function once at application startup to populate the registry.
    """
    logger.info("Registering all skills...")
    
    # Import agent skills
    from toc_agent.agent import toc_agent
    from chapter_agent.agent import chapter_agent_parallel
    from collation_agent.agent import collation_agent
    
    # Import utility skills
    from toc_agent.scripts.validate_yaml import validate_yaml
    
    # Register agent skills
    SkillRegistry.register(
        'toc_agent',
        toc_agent,
        description='Generate table of contents from topic description',
        category='agent'
    )
    
    SkillRegistry.register(
        'chapter_agent_parallel',
        chapter_agent_parallel,
        description='Generate all book chapters in parallel',
        category='agent'
    )
    
    SkillRegistry.register(
        'collation_agent',
        collation_agent,
        description='Collate chapters into final PDF book',
        category='agent'
    )
    
    # Register validation skills
    SkillRegistry.register(
        'validate_yaml',
        validate_yaml,
        description='Validate YAML content structure',
        category='validator'
    )
    
    logger.info(f"✓ Registered {len(SkillRegistry.list_available())} skills")
    
    # Log by category
    by_category = SkillRegistry.list_by_category()
    for category, skills in by_category.items():
        logger.info(f"  {category}: {', '.join(skills)}")


def register_router_functions() -> None:
    """
    Register router functions separately (they depend on route_after_toc).
    
    Router functions are registered in WorkflowRegistry, but we can also
    register them in SkillRegistry for consistency.
    """
    # Import locally to avoid circular dependencies
    from agent_graph import route_after_toc
    
    SkillRegistry.register(
        'route_after_toc',
        route_after_toc,
        description='Route after TOC generation based on validation',
        category='router'
    )
    
    logger.info("✓ Registered router functions")


# Auto-register when module is imported
# Commented out to allow manual control - uncomment if you want auto-registration
# register_all_skills()
