"""LLM module with factory pattern for creating LLM clients."""

from typing import Dict, Any
from .base import LLMClient
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient


def create_llm_client(config: Dict[str, Any]) -> LLMClient:
    """Factory function to create appropriate LLM client based on configuration.
    
    Args:
        config: Dictionary containing LLM configuration with 'provider' key
        
    Returns:
        Configured LLM client instance
        
    Raises:
        ValueError: If unsupported LLM provider is specified
    """
    provider = config.get("provider", "openai").lower()
    
    if provider == "openai":
        return OpenAIClient(config)
    elif provider == "anthropic":
        return AnthropicClient(config)
    else:
        supported_providers = ["openai", "anthropic"]
        raise ValueError(
            f"Unsupported LLM provider: '{provider}'. "
            f"Supported providers: {', '.join(supported_providers)}"
        )


__all__ = ["LLMClient", "OpenAIClient", "AnthropicClient", "create_llm_client"]