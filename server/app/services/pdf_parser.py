"""PDF 解析服务

使用 pymupdf (fitz) 进行 PDF 解析，提取文本、版式元素和结构信息
"""

import re
from pathlib import Path
from typing import Any

import fitz  # pymupdf


class PageBlock:
    """页面块"""

    def __init__(
        self,
        block_type: str,
        text: str,
        bbox: tuple[float, float, float, float],
        font_size: float = 0,
    ):
        self.type = block_type  # 'heading' | 'paragraph' | 'list'
        self.text = text.strip()
        self.bbox = bbox  # (x0, y0, x1, y1)
        self.font_size = font_size

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "text": self.text,
            "bbox": list(self.bbox),
            "font_size": self.font_size,
        }


class PDFParser:
    """PDF 解析器"""

    def __init__(self):
        # 标题识别阈值（字体大小）
        self.heading_font_threshold = 14.0

    def parse_pdf(self, file_path: Path) -> dict[str, Any]:
        """
        解析 PDF 文件

        Returns:
            {
                "filename": str,
                "total_pages": int,
                "pages": [
                    {
                        "page_number": 1,
                        "blocks": [
                            {"type": "heading", "text": "...", "bbox": [...], "font_size": 16},
                            {"type": "paragraph", "text": "...", "bbox": [...], "font_size": 12}
                        ]
                    }
                ]
            }
        """
        doc = fitz.open(file_path)
        pages = []

        for page_num, page in enumerate(doc, 1):
            blocks = self._extract_blocks(page)
            pages.append({"page_number": page_num, "blocks": [b.to_dict() for b in blocks]})

        doc.close()

        return {
            "filename": file_path.name,
            "total_pages": len(pages),
            "pages": pages,
        }

    def _extract_blocks(self, page: fitz.Page) -> list[PageBlock]:
        """提取页面块元素"""
        blocks = []
        
        # 获取页面文本块（带格式信息）
        text_dict = page.get_text("dict")
        
        for block in text_dict.get("blocks", []):
            # 跳过图片块
            if block.get("type") == 1:  # 图片
                continue
            
            # 处理文本块
            if block.get("type") == 0:  # 文本
                text_lines = []
                max_font_size = 0
                
                for line in block.get("lines", []):
                    line_text = ""
                    for span in line.get("spans", []):
                        line_text += span.get("text", "")
                        font_size = span.get("size", 0)
                        max_font_size = max(max_font_size, font_size)
                    
                    if line_text.strip():
                        text_lines.append(line_text.strip())
                
                if text_lines:
                    text = " ".join(text_lines)
                    bbox = tuple(block.get("bbox", [0, 0, 0, 0]))
                    
                    # 判断块类型
                    block_type = self._classify_block(text, max_font_size)
                    
                    blocks.append(PageBlock(
                        block_type=block_type,
                        text=text,
                        bbox=bbox,
                        font_size=max_font_size,
                    ))
        
        return blocks

    def _classify_block(self, text: str, font_size: float) -> str:
        """分类块类型"""
        # 根据字体大小判断是否为标题
        if font_size >= self.heading_font_threshold:
            return "heading"
        
        # 判断是否为列表
        if re.match(r"^\s*[\d\-•·]\s+", text):
            return "list"
        
        return "paragraph"


class TextCleaner:
    """文本清洗器"""

    @staticmethod
    def clean_text(text: str) -> str:
        """清洗文本"""
        # 去除多余空白
        text = re.sub(r"\s+", " ", text)
        
        # 合并断行（中文）
        text = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", text)
        
        # 去除页眉页脚常见模式
        text = re.sub(r"^\d+\s*$", "", text)  # 单独的页码
        text = re.sub(r"^第\s*\d+\s*页", "", text)  # "第X页"
        
        return text.strip()

    @staticmethod
    def is_header_footer(text: str, page_height: float, bbox: tuple) -> bool:
        """判断是否为页眉页脚"""
        # 页眉：靠近顶部
        if bbox[1] < page_height * 0.1:
            return True
        
        # 页脚：靠近底部
        if bbox[3] > page_height * 0.9:
            return True
        
        # 单独的页码
        if re.match(r"^\d+$", text.strip()):
            return True
        
        return False


async def clean_and_chunk(
    pages_data: list[dict[str, Any]],
    target_tokens: int = 400,
    overlap: int = 50,
) -> list[dict[str, Any]]:
    """
    清洗和分块

    Args:
        pages_data: 页面数据
        target_tokens: 目标 token 数（约等于字符数的 60%）
        overlap: 重叠 token 数

    Returns:
        分块后的文本列表
    """
    cleaner = TextCleaner()
    chunks = []
    current_chunk = []
    current_length = 0
    chunk_id = 0
    
    # 提取所有文本块
    all_blocks = []
    for page in pages_data:
        page_number = page["page_number"]
        for block in page.get("blocks", []):
            # 清洗文本
            text = cleaner.clean_text(block["text"])
            if not text:
                continue
            
            # 跳过页眉页脚（简化判断）
            if len(text) < 5:
                continue
            
            all_blocks.append({
                "text": text,
                "type": block["type"],
                "page": page_number,
            })
    
    # 分块
    for block in all_blocks:
        text = block["text"]
        block_length = len(text)
        
        # 如果当前块太大，直接作为独立 chunk
        if block_length > target_tokens * 2:
            if current_chunk:
                chunks.append(_create_chunk(chunk_id, current_chunk))
                chunk_id += 1
                current_chunk = []
                current_length = 0
            
            # 大块拆分
            chunks.extend(_split_large_block(text, block["page"], chunk_id, target_tokens))
            chunk_id = len(chunks)
            continue
        
        # 如果加入当前块会超过目标长度
        if current_length + block_length > target_tokens and current_chunk:
            chunks.append(_create_chunk(chunk_id, current_chunk))
            chunk_id += 1
            
            # 保留重叠部分
            if overlap > 0 and current_chunk:
                overlap_text = current_chunk[-1]["text"][-overlap:]
                current_chunk = [{"text": overlap_text, "type": "paragraph", "page": block["page"]}]
                current_length = len(overlap_text)
            else:
                current_chunk = []
                current_length = 0
        
        # 添加到当前 chunk
        current_chunk.append(block)
        current_length += block_length
    
    # 处理最后一个 chunk
    if current_chunk:
        chunks.append(_create_chunk(chunk_id, current_chunk))
    
    return chunks


def _create_chunk(chunk_id: int, blocks: list[dict]) -> dict[str, Any]:
    """创建 chunk"""
    text = "\n".join(b["text"] for b in blocks)
    pages = list(set(b["page"] for b in blocks))
    
    return {
        "chunk_id": f"chunk_{chunk_id:04d}",
        "text": text,
        "tokens": len(text),  # 简化：使用字符数
        "pages": sorted(pages),
        "block_types": [b["type"] for b in blocks],
    }


def _split_large_block(text: str, page: int, start_id: int, target_size: int) -> list[dict]:
    """拆分大块"""
    chunks = []
    sentences = re.split(r"[。！？\n]", text)
    
    current = []
    current_len = 0
    
    for sent in sentences:
        if not sent.strip():
            continue
        
        if current_len + len(sent) > target_size and current:
            chunks.append({
                "chunk_id": f"chunk_{start_id + len(chunks):04d}",
                "text": "".join(current),
                "tokens": current_len,
                "pages": [page],
                "block_types": ["paragraph"],
            })
            current = []
            current_len = 0
        
        current.append(sent + "。")
        current_len += len(sent) + 1
    
    if current:
        chunks.append({
            "chunk_id": f"chunk_{start_id + len(chunks):04d}",
            "text": "".join(current),
            "tokens": current_len,
            "pages": [page],
            "block_types": ["paragraph"],
        })
    
    return chunks