from sdk.ai_agent import AIAgent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.base_agent import BaseAgent

class AIAgentParallel():
    def __init__(self, 
                 name: str,
                 agent_list: list[BaseAgent]):
        self.name = name
        self.agent_list = agent_list

    def create_agent(self) -> ParallelAgent:
        parallel_agent = ParallelAgent(
            name=self.name,
            sub_agents=self.agent_list,
            description="Runs multiple research agents in parallel to gather information."
        )
        return parallel_agent
    
    
    