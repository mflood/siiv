from typing import Any, Dict, List, Optional

from agent.tools.ask_merlin_for_information_tool import \
    AskMerlinForInformationTool
from agent.tools.execute_command_tool import ExecuteCommandTool
from agent.tools.find_file_tool import FindFileTool
from agent.tools.finish_task_tool import FinishTaskTool
from agent.tools.list_code_definition_names_tool import \
    ListCodeDefinitionNamesTool
from agent.tools.list_files_tool import ListFilesTool
from agent.tools.read_file_tool import ReadFileTool
from agent.tools.replace_in_file_tool import ReplaceInFileTool
from agent.tools.search_files_tool import SearchFilesTool
from agent.tools.tool_interface import ToolExecutionResult, ToolInterface
from agent.tools.write_to_file_tool import WriteToFileTool


class TaskCompleteError(Exception):
    pass


class ToolManager:

    def __init__(self, tool_list: List[ToolInterface]):
        self._tool_list = tool_list

        self._tool_map = {}
        for tool in tool_list:
            print(tool)
            schema = tool.get_schema()
            function_name = schema["function"]["name"]
            self._tool_map[function_name] = tool

    def get_tools_schema_list(self) -> List[dict]:
        return [tool.get_schema() for tool in self._tool_list]

    def execute_tool_by_name(
        self, name: str, args: Dict[str, Any]
    ) -> Optional[ToolExecutionResult]:
        tool = self._tool_map.get(name)
        return tool.execute(**args) if tool else None

    @classmethod
    def default(cls, root_dir: str) -> "ToolManager":
        return cls(
            [
                ExecuteCommandTool(
                    pwd=root_dir,
                    allowed_commands=[
                        "pwd",
                        "whoami",
                        "ping",
                        "mkdir",
                        "ls",
                        "cat",
                        "echo",
                        "find",
                        "grep",
                        "file",
                        "pip",
                    ],
                ),
                ListFilesTool(pwd=root_dir),
                ReadFileTool(pwd=root_dir),
                ReplaceInFileTool(pwd=root_dir),
                SearchFilesTool(root_path=root_dir),
                WriteToFileTool(root_path=root_dir),
                # FindFileTool(pwd=root_dir),
                ListCodeDefinitionNamesTool(pwd=root_dir),
                # AskMerlinForInformationTool(pwd=root_dir),
                FinishTaskTool(),
            ]
        )


if __name__ == "__main__":
    import json

    ROOT = "/Users/matthewflood/workspace/siiv/photo_to_code"
    manager = ToolManager.default(root_dir=ROOT)
    schema = manager.get_tools_schema_list()
    as_string = json.dumps(schema, indent=2)
    print(as_string)
