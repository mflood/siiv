from enum import Enum


class TaskTypeId(Enum):
    """
    The type of task to be performed.
    """
    FIND_FILE = "find_file"

def get_system_prompt() -> str:

    prompt_textfile = f"agent/prompt_text/system_message.txt"
    with open(prompt_textfile, "r") as f:
        return f.read()

def get_user_task_prompt() -> str:
    prompt_textfile = f"agent/prompt_text/current_state_message.txt"
    with open(prompt_textfile, "r") as f:
        return f.read()


if __name__ == "__main__":
    print(get_system_prompt())
    print(get_user_task_prompt())  
    