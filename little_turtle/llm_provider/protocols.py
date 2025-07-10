from typing import Protocol, Any


class LLMResponse(Protocol):
    content: str
    raw_response: Any


class LLMClient(Protocol):
    
    def create_completion(
        self, 
        messages: list[dict[str, str]], 
        **kwargs
    ) -> LLMResponse:
        ...
    
    def create_completion_with_tools(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]],
        **kwargs
    ) -> LLMResponse:
        ...