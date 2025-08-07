from typing import TypedDict

from little_turtle.prompts.prompts_provider import PromptsProvider
from little_turtle.llm_provider import LLMClient


class StoryAgentVariables(TypedDict):
    historical_event: str
    current_date: str
    language: str


class StoryAgent:
    def __init__(self, llm_client: LLMClient, prompts_provider: PromptsProvider):
        self.llm_client = llm_client
        self.prompts_provider = prompts_provider

    def run(self, prompt_vars: StoryAgentVariables) -> str:
        prompt = self.prompts_provider.format("little_turtle_story", prompt_vars)

        resp = self.llm_client.create_completion(
            messages=prompt.messages,
            temperature=1,
            model="gpt-5",
        )

        return resp.content
