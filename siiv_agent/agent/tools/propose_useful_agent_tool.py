import json
from agent.tools.tool_interface import ToolExecutionResult, ToolInterface
from typing import Dict, Any


class ProposeUsefulAgentTool(ToolInterface):
    
    def __init__(self):
        self.proposals = []

    def propose_tool(self, task_description, issues_encountered, suggested_tool, user_prompt, additional_notes=""):
        # Create a proposal dictionary
        proposal = {
            "task_description": task_description,
            "issues_encountered": issues_encountered,
            "suggested_tool": suggested_tool,
            "user_prompt": user_prompt,
            "additional_notes": additional_notes
        }

        # Store the proposal
        self.proposals.append(proposal)

        # Return the formatted proposal
        return self.format_proposal(proposal)

    def format_proposal(self, proposal):
        # Format the proposal as a JSON string for easy readability
        return json.dumps(proposal, indent=4)

    def get_all_proposals(self):
        # Return all collected proposals
        return [self.format_proposal(proposal) for proposal in self.proposals]

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "propose_useful_agent",
                "description": "Proposes a new tool that could assist in completing the current task more effectively. This tool captures the task description, issues encountered, a suggestion for a new tool, the user prompt given to the LLM, and any additional notes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_description": {
                            "type": "string",
                            "description": "A brief description of the task being attempted."
                        },
                        "issues_encountered": {
                            "type": "string",
                            "description": "Any challenges faced while completing the task."
                        },
                        "suggested_tool": {
                            "type": "string",
                            "description": "A description of the proposed new tool."
                        },
                        "user_prompt": {
                            "type": "string",
                            "description": "The prompt given to the LLM while attempting the task."
                        },
                        "additional_notes": {
                            "type": "string",
                            "description": "Any additional information that might help in the proposal."
                        }
                    },
                    "required": ["task_description", "issues_encountered", "suggested_tool", "user_prompt"],
                },
            },
        }

    def execute(self, **kwargs) -> ToolExecutionResult:
        task_description = kwargs.get("task_description")
        issues_encountered = kwargs.get("issues_encountered")
        suggested_tool = kwargs.get("suggested_tool")
        user_prompt = kwargs.get("user_prompt")
        additional_notes = kwargs.get("additional_notes", "")

        proposal = self.propose_tool(task_description, issues_encountered, suggested_tool, user_prompt, additional_notes)

        return ToolExecutionResult(
            tool_name="propose_useful_agent",
            args=kwargs,
            stdout=proposal,
            stderr="",
            return_code=0,
        )


# Example Usage
if __name__ == "__main__":
    tool = ProposeUsefulAgentTool()

    # Example input (this should be dynamically set in real use)
    task_description = "Refactor a large module with multiple long functions."
    issues_encountered = "Difficulty in identifying which functions to refactor efficiently."
    suggested_tool = "Refactoring Assistant Tool that suggests refactoring based on code complexity."
    user_prompt = "Develop a prototype for a Refactoring Assistant Tool."
    additional_notes = "The tool should analyze function lengths and cyclomatic complexity."

    proposal = tool.propose_tool(task_description, issues_encountered, suggested_tool, user_prompt, additional_notes)
    print("Proposal for New Tool:")
    print(proposal)

