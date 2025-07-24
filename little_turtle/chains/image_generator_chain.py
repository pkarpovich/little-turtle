from typing import TypedDict

from little_turtle.prompts.prompts_provider import PromptsProvider
from little_turtle.llm_provider import LLMClient


class ImageGeneratorChainVariables(TypedDict):
    story: str


class ImageGeneratorChain:
    def __init__(self, llm_client: LLMClient, prompts_provider: PromptsProvider):
        self.prompts_provider = prompts_provider
        self.llm_client = llm_client

    def run(self, prompt_vars: ImageGeneratorChainVariables) -> str:
        prompt = self.prompts_provider.format("little_turtle_image", prompt_vars)

        return self.llm_client.generate_image(
            prompt.messages[0]['content'],
            prompt.messages[1]['content'],
            **prompt,
        )