from typing import TypedDict, List
from declarative_agent_sdk import AgentState

class BookAgentState(AgentState):
    toc_location: str
    chapter_locations: List[str]
    reasoning_steps: List[str]
    final_content: str