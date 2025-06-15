import logging
from agent.utils import print_orange
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from agent.tools.tool_interface import ToolExecutionResult, ToolInterface

LOGGER_NAME = __name__


def _should_ignore_file(file_path: str) -> bool:
    logger = logging.getLogger(LOGGER_NAME)

    ignore_list = [
        "..",
        ".ruff_cache",
        ".pytest_cache",
        ".mypy_cache",
        "Index.noindex",
        "DerivedData",
        ".vscode",
        ".ipynb_checkpoints",
        ".git",
        "e/tmp/",
        ".my_cache",
        ".DS_Store",
        ".spw",
        ".gitignore",
        ".gitkeep",
        ".gitignore",
        "/venv/",
        "/__pycache__/",
    ]

    for match in ignore_list:
        if match in file_path:
            return True

    ignore_ends_with = [".csv", ".yaml", ".parquet", ".tsv", ".log"]

    for end in ignore_ends_with:
        if file_path.endswith(end):
            return True

    return False


class ListFilesTool(ToolInterface):

    def __init__(self, pwd: str):
        self._root_path = pwd
        self._logger = logging.getLogger(LOGGER_NAME)

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "Request to list files and directories within the specified directory. If recursive is true, it will list all files and directories recursively. If recursive is fals or not provided, it will only list the top-level contents.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "The path of the directory to list contents for (relative to the current working directory {self._root_path})",
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "Whether to list files recursively. Use true for recursive listing, false or omit for top-level only.",
                            "default": False,
                        },
                    },
                    "required": ["directory"],
                },
            },
        }

    def execute(self, **kwargs) -> ToolExecutionResult:
        directory = kwargs["directory"]
        recursive = kwargs.get("recursive", False)
        return self._execute(directory=directory, recursive=recursive)

    def _execute(self, directory: str, recursive: bool) -> ToolExecutionResult:
        args = {"directory": directory, "recursive": recursive}

        print_orange(f"ListFilesTool.execute(directory='{directory}', recursive={recursive}")

        if directory.startswith("./"):
            directory = directory[2:]

        if not directory.startswith("/"):
            directory = os.path.join(self._root_path, directory)
            self._logger.info(
                f"Appending root path '{self._root_path}' to directory: {directory}"
            )

        if not str(directory).startswith(str(self._root_path)):
            return ToolExecutionResult(
                tool_name="list_files",
                args=args,
                stdout="",
                stderr="Access denied: outside allowed directory",
                return_code=1,
            )

        path_object = Path(directory)

        if not path_object.is_dir():
            return ToolExecutionResult(
                tool_name="list_files",
                args=args,
                stdout="",
                stderr="Not a directory",
                return_code=1,
            )

        try:
            candidates = path_object.rglob("*") if recursive else path_object.glob("*")
            files = []
            num_candidates = 0
            for file in candidates:
                num_candidates += 1
                path = str(file)
                if not file.is_file():
                    path += "/"

                if not _should_ignore_file(path):
                    files.append(path)

            self._logger.info(
                f"%d of %d files were valid in %s",
                len(files),
                num_candidates,
                path_object,
            )

            return ToolExecutionResult(
                tool_name="list_files",
                args=args,
                stdout="\n".join(files),
                stderr="",
                return_code=0,
            )

        except Exception as e:
            return ToolExecutionResult(
                tool_name="list_files",
                args=args,
                stdout="",
                stderr=str(e),
                return_code=1,
            )


if __name__ == "__main__":

    import agent.my_logging

    pwd = "/Users/matthewflood/workspace/siiv"
    tool = ListFilesTool(pwd=pwd)
    results = tool._execute(directory="", recursive=True)

    content = results.to_llm_message()
    print(content)
