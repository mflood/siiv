import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional

import requests

# from agent.tools.tool_manager import ToolManager


LOGGER_NAME = __name__


LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
LM_MODEL = "gemma-2-9b-tf"
LM_MODEL = "codestral-22b-v0.1"
LM_MODEL = "openhermes-2-5-mistral-7b"
LM_MODEL = "mistral-7b-instruct-v0.2"
LM_MODEL = "gemma-2-9b-pl"
LM_MODEL = "deepset/deepset-k1-6528-qwen3-8b"
LM_MODEL = "google/gemma-3-12b"
LM_API_KEY = "whatever"


@dataclass
class ChatAndToolResponse:
    content: Optional[str]
    tool_calls: List[Any]


class LLMClient:
    def __init__(self):
        self._model = LM_MODEL
        self._url = LM_STUDIO_URL
        self._api_key = LM_API_KEY
        self._logger = logging.getLogger(LOGGER_NAME)

    def call_chat(
        self, messages: List[dict], tool_schema=dict, temperature=0.8, max_tokens=8192
    ):
        headers = {}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "n": 1,
            "tools": [],
            "tool_choice": "auto",
        }

        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S") + f"_{now.microsecond // 1000:03d}"

        with open(f"_llm_request_{timestamp}.log", "w", encoding="utf-8") as handle:
            as_string = json.dumps(payload, indent=2)
            handle.write(as_string)

        # del payload['max_tokens']
        response = requests.post(self._url, headers=headers, json=payload)

        if response.status_code != 200:
            self._logger.error(
                "LLM call failed: %s %s", response.status_code, response.text
            )
            raise Exception(f"LLM call failed: {response.status_code} {response.text}")

        data = response.json()

        with open(f"_llm_response_{timestamp}.log", "w", encoding="utf-8") as handle:
            as_string = json.dumps(data, indent=2)
            handle.write(as_string)

        try:
            content = data["choices"][0]["message"].get("content")
            tool_calls = data["choices"][0]["message"].get("tool_calls")
            return ChatAndToolResponse(content=content, tool_calls=tool_calls)
        except Exception:
            print("Exception!!!!")
            print(data)


if __name__ == "__main__":

    import agent.my_logging

    messages = [
        {
            "role": "system",
            "content": "You are a cheerful and helpful agent. Provide answers as complete sentences and include fun emojis. Don't use a tool if you already know the answer. The only tool available is onnect_to_file. Do not use that tool unless instructed to.",
        },
        {"role": "user", "content": "What is the wisest thing anyone has ever said?"},
    ]

    client = LLMClient()

    response = client.call_chat(messages=messages, tool_schema=[])

    print(response)
