import os
from pathlib import Path
from typing import Any, Dict

from agent.tools.tool_interface import ToolExecutionResult, ToolInterface


class ReadFileTool(ToolInterface):

    def __init__(self, pwd: str):
        self._root_path = pwd

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Request to read the contents of a file at the specified path. Use this when you need to examine the contents of an existing file you do not know the contents of, for example to analyze code, review text files, or extract information from configuration files. Automatically extracts raw text from PDF and DOCX files. May not be suitable for other types of binary files, as it returns the raw content as a string.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path of the file to read (relative to the current working directory (self._root_path))",
                        },
                    },
                    "required": ["file_path"],
                },
            },
        }

    def execute(self, **kwargs) -> ToolExecutionResult:
        file_path = kwargs["file_path"]
        return self._execute(file_path=file_path)

    def _execute(self, file_path: str) -> ToolExecutionResult:
        args = {"file_path": file_path}

        if not file_path.startswith("/"):
            file_path = os.path.join(self._root_path, file_path)

        if not str(file_path).startswith(str(self._root_path)):
            return ToolExecutionResult(
                tool_name="read_file",
                args=args,
                stdout="",
                stderr="Access denied: outside allowed directory",
                return_code=1,
            )

        file_path = Path(file_path)

        if not file_path.exists():
            return ToolExecutionResult(
                tool_name="read_file",
                args=args,
                stdout="",
                stderr=f"File '{file_path}' does not exist",
                return_code=1,
            )

        if not file_path.is_file():
            return ToolExecutionResult(
                tool_name="read_file",
                args=args,
                stdout="",
                stderr="Path is not a file",
                return_code=1,
            )

        try:
            contents = file_path.read_text(encoding="utf-8", errors="replace")
            return ToolExecutionResult(
                tool_name="read_file",
                args=args,
                stdout=contents,
                stderr="",
                return_code=0,
            )

        except Exception as e:
            return ToolExecutionResult(
                tool_name="read_file",
                args=args,
                stdout="",
                stderr=str(e),
                return_code=1,
            )


if __name__ == "__main__":
    pwd = "/Users/matthewflood/workspace/siiv/"
    tool = ReadFileTool(pwd=pwd)
    results = tool.execute(file_path=f"photo_to_code/photo_to_code_batch.py")
    content = results.to_llm_message()
    print(content)
