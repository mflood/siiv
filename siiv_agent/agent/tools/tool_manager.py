class ToolManager:

    def __init__(self, tool_list: List[ToolInterface]):
        self._tool_list = tool_list

        self._tool_map = {
            tool.get_schema()["function"]["name"]: tool for tool in tool_list
        }

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
