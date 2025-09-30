"""PDF 摄取任务

完整的 PDF 解析流程：上传 -> 解析 -> 清洗分块 -> 向量化 -> 存储
"""

import asyncio
from pathlib import Path

from app.services.embedder import Embedder
from app.services.pdf_parser import PDFParser, clean_and_chunk
from app.tasks.worker import celery_app


@celery_app.task(bind=True, name="ingest_pdf")
def ingest_pdf_task(self, file_path: str):
    """
    PDF 摄取任务
    
    Args:
        file_path: PDF 文件路径
        
    Returns:
        {
            "chunks": [...],
            "metadata": {...}
        }
    """
    try:
        # 阶段 1: 解析 PDF (10%)
        self.update_state(
            state="STARTED",
            meta={"stage": "parsing", "progress": 10},
        )
        
        parser = PDFParser()
        result = parser.parse_pdf(Path(file_path))
        
        # 阶段 2: 清洗与分块 (50%)
        self.update_state(
            state="STARTED",
            meta={"stage": "chunking", "progress": 50},
        )
        
        # 使用 asyncio.run 运行异步函数
        chunks = asyncio.run(clean_and_chunk(result["pages"]))
        
        # 阶段 3: 向量化 (80%)
        self.update_state(
            state="STARTED",
            meta={"stage": "embedding", "progress": 80},
        )
        
        embedder = Embedder()
        chunks_with_embeddings = asyncio.run(embedder.embed_chunks(chunks))
        
        # 阶段 4: 存储（暂时跳过，直接返回）(95%)
        self.update_state(
            state="STARTED",
            meta={"stage": "indexing", "progress": 95},
        )
        
        # TODO: 将 chunks 存储到向量数据库
        
        # 完成
        return {
            "filename": result["filename"],
            "total_pages": result["total_pages"],
            "chunks_count": len(chunks_with_embeddings),
            "chunks": [
                {
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text"][:100] + "..." if len(chunk["text"]) > 100 else chunk["text"],
                    "pages": chunk["pages"],
                    "tokens": chunk["tokens"],
                }
                for chunk in chunks_with_embeddings[:5]  # 只返回前5个用于预览
            ],
        }
    except FileNotFoundError:
        self.update_state(
            state="FAILURE",
            meta={"error": f"文件不存在: {file_path}"},
        )
        raise
    except Exception as e:
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)},
        )
        raise