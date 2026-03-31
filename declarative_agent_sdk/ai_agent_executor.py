from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from declarative_agent_sdk import AIAgent
from a2a.utils.errors import ServerError
from a2a.utils import new_agent_text_message
from a2a.server.tasks import TaskUpdater
from declarative_agent_sdk.agent_logging import get_logger
logger = get_logger(__name__)

from a2a.types import (
    DataPart,
    Part,
    Task,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)

class AIAgentExecutor(AgentExecutor):
    def __init__(self, agent: AIAgent):
        self._agent = agent

    async def execute(
      self,
      context: RequestContext,
      event_queue: EventQueue,
  ) -> None:
        ui_event_part = None
        query = ""
        action = None

        logger.info(f"Received execution request with context: {context.message}")
        if context.message and context.message.parts:
            logger.info("Executing AI agent with message parts: %s", context.message.parts)
            for i, part in enumerate(context.message.parts):
                if isinstance(part.root, DataPart):
                    if "userAction" in part.root.data:
                        ui_event_part = part.root.data["userAction"]
                        logger.info(f"Found userAction in DataPart: {ui_event_part}")
                elif isinstance(part.root, TextPart):
                    logger.info(f"Processing TextPart: {part.root.text}")
        
        if ui_event_part:
            action = ui_event_part.get("action")
            ctx = ui_event_part.get("context", {})

            if action == "find_route":
                origin = ctx.get("origin")
                destination = ctx.get("destination")
                logger.info(f"Finding route from {origin} to {destination}")
                query = f"Find a route from {origin} to {destination}"
        else:
            logger.warning("No userAction found in message parts. Executing agent with empty input.")
            query = context.get_user_input()
        
        logger.info(f"User input query: {query}")
        
        logger.info(f"task_id: {context.task_id}, context_id: {context.context_id}")
        
        if not context.task_id or not context.context_id:
            raise ServerError(error=UnsupportedOperationError(message="task_id or context_id is None"))
        
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        if not context.current_task:
            await updater.submit()
        await updater.start_work()

        try:
            result = await self._agent.run(query)
            logger.info(f"Agent execution result: {result}")
            if result:
                await updater.add_artifact([Part(root=TextPart(text=str(result)))], name="final_response")
                await updater.complete()
        except Exception as e:
            logger.error(f"Error during agent execution: {e}")
            await updater.update_status(
                TaskState.failed,
                message=new_agent_text_message(f"An error occurred: {str(e)}"),
                final=True,
            )

    async def cancel(
      self, context: RequestContext, event_queue: EventQueue
  ) -> None:
        raise ServerError(error=UnsupportedOperationError())