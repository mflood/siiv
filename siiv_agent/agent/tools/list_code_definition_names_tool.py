import ast
from pathlib import Path
import os
from typing import Any, Dict, List
from agent.tools.tool_interface import ToolInterface, ToolExecutionResult

def extract_definitions(file_path: Path) -> List[str]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=str(file_path))
        definitions = []

        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                definitions.append(f"def {node.name}()")
            elif isinstance(node, ast.ClassDef):
                definitions.append(f"class {node.name}")

        return definitions
    except Exception as e:
        return [f"# Error parsing {file_path}: {e}"]

class ListCodeDefinitionNamesTool(ToolInterface):
    def __init__(self, pwd: str):

        self._root_path = pwd

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_code_definition_names",
                "description": (
                    "List top-level class, function, and method definitions in Python files "
                    "within a specified directory. This only lists definitions in files at "
                    "the top level of the given directory (non-recursive)."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory to list top-level Python code definitions from",
                        },
                    },
                    "required": ["path"],
                },
            },
        }

    def execute(self, **kwargs) -> ToolExecutionResult:
        return self._execute(path=kwargs["path"])

    def _execute(self, path: str) -> ToolExecutionResult:
        args = {"path": path}

        try:
            if not path.startswith("/"):
                path = os.path.join(self._root_path, path)

            if not str(path).startswith(str(self._root_path)):
                return ToolExecutionResult(
                    "list_code_definition_names", args, "", "Access denied", 1
                )

            path_object = Path(path)
            if not path_object.exists() or not path_object.is_dir():
                return ToolExecutionResult(
                    "list_code_definition_names", args, "", "Not a directory", 1
                )

            results = []
            for file in path_object.glob("*.py"):
                definitions = extract_definitions(file)
                if definitions:
                    results.append(f"{file.name}:\n" + "\n".join(definitions))

            output = "\n\n".join(results) if results else "No definitions found."
            return ToolExecutionResult(
                "list_code_definition_names", args, output, "", 0
            )
        except Exception as e:
            return ToolExecutionResult(
                "list_code_definition_names", args, "", str(e), 1
            )

if __name__ == "__main__":
    # Change this path as needed for local testing
    pwd = "/Users/matthewflood/workspace/siiv/photo_to_code"
    tool = ListCodeDefinitionNamesTool(pwd=pwd)
    results = tool.execute(path="") # relative to `pwd`
    content = results.to_llm_message()
    print(content)
