import json
import logging
import os
import pprint
import time
from datetime import datetime
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
from agent.llm_clients.client_interface import LLMClientInterface
from agent.llm_client import ChatAndToolResponse

LOGGER_NAME = __name__

class OpenAiClient(LLMClientInterface):
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        self._client = OpenAI(api_key=api_key)
        self._logger = logging.getLogger(LOGGER_NAME)
        self._model = "gpt-4o-mini"
        self._max_tokens = 8192
        self._temperature = 0.8

    def call_chat(self, messages: List[dict], tool_schema=List[dict]):
        time.sleep(5)

        if tool_schema:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=self._temperature,
                tools=tool_schema,
                tool_choice="auto",
            )
        else:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=self._temperature,
            )

        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S") + f"_{now.microsecond // 1000:03d}"

        with open(f"_openai_response_{timestamp}.log", "w", encoding="utf-8") as handle:
            as_string = json.dumps(response.to_json(), indent=2)
            handle.write(as_string)

        try:
            choice = response.choices[0]
            content = choice.message.content
            tool_calls = choice.message.tool_calls
            return ChatAndToolResponse(content=content, tool_calls=tool_calls)
        except Exception as e:
            self._logger.error("Error parsing response: %s", e)
            raise

if __name__ == "__main__":
    from agent.my_logging import init_logging
    init_logging()
    messages = [{"role": "system", "content": "You are a cheerful and helpful agent. Provide answers as complete sentences and include fun emojis. Don't use a tool if you already know the answer. The only tool available is onnect_to_file. Do not use that tool unless instructed to."}, {"role": "user", "content": "What is the wisest thing anyone has ever said?"}]
    client = OpenAiClient()
    response = client.call_chat(messages=messages, tool_schema=[])
    print(response)
