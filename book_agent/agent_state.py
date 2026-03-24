from typing import TypedDict, List
from sdk.agent_state import AgentState

class BookAgentState(AgentState):
    topic_description: str
    toc_location: str
    chapter_locations: List[str]
    reasoning_steps: List[str]
    final_content: str