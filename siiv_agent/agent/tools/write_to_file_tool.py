import os
from pathlib import Path
from typing import Any, Dict

from agent.tools.tool_interface import ToolExecutionResult, ToolInterface


class WriteToFileTool(ToolInterface):

    def __init__(self, root_path: str):
        self._root_path = Path(root_path).resolve()

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "write_to_file",
                "description": "Write content to a file. If the file exists, it will be overwritten. Creates parent directories as needed. If the file doesn't exist, it will be created. This tool will automatically create any directories needed to write the file. ALWAYS provide the COMPLETE intended content of the file, without any truncation or omissions. You MUST include ALL parts of the file, even if they haven't been modified.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The full path of the file to write.",
                        },
                        "content": {
                            "type": "string",
                            "description": "The content to write to the file.",
                        },
                    },
                    "required": ["file_path", "content"],
                },
            },
        }

    def execute(self, **kwargs) -> ToolExecutionResult:
        file_path = kwargs["file_path"]
        content = kwargs["content"]
        return self._execute(file_path, content)

    def _execute(self, file_path: str, content: str) -> ToolExecutionResult:
        args = {"file_path": file_path, "content": f"({len(content)} characters)"}

        try:
            if not str(file_path).startswith(("/", ".")):
                file_path = os.path.join(self._root_path, file_path)

            path = Path(file_path).resolve()

            if not str(path).startswith(str(self._root_path)):
                return ToolExecutionResult(
                    tool_name="write_to_file",
                    args=args,
                    stdout="",
                    stderr="Access denied: outside allowed root directory",
                    return_code=4,
                )

            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

            return ToolExecutionResult(
                tool_name="write_to_file",
                args=args,
                stdout=f"Successfully wrote ({len(content)}) characters to '{file_path}'",
                stderr="",
                return_code=0,
            )

        except Exception as ex:
            return ToolExecutionResult(
                tool_name="write_to_file",
                args=args,
                stdout="",
                stderr=str(ex),
                return_code=1,
            )


if __name__ == "__main__":

    pwd = Path.cwd()
    tool = WriteToFileTool(root_path=str(pwd))
    result = tool._execute(
        str(pwd / "tmp/test_output.txt"), "Hello from the write_to_file tool!"
    )
    contents = result.to_llm_message()
    print(contents)

# end
