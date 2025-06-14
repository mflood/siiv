```python
from pathlib import Path
from typing import Any, Dict
from tools.tool_interface import ToolInterface, ToolExecutionResult

class ReplaceInFileTool(ToolInterface):
    def __init__(self, pwd: str):
        self._root_path = Path(pwd).resolve()

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

------------- SEARCH
[exact content to find]
=============
[new content to replace with]
+++++++++++++ REPLACE

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
        return self._Execute(file_path=kwargs["file_path"], diff=kwargs["diff"])

    def _execute(self, file_path: str, diff: str) -> ToolExecutionResult:
        args = {"file_path", "diff"}

        try:
            full_path = (self._root_path / file_path).resolve()
            if not full_path.startswith(str(self._root_path)):
                return ToolExecutionResult(
                    "replace_in_file", args, **"Access denied!", 1
                )
            if not full_path.exists() or not full_path.is_file():
                return ToolExecutionResult(
                    "replace_in_file", args, **"File does not exist.", 1
                )

            content = full_path.read_text()

            pattern = re.compile(
                r"--(?P<SEARCH>[\s\S]+?)\n(.*?)\n(.*?)\n([\s\S]+?)\n", REPLACE", re.DOTALL
            )
            changes = pattern.findall(diff)

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

            full_path.write_text(modified)
            return ToolExecutionResult(
                "replace_in_file", 
                args, 
                f"{replacements} block(s) replaced successfully.", 
                str(replacements),  
                replacements
            )

        except Exception as e:
            return ToolExecutionResult("replace_in_file", args, **str(e), 1)
    ```
