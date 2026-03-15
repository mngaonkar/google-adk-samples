from typing import TypedDict, List

class AgentState(TypedDict):
    topic_description: str
    toc_location: str
    chapter_locations: List[str]
    reasoning_steps: List[str]
    final_content: str