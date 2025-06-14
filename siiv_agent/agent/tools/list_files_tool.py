```python
import subprocess
from pathlib import Path
import os
from typing import Any, Dict, List
from tools.tool_interface import ToolInterface, ToolExecutionResult

def _should_ignore_file(file_path: str) -> bool:

    if "ecs" not in file_path:
        return True

    ignore_list = [
        "arehouse/local",
        ".vscode",
        ".ipynb_checkpoints",
        ".git",
        "e/tmp/",
        ".my_cache",
        "tests/E2E",
        "/__",
        "/pycache__",
        "airflow-datawarehouse/deployments",
        "airflow-datawarehouse/myout",
        "airflow-datawarehouse/scripts",
        "airflow-datawarehouse/templates",
        "lib/dbt/",
        ".spw",
        "datawarehouse/logs",
        ".DS_Store",
    ]

    for match in ignore_list:
        if match in file_path:
            return True

    ignore_ends_with = [".csv", ".yaml", ".parquet", ".tsv"]

    for end in ignore_ends_with:
        if file_path.endswith(end):
            return True

    return False

class ListFilesTool(ToolInterface):

    def __init__(self, pwd: str):
        self._root_path = pwd

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "Request to list files and directories within the specified directory. If recursive is true, 
ir not provided, it will only list the top-level contents.",
                "parameters": {
``````python
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
                "default": false,
            },
        },
        "required": ["directory"],
    },
},

def execute(self, **kwargs) -> ToolExectutionResult:
    directory = kwargs["directory"]
    recursive = kwargs.get("recursive", false)
    return self._execute(directory=directory, recursive=recursive)

def _execute(self, directory: str, recursive: bool) -> ToolExectutionResult:
    args = {"directory": directory, "recursive": recursive}

    if not directory.startwith("/"):
        directory = os.path.join(self._root_path, directory)

    if not str(directory).startswith(str(self._root_path)):
        return ToolExectutionResult(
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
        for file in candidates:
            path = str(file)
            if not file.is_file():
                path += "/"
``````python
def _execute(self, directory: str, recursive: bool) -> ToolExecutionResult:
    args = {"directory": directory, "recursive": recursive}

    if not directory.startswith("/"):
        directory = os.path.join(self._root_path, directory)

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
        for file in candidates:
            path = str(file)
            if not file.is_file():
                path += "/"
            if not _should_ignore_file(path):
                files.append(path)

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
    pwd = "/Users/matthew.flood/workspace/airflow-datawarehouse"
    tool = ListFilesTool(pwd=pwd)
    results = tool._execute(directory="dags", recursive=False)
    content = results.to_llm_message()
    print(content)
```