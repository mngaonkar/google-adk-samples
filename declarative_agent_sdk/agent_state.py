from typing import TypedDict, List

class AgentState(TypedDict):
    user_query: str
    agent_output: dict[str, str]