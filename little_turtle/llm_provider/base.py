from abc import ABC, abstractmethod
from typing import Any

from little_turtle.services import AppConfig
from .protocols import LLMResponse


class BaseLLMAdapter(ABC):
    
    def __init__(self, config: AppConfig):
        self.config = config
    
    @abstractmethod
    def create_completion(
        self, 
        messages: list[dict[str, str]], 
        **kwargs
    ) -> LLMResponse:
        pass
    
    @abstractmethod
    def create_completion_with_tools(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]],
        **kwargs
    ) -> LLMResponse:
        pass