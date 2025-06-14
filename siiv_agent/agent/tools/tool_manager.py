from typing import Any, Dict, List, Optional

from agent.tools.tool_interface import ToolInterface, ToolExecutionResult
from agent.tools.execute_command_tool import ExecuteCommandTool
from agent.tools.list_files_tool import ListFilesTool
from agent.tools.read_file_tool import ReadFileTool
from agent.tools.search_files_tool import SearchFilesTool
from agent.tools.write_to_file_tool import WriteToFileTool
from agent.tools.find_file_tool import FindFileTool
from agent.tools.list_code_definition_names_tool import ListCodeDefinitionNamesTool
from agent.tools.ask_merlin_for_information_tool import AskMerlinForInformationTool
from agent.tools.finish_task_tool import FinishTaskTool

ROOT = "/Users/matthewflood/workspace/siiv/photo_to_code"

class TaskCompleteError(Exception):
    pass

class ToolManager:

    def __init__(self, tool_list: List[ToolInterface]):
        self._tool_list = tool_list

        self._tool_map = {}
        for tool in tool_list:
            print(tool)
            schema = tool.get_schema()
            function_name = schema['function']['name']
            self._tool_map[function_name] = tool

    def get_tools_schema_list(self) -> List[dict]:
        return [tool.get_schema() for tool in self._tool_list]

    def execute_tool_by_name(
        self, name: str, args: Dict[str, Any]
    ) -> Optional[ToolExecutionResult]:
        tool = self._tool_map.get(name)
        return tool.execute(**args) if tool else None

    @classmethod
    def default(cls) -> "ToolManager":
        return cls(
            [
                ExecuteCommandTool(
                    pwd=ROOT,
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
                ListFilesTool(pwd=ROOT),
                ReadFileTool(pwd=ROOT),
                # ReplaceInFileTool(pwd=ROOT),
                SearchFilesTool(root_path=ROOT),
                WriteToFileTool(root_path=ROOT),
                FindFileTool(pwd=ROOT),
                ListCodeDefinitionNamesTool(pwd=ROOT),
                AskMerlinForInformationTool(pwd=ROOT),
                FinishTaskTool(),
            ]
        )


if __name__ == "__main__":
    import json

    manager = ToolManager.default()
    schema = manager.get_tools_schema_list()
    as_string = json.dumps(schema, indent=2)
    print(as_string)
