import subprocess
from typing import Any, Dict, List
from tools.tool_interface import ToolInterface, ToolExecutionResult


class ExecuteCommandTool(ToolInterface):

    def __init__(self, pwd: str, allowed_commands: List[str] = None):
        # Optional safety: restrict which commands can be executed
        self._pwd = pwd
        self._allowed_commands = allowed_commands or []

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "execute_command",
                "description": (
                    "Request to execute a CLI command on the system. "
                    "Commands will be executed using the /bin/zsh shell by default. "
                    "Use this when you need to perform system operations or run "
                    "specific commands to accomplish any step in the user's task. "
                    "For safety tailor your command to the user's system and provide "
                    "a clear explanation of what the command does. "
                    "Additionally, please use the appropriate chaining syntax for "
                    "the user's shell. Prefer to execute complex CLI commands over "
                    "executive scripts, as they are more flexible and easier "
                    "Commands will be executed in the current working directory: "
                    f"{self._pwd}"
                    "\n"
                    "allowed_commands"
                    ", ".join(self._allowed_commands)
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": (
                                "The CLI command to execute. This should be valid for "
                                "the current operating system (macOS). Ensure the command "
                                "is properly formatted and does not contain any harmful instructions."
                            ),
                        },
                        "requires_approval": {
                            "type": "boolean",
                            "description": (
                                "A boolean indicating whether this command requires explicit user "
                                "approval before execution in case the user has auto-approve mode enabled. "
                                "Set to 'true' for potentially impactful operations like installing/uninstalling "
                                "packages, deleting/overwriting files, system configuration changes, network "
                                "operations, or any commands that could have unintended side effects. "
                                "Set to 'false' for safe operations like reading files/directories, "
                                "running development servers, building projects, and other non-destructive operations."
                            ),
                        },
                    },
                    "required": ["command", "requires_approval"],
                },
            },
        }

    def execute(self, **kwargs) -> ToolExecutionResult:
        command = kwargs["command"]
        return self._execute(command)

    def _execute(self, command: str) -> ToolExecutionResult:
        args = {"command": command}

        # Optional: validate against allowed commands
        if self._allowed_commands and not any(
            command.startswith(cmd) for cmd in self._allowed_commands
        ):
            return ToolExecutionResult(
                tool_name="execute_command",
                args=args,
                stdout="",
                stderr=f"Command not allowed: {command}",
                return_code=1,
            )

        try:
            result = subprocess.run(
                command, shell=True, check=False, capture_output=True, text=True
            )
            return ToolExecutionResult(
                tool_name="execute_command",
                args=args,
                stdout=result.stdout.strip(),
                stderr=result.stderr.strip(),
                return_code=result.returncode,
            )

        except Exception as e:
            return ToolExecutionResult(
                tool_name="execute_command",
                args=args,
                stdout="",
                stderr=str(e),
                return_code=1,
            )


if __name__ == "__main__":
    tool = ExecuteCommandTool(
        pwd="/Users/matthew.flood/workspace/airflow-datawarehouse",
        allowed_commands=["ls", "echo", "whoami", "pwd"],
    )

    result = tool.execute("ls -la")
    content = result.to_llm_message()
    print(content)

# end
