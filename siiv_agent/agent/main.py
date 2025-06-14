import json
import logging
import pprint
import uuid
import demjson3

from cline_messages import get_system_message, get_user_task_message
from llm_client import LLMClient
from prompts import TaskTypeId, get_system_prompt
from retrieval import VectorClient
from tools.tool_manager import TaskCompleteError, ToolManager

vector_client = VectorClient.factory()
llm_client = LLMClient()

LOGGER_NAME = __name__

logger = logging.getLogger(LOGGER_NAME)
tool_manager = ToolManager.default()

import json
from typing import Any, Dict

class BadToolRequestError(Exception):
    pass

class NoToolRequestError(Exception):
    pass

class InvalidCommandJson(Exception):
    pass

def parse_tool_request_to_llm_format(text: str) -> dict:
    """
    Converts the last TOOL_REQUEST block into an LLM-style tool call dict.
    
    Args:
        text (str): The input string with [TOOL_REQUEST] JSON block.
    
    Returns:
        ... dict: Tool call in LLM function format.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.info('looking for TOOL_REQUEST block in text')

    end_idx = text.find('[END_TOOL_REQUEST]')
    if end_idx == -1:
        end_idx = text.rfind('[/TOOL_REQUEST]')

    if end_idx == -1:
        logger.info('No END_TOOL_REQUEST tag found')
        raise NoToolRequestError("Missing [END_TOOL_REQUEST] tag")
``````python
    end_idx = text.rfind("[/TOOL_REQUEST]")

    if end_idx == -1:
        logger.info("No END_TOOL_REQUEST tag found")
        raise NoToolRequestError("Missing [/END_TOOL_REQUEST] tag")

    start_tag = "[TOOL_REQUEST]"
    start_idx = text.rfind(start_tag, 0, end_idx)
    if start_idx == -1:
        logger.info("No TOOL_REQUEST tag found before END_TOOL_REQUEST")
        raise BadToolRequestError(
            "Missing [TOOL_REQUEST] tag before [/END_TOOL_REQUEST]"
        )

    block = text[start_idx + len(start_tag) : end_idx].strip()
    block = re.sub(r'\s+(\s*{', '{', block)

    try:
        logger.info("Attempting to parse json block: %s", block)

        raw_json = demjson3.decode(block)
        logger.error("Failed to parse TOOL_REQUEST JSON: %s", block)
        raise InvalidCommandJson(f"Invalid json provided for tool request: {e}")

    tool_call = {
        "id": str(uuid.uuid4()),
        "function": {
            "name": raw_json["name"],
            "arguments": json.dumps(raw_json["arguments"]),
        },
    }

    logger.info("Found tool call: %s", tool_call)
    return tool_call

    def write_contents_to_file(filepath: str, content: str) -> str:
        with open("generated_file.py", "w", encoding="utf-8") as handle:
            handle.write(content)
        return 'Success'

    def handle_pytest_query(query_text: str):

    # related_code_chunks = vector_client.retrieve(query_text=query_text, top_k=10)
    # context_string = vector_client.build_context_string(code_chunks=related_code_chunks)

    messages = [
        get_system_message({
          "full_current_working_dir": "/Users/matthew.flood/workspace/airflow-datawarehouse"
        }),
        get_user_task_message(task=query_text),
    ]

    tool_schema = tool_manager.get_tools_schema_list()

    logger.info("----------- START INVOCATION -------------")
    for message in messages:
        logger.info(
            "------- %s message ------",
            message["role"],
            message.get("tool_call_id", ""),
        )
        pprint.pprint(message)

    logger.info("----------- END INVOCATION -------------")

    while True:
        chat_and_tool_response = llm_client.call_chat(
            messages=messages,
            tool_schema=tool_schema,
        )

        tool_calls = []
        if chat_and_tool_response.tool_calls:
            tool_calls = chat_and_tool_response.tool_calls
            logger.info(
                "The LLM response included %d explicit tool calls", len(tool_calls)
            )
        else:
            try:
                tool_call = parse_tool_request_to_llm_format(
                    text=chat_and_tool_response.content
                )
                tool_calls = [tool_call]
            except NoToolRequestError:
                logger.error("Got a message without a tool")
                message = {"role": "assistant", "content": chat_and_tool_response.content}
                logger.error(message)
                messages.append(message)

                message = {"role": "user", "content": "You did not call a tool. You must call a tool"}
                logger.error(message)
                messages.append(message)

            except BadToolRequestError as e:
                message = {
                    "role": "user",
                    "text": f"Your call was not formatted correctly. You must make a valid tool call. Error: {e}",
                }
                logger.error(message)
                messages.append(message)
            except InvalidCommandJson as e:

                message = {"role": "assistant", "content": chat_and_tool_response.content}
                logger.error(message)
                messages.append(message)

                message = {"role": "user", "content": f"Your tool call was not valid json. Error: {e}"}
                logger.error(message)
                messages.append(message)

            if tool_calls:
                logger.info("Processing %d tool calls", len(tool_calls))
                assistant_message = {
                    "role": "assistant",
                    "tool_calls": chat_and_tool_response.tool_calls,
                }
                logger.info(assistant_message)
                messages.append(assistant_message)

                for tool_call in tool_calls:
                    tool_name = tool_call["function"]["name"]
                    args = json.loads(tool_call["function"]["arguments"])
                    logger.info("Invoking tool: %s with args: %s", tool_name, args)

                    try:
                        result = tool_manager.execute_tool_by_name(tool_name, args)
                    except TaskCompleteError as e:
                        logger.info("Got TaskComplete!!")
                        logger.info("Final message: %s", e)
                        return

                    if result is None:
                        tool_response_message = {
                            "role": "tool",
                            "name": tool_name,
                            "tool_call_id": tool_call["id"],
                            "content": f"Tool '{tool_name}' not found.",
                        }
                    else:
                        tool_response_message = {
                            "role": "tool",
                            "name": tool_name,
                            "tool_call_id": tool_call["id"],
                            "content": result.to_llm_message(),
                        }
                    logger.info(tool_response_message)
                    messages.append(tool_response_message)

if __name__ == "__main__":
    import my_logging

    query_text = "Determine why the DAG named 'ecs_se_gl_feed_stat_auto_report_dag' failed to produce a report on the expected days."
    handle_pytest_query(query_text)
