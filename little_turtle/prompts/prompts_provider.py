from typing import TYPE_CHECKING, Mapping, Any

from phoenix.client import Client

if TYPE_CHECKING:
    from phoenix.client.types import PromptVersion


class PromptsProvider:
    @staticmethod
    def get_prompt(prompt_identifier: str) -> "PromptVersion":
        return Client().prompts.get(prompt_identifier=prompt_identifier)

    @staticmethod
    def format(prompt_identifier: str, prompt_vars: Mapping[str, Any]) -> any:
        prompt = PromptsProvider.get_prompt(prompt_identifier)
        return prompt.format(variables=prompt_vars)