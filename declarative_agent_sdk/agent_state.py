from typing import TypedDict, List

class AgentState(TypedDict):
    """Defines the state structure for agents in the AI workflow.
    
    Attributes:
        user_query (str): The user's query or input to the agent.

        Add additional keys (agent name) for storing agent output
    """
    user_query: str
    final_answer: str