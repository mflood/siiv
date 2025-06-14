from pathlib import Path
from typing import Any, Dict
from tools.tool_interface import ToolInterface, ToolExecutionResult

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
                        "description": "The path of the directory to search in (relative to the current working directory (self._root_path)). This directory will be recursively searched.",
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
                    "search_files", args, 1,
                    "Access denied: outside allowed directory."
                )

            if not target_dir.is_dir():
                return ToolExecutionResult(
                    "search_files", args, 1, "Provided path is not a directory."
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
                            line_max = ' '.join(
                                lines[max(idx - 2, 0): min(len(lines), idx + 3)]
                            )
                            result_lines.append(
                                f"{file_path}:{idx+1}\n{context}\n\n"
                            )

                except Exception as ex:
                    result_lines.append(f"[{file_path}] Error reading file: {ex}")

            if not result_lines:
                return ToolExecutionResult(
                    "search_files", args, 0, "No matches found."
                )

            return ToolExecutionResult("search_files", args, "\n".join(result_lines), 1)

            except Exception as ex:
                return ToolExecutionResult("search_files", args, str(ex), 1)

if __name__ == "__main__":
    root = "/Users/mathew.flood/workspace/airflom-datawarehouse/"
    tool = SearchFilesTool(root=root)
    result = tool.execute(args=["regex", "def main", "file_pattern=*.py"])
    content = result.to_lambda_message()
    print(content)
