from enum import Enum
from agent.tools.list_files_tool import ListFilesTool
import datetime
import textwrap
from agent.tools.list_files_tool import ListFilesTool


def get_user_task_prompt() -> str:
    prompt_textfile = f"agent/prompt_text/current_state_message.txt"
    with open(prompt_textfile, "r") as f:
        return f.read()


def get_system_message(
    full_current_working_dir: str,
    default_shell="bin/zsh",
    home_dir="/Users/matthewflood",
    operating_system="macOS",
):

    prompt_textfile = f"agent/prompt_text/system_message.txt"
    with open(prompt_textfile, "r") as handle:
        content = handle.read()

    content = content.replace("[[full_current_working_dir]]", full_current_working_dir)
    content = content.replace("[[default_shell]]", default_shell)
    content = content.replace("[[operating_system]]", operating_system)
    content = content.replace("[[home_dir]]", home_dir)

    message = {"role": "system", "content": content}
    return message


def get_current_working_dir_filelist(full_current_working_dir: str) -> str:
    filelist = ListFilesTool(pwd=full_current_working_dir)
    results = filelist.execute(directory="", recursive=False)
    return results.to_llm_message()


def get_user_task_message(
    task: str, full_current_working_dir: str, current_time: datetime.datetime
):

    formatted_current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    current_working_dir_filelist = get_current_working_dir_filelist(
        full_current_working_dir
    )

    env_details = textwrap.dedent(
        f"""
    Current working directory: {full_current_working_dir}
    Current time: {formatted_current_time}
    Current working directory filelist: {current_working_dir_filelist}
    """
    )

    message = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": f"<task>\n{task}\n</task>",
            },
            {
                "type": "text",
                "text": f"<environment_details>\n{env_details}\n</environment_details>",
            },
        ],
    }
    return message


if __name__ == "__main__":

    current_working_dir = "/Users/matthewflood/workspace/siiv/photo_to_code"
    current_time = datetime.datetime.now()

    print(
        get_system_message(
            full_current_working_dir=current_working_dir,
            default_shell="bin/zsh",
            home_dir="/Users/matthewflood",
            operating_system="macOS",
        )
    )

    print(
        get_user_task_message(
            task="Find the file photo_to_code_batch.py",
            full_current_working_dir=current_working_dir,
            current_time=current_time,
        )
    )

# end
