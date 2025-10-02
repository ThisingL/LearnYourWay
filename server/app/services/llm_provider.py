"""LLM Provider 抽象层

不使用 LangChain，通过 Protocol 定义接口，支持多家 LLM 厂商切换
"""

import json
from typing import Any, Protocol

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

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


class OpenAICompatibleProvider:
    """OpenAI 兼容 API Provider（支持 OpenAI、SiliconFlow 等）"""

    def __init__(
        self, 
        api_key: str, 
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )

    async def complete(self, prompt: str, **kwargs) -> str:
        """文本补全"""
        # 转为 chat 格式
        return await self.chat([{"role": "user", "content": prompt}], **kwargs)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def chat(self, messages: list[dict[str, str]], **kwargs) -> str:
        """
        对话补全
        
        Args:
            messages: 消息列表
            **kwargs: temperature, max_tokens 等参数
            
        Returns:
            LLM 生成的文本
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", settings.max_tokens),  # 从配置读取
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
            )
            
            response.raise_for_status()
            data = response.json()
            
            return data["choices"][0]["message"]["content"]
            
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP Error: {e.response.status_code}")
            print(f"Response: {e.response.text}")
            raise
        except Exception as e:
            print(f"❌ API 调用失败: {str(e)}")
            raise

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """
        文本嵌入
        
        注意：不是所有 OpenAI 兼容 API 都支持 embeddings
        """
        try:
            payload = {
                "model": settings.embedding_model,
                "input": texts,
            }
            
            response = await self.client.post(
                f"{self.base_url}/embeddings",
                json=payload,
            )
            
            response.raise_for_status()
            data = response.json()
            
            return [item["embedding"] for item in data["data"]]
            
        except Exception as e:
            print(f"⚠️ Embedding API 不可用，返回占位向量: {str(e)}")
            # 返回占位向量
            return [[0.0] * 1536 for _ in texts]

    async def close(self):
        """关闭连接"""
        await self.client.aclose()


class OpenAIProvider(OpenAICompatibleProvider):
    """OpenAI Provider（继承自兼容层）"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        super().__init__(
            api_key=api_key,
            model=model,
            base_url="https://api.openai.com/v1"
        )


class SiliconFlowProvider(OpenAICompatibleProvider):
    """硅基流动 Provider（继承自兼容层）"""
    
    def __init__(self, api_key: str, model: str = "Qwen/Qwen2.5-7B-Instruct"):
        super().__init__(
            api_key=api_key,
            model=model,
            base_url="https://api.siliconflow.cn/v1"
        )


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
    elif provider_name == "siliconflow":
        return OpenAICompatibleProvider(
            api_key=settings.openai_api_key,  # 复用 OPENAI_API_KEY 配置项
            model=settings.llm_model,
            base_url=settings.llm_base_url,  # 从配置读取 API 地址
        )
    elif provider_name == "anthropic":
        return AnthropicProvider(
            api_key=settings.anthropic_api_key,
            model=settings.llm_model,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")
