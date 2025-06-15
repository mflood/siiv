import logging
from typing import Any, Dict

from agent.tools.tool_interface import ToolExecutionResult, ToolInterface

LOGGER_NAME = __name__


class TaskCompleteError(Exception):
    """Raised when the agent has completed its task and is ready to return the final message to the user."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class FinishTaskTool(ToolInterface):

    def __init__(self):
        self._logger = logging.getLogger(LOGGER_NAME)

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "finish_task",
                "description": "Call this when the task is fully complete. The message should describe what was done.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "A summary of the steps taken or results obtained by the agent.",
                        },
                    },
                    "required": ["summary"],
                },
            },
        }

    def execute(self, **kwargs) -> ToolExecutionResult:
        self._logger.info(f"Executing finish_task tool with kwargs: {kwargs}")
        message = kwargs["summary"]
        self._logger.info(f"Raising TaskCompleteError with message: {message}")
        raise TaskCompleteError(message)


if __name__ == "__main__":
    import agent.my_logging

    tool = FinishTaskTool()
    try:
        result = tool.execute(message="I have finished the task")
    except TaskCompleteError as e:
        print(e.message)

# end
