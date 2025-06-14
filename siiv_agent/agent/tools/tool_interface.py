from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass
class ToolExecutionResult:
    tool_name: str
    args: Dict[str, Any]
    stdout: str
    stderr: str
    return_code: int

    def to_llm_message(self) -> List[Dict[str, str]]:
        def format_args(args: Dict[str, Any]) -> str:
            if not args:
                return ""
            formatted = ", ".join(f"{k}={repr(v)}" for k, v in args.items())
            return f" with args ({formatted})"

        message_text = f"[{self.tool_name}]{format_args(self.args)} Result:"
        content_text = self.stdout if self.stdout else self.stderr

        return content_text
        # return [
        #     {"type": "text", "text": message_text},
        #     {"type": "text", "text": content_text},
        # ]

class ToolInterface(ABC):
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def execute(self, **kwargs) -> ToolExecutionResult:
        pass
