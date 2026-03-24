"""
Skill Registry - Registry pattern for agent skills and sub-agents.

This module provides a centralized registry to manage agent skills (sub-agents)
and their metadata. The actual callable functions are stored in ToolRegistry.
"""

import os
import yaml
from typing import Dict, List, Any, Optional
from sdk.logging_config import get_logger

logger = get_logger(__name__)


class SkillRegistry:
    """
    Registry to map skill names to their directories.
    
    Skills are reusable agent functions or sub-agents that can be composed
    into larger workflows. This registry provides a central location to
    manage skill directories and metadata. Functions/callables are stored
    in ToolRegistry which auto-discovers scripts in skill directories.
    
    Example:
        # Register skills
        SkillRegistry.register('toc_agent', directory='skills/toc')
        
        # Get skill directory
        directory = SkillRegistry.get_directory('toc_agent')
        
        # Get skill function from ToolRegistry
        from sdk.tool_registry import ToolRegistry
        toc_agent = ToolRegistry.get('toc_agent')
        
        # List all registered
        skills = SkillRegistry.list_available()
    """
    
    _skills: Dict[str, str] = {}  # Maps skill name to directory path
    _metadata: Dict[str, Dict[str, Any]] = {}  # Maps skill name to metadata
    
    @classmethod
    def register(
        cls, 
        name: str,
        directory: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        **metadata
    ) -> None:
        """
        Register a skill with a given name and directory.
        
        Args:
            name: String identifier for the skill
            directory: Directory path where the skill is located
            description: Optional description of what the skill does
            category: Optional category (e.g., 'agent', 'validator', 'tool')
            **metadata: Additional metadata to store with the skill
            
        Example:
            SkillRegistry.register(
                'toc_agent',
                directory='skills/toc',
                description='Generate table of contents',
                category='agent'
            )
        """
        cls._skills[name] = directory
        
        # Store metadata
        skill_metadata = {
            'description': description,
            'category': category,
            'directory': directory,
            **metadata
        }
        cls._metadata[name] = skill_metadata
        
        logger.debug(f"Registered skill: {name} (category: {category}, directory: {directory})")
    
    @classmethod
    def get_directory(cls, name: str) -> Optional[str]:
        """
        Get the directory path for a skill.
        
        Args:
            name: The skill name
            
        Returns:
            Directory path or None if not set
            
        Raises:
            ValueError: If skill name is not found in registry
            
        Example:
            directory = SkillRegistry.get_directory('toc_agent')
            print(f"Skill located at: {directory}")
        """
        if name not in cls._skills:
            available = list(cls._skills.keys())
            raise ValueError(
                f"Skill '{name}' not found in registry. "
                f"Available skills: {available}"
            )
        return cls._skills.get(name)
    
    @classmethod
    def get_metadata(cls, name: str) -> Dict[str, Any]:
        """
        Get metadata for a skill.
        
        Args:
            name: The skill name
            
        Returns:
            Dictionary of metadata including description, category, and directory
            
        Example:
            metadata = SkillRegistry.get_metadata('toc_agent')
            print(metadata['description'])
            print(metadata['directory'])
        """
        return cls._metadata.get(name, {})
    
    @classmethod
    def list_available(cls, category: Optional[str] = None) -> List[str]:
        """
        List all available skill names, optionally filtered by category.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of registered skill names
            
        Example:
            all_skills = SkillRegistry.list_available()
            agents_only = SkillRegistry.list_available(category='agent')
        """
        if category is None:
            return list(cls._skills.keys())
        
        return [
            name for name, metadata in cls._metadata.items()
            if metadata.get('category') == category
        ]
    
    @classmethod
    def list_by_category(cls) -> Dict[str, List[str]]:
        """
        List all skills grouped by category.
        
        Returns:
            Dictionary mapping categories to lists of skill names
            
        Example:
            by_category = SkillRegistry.list_by_category()
            print(by_category)
            # {'agent': ['toc_agent', 'chapter_agent'], 
            #  'validator': ['validate_yaml'], ...}
        """
        categories: Dict[str, List[str]] = {}
        for name, metadata in cls._metadata.items():
            category = metadata.get('category', 'uncategorized')
            if category not in categories:
                categories[category] = []
            categories[category].append(name)
        return categories
    
    @classmethod
    def clear(cls) -> None:
        """
        Clear all registered skills.
        
        This is primarily useful for testing to reset the registry state.
        
        Example:
            SkillRegistry.clear()
        """
        cls._skills.clear()
        cls._metadata.clear()
        logger.debug("Cleared all skills from registry")
    
    @classmethod
    def is_registered(cls, name: str) -> bool:
        """
        Check if a skill name is registered.
        
        Args:
            name: The skill name to check
            
        Returns:
            True if registered, False otherwise
            
        Example:
            if SkillRegistry.is_registered('toc_agent'):
                directory = SkillRegistry.get_directory('toc_agent')
        """
        return name in cls._skills
    
    @classmethod
    def register_multiple(
        cls, 
        skills: Dict[str, str],
        category: Optional[str] = None,
        description: Optional[str] = None
    ) -> None:
        """
        Register multiple skills at once.
        
        Args:
            skills: Dictionary mapping skill names to directory paths
            category: Optional category to apply to all skills
            description: Optional description to apply to all skills
            
        Example:
            SkillRegistry.register_multiple({
                'toc_agent': 'skills/toc',
                'chapter_agent': 'skills/chapter',
                'collation_agent': 'skills/collation'
            }, category='agent')
        """
        for name, directory in skills.items():
            cls.register(name, directory=directory, category=category, description=description)
        logger.info(f"Registered {len(skills)} skills (category: {category})")
    
    @classmethod
    def register_all_from_directory(cls, skills_directory: str = 'skills') -> int:
        """
        Auto-discover and register all skills from a directory.
        
        This method:
        1. Traverses the skills directory recursively
        2. Finds all SKILL.md files with YAML frontmatter
        3. Registers each skill in SkillRegistry
        4. Auto-discovers and registers tools from scripts/ folders in ToolRegistry
        
        Args:
            skills_directory: Base directory containing skill folders (default: 'skills')
            
        Returns:
            Total number of skills registered
            
        Example:
            # Auto-discover and register all skills
            count = SkillRegistry.register_all_from_directory('my_skills')
            print(f"Registered {count} skills")
            
        Skill Directory Structure:
            skills/
              skill_name/
                SKILL.md              # Must have YAML frontmatter with name & description
                scripts/
                  tool1.py            # Auto-discovered as tools
                  tool2.py
        """
        from sdk.tool_registry import ToolRegistry
        
        logger.info(f"Auto-discovering skills from: {skills_directory}")
        
        skills_registered = 0
        tools_registered = 0
        
        for root, dirs, files in os.walk(skills_directory):
            for dir_name in dirs:
                skill_dir_path = os.path.join(root, dir_name)
                skill_md_path = os.path.join(skill_dir_path, 'SKILL.md')
                
                if os.path.exists(skill_md_path):
                    try:
                        with open(skill_md_path, 'r') as f:
                            content = f.read()
                            
                            # Parse YAML frontmatter (between --- delimiters)
                            if content.startswith('---'):
                                parts = content.split('---', 2)
                                if len(parts) >= 3:
                                    # Parse the YAML frontmatter (parts[1])
                                    frontmatter = yaml.safe_load(parts[1])
                                    
                                    skill_name = frontmatter.get('name')
                                    skill_desc = frontmatter.get('description')
                                    skill_category = frontmatter.get('category', 'agent')
                                    
                                    if skill_name and skill_desc:
                                        # Register skill metadata in SkillRegistry
                                        cls.register(
                                            skill_name,
                                            directory=skill_dir_path,
                                            description=skill_desc,
                                            category=skill_category
                                        )
                                        skills_registered += 1
                                        logger.info(f"✓ Registered skill: {skill_name} (directory: {skill_dir_path})")
                                        
                                        # Auto-discover and register tools from scripts folder
                                        scripts_dir = os.path.join(skill_dir_path, 'scripts')
                                        if os.path.exists(scripts_dir):
                                            count = ToolRegistry.register_from_scripts_folder(
                                                scripts_dir, 
                                                prefix=""
                                            )
                                            if count > 0:
                                                tools_registered += count
                                                logger.info(f"  ✓ Registered {count} tools from {scripts_dir}")
                                    else:
                                        logger.warning(f"SKILL.md at {skill_md_path} is missing 'name' or 'description' in YAML frontmatter.")
                                else:
                                    logger.warning(f"SKILL.md at {skill_md_path} doesn't have proper YAML frontmatter delimiters.")
                    except yaml.YAMLError as e:
                        logger.error(f"✗ Failed to parse YAML frontmatter in {skill_md_path}: {e}")
                    except Exception as e:
                        logger.error(f"✗ Error processing {skill_md_path}: {e}")
        
        logger.info(f"✓ Registered {skills_registered} skills and {tools_registered} tools")
        
        # Log by category
        by_category = cls.list_by_category()
        for category, skills in by_category.items():
            logger.info(f"  {category}: {', '.join(skills)}")
        
        return skills_registered
    
    @classmethod
    def unregister(cls, name: str) -> None:
        """
        Unregister a skill.
        
        Args:
            name: The skill name to unregister
            
        Example:
            SkillRegistry.unregister('old_agent')
        """
        if name in cls._skills:
            del cls._skills[name]
        if name in cls._metadata:
            del cls._metadata[name]
        logger.debug(f"Unregistered skill: {name}")
    
    @classmethod
    def info(cls) -> Dict[str, Any]:
        """
        Get information about the registry.
        
        Returns:
            Dictionary with registry statistics
            
        Example:
            info = SkillRegistry.info()
            print(f"Total skills: {info['total_skills']}")
        """
        by_category = cls.list_by_category()
        return {
            'total_skills': len(cls._skills),
            'categories': list(by_category.keys()),
            'skills_by_category': by_category
        }
