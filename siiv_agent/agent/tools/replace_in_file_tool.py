from pathlib import Path
from typing import Any, Dict
from agent.tools.tool_interface import ToolInterface, ToolExecutionResult
import os
import re
import logging
LOGGER_NAME = __name__

class ReplaceInFileTool(ToolInterface):
    def __init__(self, pwd: str):
        self._root_path = pwd
        self._logger = logging.getLogger(LOGGER_NAME)

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "replace_in_file",
                "description": "Replace sections of content in an existing file using SEARCH/REPLACE blocks "
                               "that define exact changes to specific parts of the file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path of the file to modify (relative to the current working directory (self._root_path))",
                        },
                        "diff": {
                            "type": "string",
                            "description": """One or more SEARCH/REPLACE blocks following this exact format:

------- SEARCH
[exact content to find]
=======
[new content to replace with]
+++++++ REPLACE

Critical rules:
1. SEARCH content must match the associated file section to find EXACTLY:
    Match character-for-character, including whitespace, indentation, line endings
    Include all constructs, not strings, etc.
2. SEARCH/REPLACE blocks will only replace the first match occurrence.
    Including multiple lines in each SEARCH section if that is what you need to change.
    Including only single lines in SEARCH sections, unless the intent is not to change multiple lines.
    When in doubt, use smaller SEARCH/REPLACE blocks, unless the intent is to change the entire section.
3. Keep SEARCH/REPLACE blocks concise.
    Break large SEARCH/REPLACE blocks into a series of smaller blocks that each change a small portion
    of the file. If you have large SEARCH blocks, and a few surrounding lines that do not change,
    consider including just those changing lines in SEARCH/REPLACE blocks.
    Do not include long comments, or unchanging lines as they seem likely to change in future
    and need to be updated. Never truncate lines only for matching purposes as this can cause
    matching failures.
4. To move code: Use two SEARCH/REPLACE blocks (one to delete from original & one to insert
    at new location)
5. To delete code: Use empty REPLACE section",
"""
                       },
                   },
                   "required": ["file_path", "diff"],
               },
           }
       }

    
    def execute(self, **kwargs) -> ToolExecutionResult:
        return self._execute(file_path=kwargs["file_path"], diff=kwargs["diff"])

    def _execute(self, file_path: str, diff: str) -> ToolExecutionResult:
        args = {"file_path": file_path, "diff": diff}

        try:
            if not file_path.startswith("/"):
                file_path = os.path.join(self._root_path, file_path)

            if not file_path.startswith(str(self._root_path)):
                return ToolExecutionResult(
                    tool_name="replace_in_file",
                    args=args,
                    stdout="",
                    stderr="Access denied!",
                    return_code=1,
                )
            
            path_object = Path(file_path)
            if not path_object.exists() or not path_object.is_file():
                return ToolExecutionResult(
                    tool_name="replace_in_file",
                    args=args,
                    stdout="",
                    stderr="File does not exist.",
                    return_code=1,
                )

            self._logger.info(f"Reading file {file_path}")
            content = path_object.read_text()

            pattern = re.compile(
                r"-{7,} SEARCH\n(.*?)\n={7,}\n(.*?)\n\+{7,} REPLACE", re.DOTALL
            )
            changes = pattern.findall(diff)
            self._logger.info(f"Found {len(changes)} changes to make in {diff}. {changes}") 

            modified = content
            replacements = 0
            for search_text, replace_text in changes:
                if search_text not in modified:
                    return ToolExecutionResult(
                        "replace_in_file", args, 
                        f"", "SEARCH block not found:\n{search_text}", 1
                    )
                modified = modified.replace(search_text, replace_text, 1)
                replacements += 1

            self._logger.info(f"Writing file {file_path}")
            path_object.write_text(modified)
            return ToolExecutionResult(
                tool_name="replace_in_file",
                args=args,
                stdout=f"{replacements} block(s) replaced successfully.",
                stderr="",
                return_code=0,
            )

        except Exception as e:
            return ToolExecutionResult(
                tool_name="replace_in_file", 
                args=args,
                stdout="",
                stderr=str(e),
                return_code=1,
            )

if __name__ == "__main__":
    import agent.my_logging
    pwd = "/Users/matthewflood/workspace/siiv/photo_to_code/"
    tool = ReplaceInFileTool(pwd=pwd)
    results = tool.execute(file_path=f"replace_example.txt", diff=f"""
--------- SEARCH
FROG
=========
VEGETABLES                                             
+++++++++ REPLACE
""")
    print(results)
    content = results.to_llm_message()
    print(content)
