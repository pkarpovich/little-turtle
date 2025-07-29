from abc import ABC, abstractmethod
from typing import Any, Optional

from little_turtle.app_config import AppConfig
from .protocols import LLMResponse, Tool


class BaseLLMAdapter(ABC):

    def __init__(self, config: AppConfig):
        self.config = config

    @abstractmethod
    def create_completion(
        self, messages: list[dict[str, str]], **kwargs
    ) -> LLMResponse:
        pass

    @abstractmethod
    def create_completion_with_tools(
        self, messages: list[dict[str, str]], tools: list[dict[str, Any]], **kwargs
    ) -> LLMResponse:
        pass

    def get_search_tool(self) -> Optional[Tool]:
        return None
