"""LLM Provider 抽象层

不使用 LangChain，通过 Protocol 定义接口，支持多家 LLM 厂商切换
"""

from typing import Any, Protocol

from app.config import get_settings

settings = get_settings()


class LLMProvider(Protocol):
    """LLM 提供商接口"""

    async def complete(self, prompt: str, **kwargs) -> str:
        """文本补全"""
        ...

    async def chat(self, messages: list[dict[str, str]], **kwargs) -> str:
        """对话补全"""
        ...

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """文本嵌入"""
        ...


class OpenAIProvider:
    """OpenAI Provider 实现"""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        # TODO: 初始化 OpenAI 客户端
        # from openai import AsyncOpenAI
        # self.client = AsyncOpenAI(api_key=api_key)

    async def complete(self, prompt: str, **kwargs) -> str:
        """文本补全"""
        # TODO: 实现 OpenAI API 调用
        # response = await self.client.completions.create(...)
        return f"[OpenAI] {prompt[:50]}..."

    async def chat(self, messages: list[dict[str, str]], **kwargs) -> str:
        """对话补全"""
        # TODO: 实现 OpenAI Chat API 调用
        # response = await self.client.chat.completions.create(
        #     model=self.model,
        #     messages=messages,
        #     **kwargs
        # )
        # return response.choices[0].message.content
        return f"[OpenAI Chat] Response to {len(messages)} messages"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """文本嵌入"""
        # TODO: 实现 OpenAI Embedding API 调用
        # response = await self.client.embeddings.create(
        #     model=settings.embedding_model,
        #     input=texts
        # )
        # return [item.embedding for item in response.data]
        return [[0.1] * 1536 for _ in texts]  # 占位


class AnthropicProvider:
    """Anthropic (Claude) Provider 实现"""

    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307"):
        self.api_key = api_key
        self.model = model

    async def complete(self, prompt: str, **kwargs) -> str:
        """文本补全"""
        return f"[Anthropic] {prompt[:50]}..."

    async def chat(self, messages: list[dict[str, str]], **kwargs) -> str:
        """对话补全"""
        return f"[Anthropic Chat] Response to {len(messages)} messages"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """文本嵌入 - Anthropic 不提供嵌入，使用 Voyage AI 或其他"""
        raise NotImplementedError("Anthropic does not provide embeddings")


def get_llm_provider() -> LLMProvider:
    """根据配置获取 LLM Provider"""
    provider_name = settings.llm_provider.lower()
    
    if provider_name == "openai":
        return OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.llm_model,
        )
    elif provider_name == "anthropic":
        return AnthropicProvider(
            api_key=settings.anthropic_api_key,
            model=settings.llm_model,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")
