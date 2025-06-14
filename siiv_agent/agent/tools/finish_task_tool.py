```python
from typing import Any, Dict
from tools.tool_interface import ToolInterface, ToolExecutionResult

class TaskCompleteError(Exception):
    """Raised when the agent has completed its task and is ready to return the final message to the user."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class FinishTaskTool(ToolInterface):
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "finish_task",
                "description": "Call this when the task is fully complete. The message should describe what was done.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "A summary of the steps taken or results obtained by the agent.",
                        },
                    },
                    "required": ["message"],
                },
            },
        }

    def execute(self, **kwargs) -> ToolExecutionResult:
        message = kwargs["message"]
        raise TaskCompleteError(message)
```