import logging
import os
from pathlib import Path
from typing import Any, Dict

from agent.tools.tool_interface import ToolExecutionResult, ToolInterface

LOGGER_NAME = __name__


def _should_ignore_file(file_path: str) -> bool:
    ignore_list = [
        ".vscode",
        ".ipynb_checkpoints",
        ".git",
        "__pycache__",
        ".mypy_cache",
        "/tests/E2E",
        "venv/",
        ".pytest_cache",
        ".dbt/",
        "**/datwarehouse/logs",
        ".DS_Store",
    ]

    for match in ignore_list:
        if match in file_path:
            return True

    ignore_ends_with = [".csv", ".yaml", ".parquet", ".tsv", ".swp"]

    for end in ignore_ends_with:
        if file_path.endswith(end):
            return True

    return False


class FindFileTool(ToolInterface):
    def __init__(self, pwd: str):
        self._root_path = pwd
        self._logger = logging.getLogger(LOGGER_NAME)

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "find_file",
                "description": "Search for files matching a given filename or pattern within a directory. Matches are case-insensitive and partial (i.e. substring).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "The target filename or substring to match (case-insensitive).",
                        },
                        "directory": {
                            "type": "string",
                            "description": "The path of the directory to search in (relative to self._root_path)",
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "Whether to search subdirectories recursively.",
                        },
                        "required": ["filename", "directory", "recursive"],
                    },
                },
            },
        }

    def execute(self, **kwargs) -> ToolExecutionResult:
        filename = kwargs["filename"]
        directory = kwargs["directory"]
        recursive = kwargs.get("recursive", False)
        return self._execute(
            filename=filename, directory=directory, recursive=recursive
        )

    def _execute(
        self, filename: str, directory: str, recursive: bool
    ) -> ToolExecutionResult:
        args = {"filename": filename, "directory": directory, "recursive": recursive}
        self._logger.info("findFileTool executing: %s", args)

        if not directory.startswith("/"):
            directory = os.path.join(self._root_path, directory)

        if not os.path.isdir(directory) or not directory.startswith(self._root_path):
            return ToolExecutionResult(
                tool_name="find_file",
                args=args,
                stdout="",
                stderr="Access denied: outside allowed directory.",
                return_code=1,
            )

        path_object = Path(directory)
        if not path_object.is_dir():
            return ToolExecutionResult(
                tool_name="find_file",
                args=args,
                stdout="",
                stderr="Not a directory.",
                return_code=1,
            )

        try:

            self._logger.info(
                "globbing path %s (recursive=%s):", path_object, recursive
            )
            candidates = path_object.rglob("*") if recursive else path_object.glob("*")

            matches = []
            num_candidates = 0
            for glob_file_object in candidates:
                num_candidates += 1
                if filename.lower() in glob_file_object.name.lower():
                    full_path_as_string = str(glob_file_object)

                    self._logger.info(
                        "name matches '%s': %s", filename.lower(), full_path_as_string
                    )

                    if _should_ignore_file(full_path_as_string):
                        self._logger.info("ignoring '%s'", full_path_as_string)
                        continue

                    if not glob_file_object.is_file():
                        self._logger.info("appending '/' to folder")
                        full_path_as_string += "/"
                    matches.append(full_path_as_string)

            self._logger.info(
                "%d of %d objects matched '%s'",
                len(matches),
                num_candidates,
                filename.lower(),
            )

            return ToolExecutionResult(
                tool_name="find_file",
                args=args,
                stdout="\n".join(matches),
                stderr="",
                return_code=0,
            )

        except Exception as e:
            self._logger.error("Unknown exception in find_files '%s': %s", e, type(e))
            return ToolExecutionResult(
                tool_name="find_file",
                args=args,
                stdout="",
                stderr=str(e),
                return_code=1,
            )


if __name__ == "__main__":

    from agent.my_logging import init_logging

    init_logging()

    pwd = "/Users/matthewflood/workspace/siiv/photo_to_code"
    tool = FindFileTool(pwd=pwd)
    results = tool.execute(
        filename="photo_to_code_batch.py", directory=pwd, recursive=False
    )
    content = results.to_llm_message()
    print(content)

# end
