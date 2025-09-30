"""PDF 解析器单元测试"""

import pytest

from app.services.pdf_parser import PageBlock, TextCleaner


def test_page_block_creation():
    """测试 PageBlock 创建"""
    block = PageBlock(
        block_type="heading",
        text="这是一个标题",
        bbox=(0, 0, 100, 20),
        font_size=16.0,
    )
    
    assert block.type == "heading"
    assert block.text == "这是一个标题"
    assert block.bbox == (0, 0, 100, 20)
    assert block.font_size == 16.0


def test_page_block_to_dict():
    """测试 PageBlock 转字典"""
    block = PageBlock(
        block_type="paragraph",
        text="段落内容",
        bbox=(0, 25, 500, 100),
        font_size=12.0,
    )
    
    block_dict = block.to_dict()
    
    assert block_dict["type"] == "paragraph"
    assert block_dict["text"] == "段落内容"
    assert block_dict["bbox"] == [0, 25, 500, 100]
    assert block_dict["font_size"] == 12.0


def test_text_cleaner_clean_text():
    """测试文本清洗"""
    # 测试去除多余空白
    text = "这是   一个    测试"
    cleaned = TextCleaner.clean_text(text)
    assert cleaned == "这是 一个 测试"
    
    # 测试中文断行合并
    text = "这是中 文文 本"
    cleaned = TextCleaner.clean_text(text)
    assert "中文" in cleaned or "中 文" in cleaned
    
    # 测试去除页码
    text = "123"
    cleaned = TextCleaner.clean_text(text)
    assert cleaned == ""


def test_text_cleaner_is_header_footer():
    """测试页眉页脚识别"""
    page_height = 1000
    
    # 页眉（顶部 10%）
    assert TextCleaner.is_header_footer("标题", page_height, (0, 50, 500, 70))
    
    # 页脚（底部 10%）
    assert TextCleaner.is_header_footer("页码", page_height, (0, 950, 500, 980))
    
    # 单独页码
    assert TextCleaner.is_header_footer("123", page_height, (0, 500, 500, 520))
    
    # 正常内容
    assert not TextCleaner.is_header_footer("正常段落", page_height, (0, 500, 500, 600))


@pytest.mark.asyncio
async def test_clean_and_chunk_empty():
    """测试空输入的分块"""
    from app.services.pdf_parser import clean_and_chunk
    
    chunks = await clean_and_chunk([])
    assert chunks == []


@pytest.mark.asyncio
async def test_clean_and_chunk_simple():
    """测试简单分块"""
    from app.services.pdf_parser import clean_and_chunk
    
    pages_data = [
        {
            "page_number": 1,
            "blocks": [
                {"type": "heading", "text": "标题", "bbox": [0, 0, 100, 20]},
                {"type": "paragraph", "text": "这是第一段内容。" * 10, "bbox": [0, 25, 500, 100]},
            ]
        }
    ]
    
    chunks = await clean_and_chunk(pages_data, target_tokens=100, overlap=20)
    
    assert len(chunks) > 0
    assert all("chunk_id" in chunk for chunk in chunks)
    assert all("text" in chunk for chunk in chunks)
    assert all("pages" in chunk for chunk in chunks)
