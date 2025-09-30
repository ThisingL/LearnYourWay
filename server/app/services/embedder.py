"""嵌入服务

负责文本向量化，支持多种嵌入模型
"""

from typing import Any

from app.config import get_settings

settings = get_settings()


class Embedder:
    """文本嵌入器"""

    def __init__(self):
        # 暂时不导入 LLM provider，避免在没有配置时报错
        self.provider = None

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        嵌入文本列表

        Args:
            texts: 文本列表

        Returns:
            向量列表
        """
        if not texts:
            return []

        # TODO: 实际调用 LLM Provider 的 embed 方法
        # try:
        #     from app.services.llm_provider import get_llm_provider
        #     if not self.provider:
        #         self.provider = get_llm_provider()
        #     embeddings = await self.provider.embed(texts)
        #     return embeddings
        # except Exception as e:
        #     print(f"嵌入失败: {e}")
        #     # 返回占位向量
        #     return [[0.0] * 1536 for _ in texts]
        
        # 当前返回占位向量（1536 维，OpenAI embedding 标准维度）
        print(f"生成 {len(texts)} 个文本的占位向量（实际部署时会调用真实 API）")
        return [[0.0] * 1536 for _ in texts]

    async def embed_chunks(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        嵌入分块文本

        Args:
            chunks: 分块列表

        Returns:
            带向量的分块列表
        """
        texts = [chunk["text"] for chunk in chunks]
        embeddings = await self.embed_texts(texts)

        # 将向量添加到 chunk
        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding
            chunk["embedding_dim"] = len(embedding)

        return chunks