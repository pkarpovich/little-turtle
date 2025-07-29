from typing import Any, Optional
from anthropic import Anthropic

from little_turtle.app_config import AppConfig
from .base import BaseLLMAdapter
from .protocols import LLMResponse, Tool


class AnthropicResponse:
    def __init__(self, response):
        self.raw_response = response
        self.content = response.content[0].text if response.content else ""
        self.tool_calls = None
    
    def __str__(self):
        return self.content


class AnthropicAdapter(BaseLLMAdapter):
    
    def __init__(self, config: AppConfig):
        super().__init__(config)
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.model = config.ANTHROPIC_MODEL
    
    def create_completion(
        self, 
        messages: list[dict[str, str]], 
        **kwargs
    ) -> LLMResponse:
        anthropic_messages = self._convert_messages(messages)
        
        response = self.client.messages.create(
            model=kwargs.get("model", self.model),
            messages=anthropic_messages,
            max_tokens=kwargs.get("max_tokens", 1024),
            **{k: v for k, v in kwargs.items() if k not in ["model", "max_tokens"]}
        )
        
        return AnthropicResponse(response)
    
    def create_completion_with_tools(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]],
        **kwargs
    ) -> LLMResponse:
        anthropic_messages = self._convert_messages(messages)
        
        response = self.client.messages.create(
            model=kwargs.get("model", self.model),
            messages=anthropic_messages,
            tools=tools,
            max_tokens=kwargs.get("max_tokens", 1024),
            **{k: v for k, v in kwargs.items() if k not in ["model", "tools", "max_tokens"]}
        )
        
        return AnthropicResponse(response)
    
    def _convert_messages(self, messages: list[dict[str, str]]) -> list[dict[str, str]]:
        converted = []
        for msg in messages:
            if msg["role"] == "system":
                converted.append({"role": "user", "content": f"System: {msg['content']}"})
            else:
                converted.append(msg)
        return converted
    
    def generate_image(
        self,
        instructions: str,
        input_text: str,
        **kwargs
    ) -> str:
        raise NotImplementedError("Anthropic adapter does not support image generation")
    
    def get_search_tool(self) -> Optional[Tool]:
        return {
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 5
        }