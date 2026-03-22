import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Registry to map tool names to actual tool objects."""
    
    _tools: Dict[str, Any] = {}
    
    @classmethod
    def register(cls, name: str, tool: Any) -> None:
        """Register a tool with a given name."""
        cls._tools[name] = tool
        logger.debug(f"Registered tool: {name}")
    
    @classmethod
    def get(cls, name: str) -> Any:
        """Get a tool by name."""
        if name not in cls._tools:
            raise ValueError(f"Tool '{name}' not found in registry. Available tools: {list(cls._tools.keys())}")
        return cls._tools[name]
    
    @classmethod
    def get_multiple(cls, names: List[str]) -> List[Any]:
        """Get multiple tools by their names."""
        return [cls.get(name) for name in names]
    
    @classmethod
    def list_available(cls) -> List[str]:
        """List all available tool names."""
        return list(cls._tools.keys())


def register_common_tools():
    """Register commonly used tools in the ToolRegistry."""
    try:
        from google.adk.tools import google_search
        ToolRegistry.register('google_search', google_search)
        logger.info("Registered common ADK tools")
    except ImportError as e:
        logger.warning(f"Could not import common tools: {e}")


# Auto-register common tools when module is imported
register_common_tools()