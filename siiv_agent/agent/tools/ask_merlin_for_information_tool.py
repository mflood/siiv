import sys
from typing import Any, Dict

from agent.tools.tool_interface import ToolExecutionResult, ToolInterface


class AskMerlinForInformationTool(ToolInterface):
    def __init__(self, pwd: str):
        self.root_path = pwd

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "ask_merlin_for_information",
                "description": "Prompt Merlin directly for a missing piece of information. Useful when an LLM needs information not provided by other tools or clarity on how to proceed. Merlin has access to the bertelsmeier files, Merlin knows the names of all relevant files, Merlin can see the airflow UI and airflow logs, Merlin can query snowflake. Merlin knows how to use kubectl to investigate kubernetes, Merlin knows which s3 buckets are used and can look into s3 files. Merlin is a staff software engineer. It is always better to ask Merlin for clarity instead of making assumptions and guesses. Merlin has direct access to logs. If you need to access a log file, you must ask Merlin.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The question or prompt for Merlin to respond to.",
                        },
                    },
                    "required": ["prompt"],
                },
            },
        }

    def execute(self, **kwargs) -> ToolExecutionResult:
        return self._execute(prompt=kwargs["prompt"])

    def _execute(self, prompt: str) -> ToolExecutionResult:
        args = {"prompt": prompt}

        try:
            print(
                "\n***** Human input required:\n\n{prompt}\n\n(Type your response. Press Ctrl-D or Ctrl-Z (Windows) when done.)\n"
            )
            user_input = sys.stdin.read()
            return ToolExecutionResult(
                tool_name="ask_human_for_information",
                args=args,
                stdout=user_input.strip(),
                stderr="",
                return_code=0,
            )

        except Exception as e:
            return ToolExecutionResult(
                tool_name="ask_human_for_information",
                args=args,
                stdout="",
                stderr=str(e),
                return_code=1,
            )


if __name__ == "__main__":
    tool = AskMerlinForInformationTool(pwd=".")
    result = tool.execute(prompt="What should the description of this tool be?")
    print(result.to_llm_message())
