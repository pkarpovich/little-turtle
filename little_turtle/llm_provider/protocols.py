from typing import Protocol, Any, Optional
from typing_extensions import TypedDict


class Tool(TypedDict):
    type: str
    name: str
    max_uses: int


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
    
    def generate_image(
        self,
        instructions: str,
        input_text: str,
        **kwargs
    ) -> str:
        ...
    
    def get_search_tool(self) -> Optional[Tool]:
        ...