from pathlib import Path
from typing import Any, Dict
from agent.tools.tool_interface import ToolInterface, ToolExecutionResult
import re

class SearchFilesTool(ToolInterface):
    def __init__(self, root_path: str):
        self._root_path = Path(root_path).resolve()

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "search_files",
                "description": "Perform a regex search across files in a specified directory, showing context-rich results.",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": f"The path of the directory to search in (relative to the current working directory ({self._root_path})). This directory will be recursively searched.",
                    },
                    "regex": {
                        "type": "string",
                        "description": "Regular expression pattern to search for (compatible with Python's `re` module syntax).",
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "(optional) Glob pattern to filter files (e.g., '*.ts' for TypeScript files). If not provided, it will search all files ('*').",
                    },
                },
                "required": ["path", "regex"],
            },
        }

    def execute(self, **kwargs) -> ToolExecutionResult:
        path = kwargs["path"]
        regex = kwargs["regex"]
        file_pattern = kwargs.get("file_pattern", "*")
        return self._execute(path, regex, file_pattern)

    def _execute(self, path: str, regex: str, file_pattern: str) -> ToolExecutionResult:
        args = {"path": path, "regex": regex, "file_pattern": file_pattern}
        result_lines = []

        try:
            target_dir = (
                Path(path) if Path(path).is_absolute() else self._root_path / path
            ).resolve()

            if not str(target_dir).startswith(str(self._root_path)):
                return ToolExecutionResult(
                    tool_name="search_files",
                    args=args,
                    stdout="",
                    stderr="Access denied: outside allowed directory.",
                    return_code=1,
                )

            if not target_dir.is_dir():
                return ToolExecutionResult(
                    tool_name="search_files",
                    args=args,
                    stdout="",
                    stderr="Provided path is not a directory.",
                    return_code=1,
                )

            compiled = re.compile(regex)

            matched_files = list(target_dir.rglob(file_pattern))

            for file_path in matched_files:

                if not file_path.is_file():
                    continue

                try:
                    lines = file_path.read_text(
                        encoding="utf-8", errors="ignore"
                    ).splitlines()

                    for idx, line in enumerate(lines):
                        compiled_search = compiled.search(line)
                        if compiled_search:
                            context = '\n'.join(
                                lines[max(idx - 2, 0): min(len(lines), idx + 3)]
                            )
                            result_lines.append(
                                f"{file_path}:{idx+1}\n{context}\n\n"
                            )

                except Exception as ex:
                    result_lines.append(f"[{file_path}] Error reading file: {ex}")

            if not result_lines:
                return ToolExecutionResult(
                    tool_name="search_files",
                    args=args,
                    stdout="",
                    stderr="No matches found.",
                    return_code=0,
                )

            return ToolExecutionResult(
                tool_name="search_files",
                args=args,
                stdout="\n".join(result_lines),
                stderr="",
                return_code=0,
            )

        except Exception as ex:
            return ToolExecutionResult(tool_name="search_files", args=args, stdout=str(ex), stderr="", return_code=1)

if __name__ == "__main__":
    root = "/Users/matthewflood/workspace/siiv/photo_to_code"
    tool = SearchFilesTool(root_path=root)
    result = tool._execute(path=".", regex="parse_args", file_pattern="*.py")
    print(result)

    content = result.to_llm_message()
    print(content)
