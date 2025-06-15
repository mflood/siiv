from abc import ABC, abstractmethod

class LLMClientInterface(ABC):
    @abstractmethod
    def call_chat(self, messages: list, tool_schema: dict, temperature: float = 0.8, max_tokens: int = 8192):
        pass
