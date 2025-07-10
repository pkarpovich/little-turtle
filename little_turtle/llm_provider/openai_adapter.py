from typing import Any
from openai import OpenAI

from little_turtle.services import AppConfig
from .base import BaseLLMAdapter
from .protocols import LLMResponse


class OpenAIResponse:
    
    def __init__(self, response):
        self.raw_response = response
        self.content = response.choices[0].message.content
        self.tool_calls = getattr(response.choices[0].message, 'tool_calls', None)
    
    def __str__(self):
        return self.content or ""


class OpenAIAdapter(BaseLLMAdapter):
    
    def __init__(self, config: AppConfig):
        super().__init__(config)
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL
    
    def create_completion(
        self, 
        messages: list[dict[str, str]], 
        **kwargs
    ) -> LLMResponse:
        response = self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,
            **{k: v for k, v in kwargs.items() if k != "model"}
        )
        
        return OpenAIResponse(response)
    
    def create_completion_with_tools(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]],
        **kwargs
    ) -> LLMResponse:
        response = self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,
            tools=tools,
            **{k: v for k, v in kwargs.items() if k not in ["model", "tools"]}
        )
        
        return OpenAIResponse(response)