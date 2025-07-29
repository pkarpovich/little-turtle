from little_turtle.app_config import AppConfig
from .types import ProviderType
from .protocols import LLMClient
from .base import BaseLLMAdapter
from .openai_adapter import OpenAIAdapter
from .anthropic_adapter import AnthropicAdapter


class LLMProvider:

    def __init__(self, config: AppConfig):
        self.config = config
        self._adapters = {
            ProviderType.OPENAI: OpenAIAdapter,
            ProviderType.ANTHROPIC: AnthropicAdapter,
        }

    def build(self, provider: ProviderType) -> LLMClient:
        if provider not in self._adapters:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Available providers: {list(self._adapters.keys())}"
            )

        adapter_class = self._adapters[provider]
        return adapter_class(self.config)

    def register_adapter(
        self, provider: str, adapter_class: type[BaseLLMAdapter]
    ) -> None:
        self._adapters[provider] = adapter_class
