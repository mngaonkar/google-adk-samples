"""
Skill Registry - Registry pattern for agent skills and sub-agents.

This module provides a centralized registry to manage agent skills (sub-agents)
and their metadata. The actual callable functions are stored in ToolRegistry.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


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
