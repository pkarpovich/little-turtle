from typing import TypedDict, List

from little_turtle.prompts.prompts_provider import PromptsProvider
from little_turtle.services import AppConfig
from little_turtle.llm_provider import LLMClient


class TurtleStoryChainVariables(TypedDict):
    historical_event: str
    current_date: str
    language: str


class TurtleStoryChain:
    def __init__(self, llm_client: LLMClient, prompts_provider: PromptsProvider):
        self.llm_client = llm_client
        self.prompts_provider = prompts_provider

    def run(self, prompt_vars: TurtleStoryChainVariables) -> str:
        resp = self.llm_client.create_completion(
            **self.prompts_provider.format("little_turtle_story", prompt_vars),
        )
        
        return resp.content