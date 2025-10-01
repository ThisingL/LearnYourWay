"""学习素材生成功能测试"""

import pytest

from app.services.material_generator import (
    QuizGenerator,
    MindMapGenerator,
    ImmersiveTextGenerator,
    get_quiz_generator,
    get_mindmap_generator,
    get_immersive_generator,
)


class TestQuizGenerator:
    """测验题生成器测试"""
    
    @pytest.mark.skip(reason="需要 LLM API 调用")
    async def test_generate_quiz(self):
        """测试生成测验题"""
        generator = QuizGenerator()
        
        content = "光合作用是植物利用光能将二氧化碳和水转化为葡萄糖和氧气的过程。"
        profile = {
            "grade": 5,
            "interests": ["足球", "科学实验"]
        }
        
        result = await generator.generate(content, profile, count=10)
        
        assert "questions" in result
        assert len(result["questions"]) == 10
        assert generator.validate(result)
    
    def test_validate_quiz(self):
        """测试测验题验证"""
        generator = QuizGenerator()
        
        # 有效的测验题
        valid_quiz = {
            "questions": [
                {
                    "id": "q1",
                    "type": "single",
                    "stem": "题目",
                    "options": ["A", "B", "C", "D"],
                    "answer": "A",
                    "explanation": "解析",
                    "difficulty": 3,
                }
            ]
        }
        assert generator.validate(valid_quiz) is True
        
        # 缺少必需字段
        invalid_quiz = {
            "questions": [
                {
                    "id": "q1",
                    "type": "single",
                    "stem": "题目",
                }
            ]
        }
        assert generator.validate(invalid_quiz) is False
        
        # 无效的题型
        invalid_type_quiz = {
            "questions": [
                {
                    "id": "q1",
                    "type": "invalid_type",
                    "stem": "题目",
                    "answer": "A",
                    "explanation": "解析",
                    "difficulty": 3,
                }
            ]
        }
        assert generator.validate(invalid_type_quiz) is False
        
        # 无效的难度
        invalid_difficulty_quiz = {
            "questions": [
                {
                    "id": "q1",
                    "type": "single",
                    "stem": "题目",
                    "answer": "A",
                    "explanation": "解析",
                    "difficulty": 10,
                }
            ]
        }
        assert generator.validate(invalid_difficulty_quiz) is False
    
    def test_mock_questions(self):
        """测试模拟题目生成"""
        generator = QuizGenerator()
        
        questions = generator._generate_mock_questions(5, 5, ["足球"])
        
        assert len(questions) >= 4  # 至少有基础的4道题
        assert all(q["type"] in ["single", "multi", "tf", "short"] for q in questions)
        assert any("足球" in q["stem"] for q in questions)  # 应该包含兴趣相关内容


class TestMindMapGenerator:
    """思维导图生成器测试"""
    
    @pytest.mark.skip(reason="需要 LLM API 调用")
    async def test_generate_mindmap(self):
        """测试生成思维导图"""
        generator = MindMapGenerator()
        
        content = "光合作用是植物利用光能将二氧化碳和水转化为葡萄糖和氧气的过程。"
        profile = {
            "grade": 5,
            "interests": ["足球", "科学实验"]
        }
        
        result = await generator.generate(content, profile)
        
        assert "nodes" in result
        assert "edges" in result
        assert len(result["nodes"]) > 0
        assert generator.validate(result)
    
    def test_validate_mindmap(self):
        """测试思维导图验证"""
        generator = MindMapGenerator()
        
        # 有效的思维导图
        valid_mindmap = {
            "nodes": [
                {"id": "node1", "label": "概念1", "type": "root"},
                {"id": "node2", "label": "概念2", "type": "concept"},
            ],
            "edges": [
                {"source": "node1", "target": "node2", "label": "关系"},
            ]
        }
        assert generator.validate(valid_mindmap) is True
        
        # 缺少节点字段
        invalid_mindmap = {
            "nodes": [
                {"id": "node1", "label": "概念1"},
            ],
            "edges": []
        }
        assert generator.validate(invalid_mindmap) is False
        
        # 边引用不存在的节点
        invalid_edge_mindmap = {
            "nodes": [
                {"id": "node1", "label": "概念1", "type": "root"},
            ],
            "edges": [
                {"source": "node1", "target": "node_nonexistent", "label": "关系"},
            ]
        }
        assert generator.validate(invalid_edge_mindmap) is False
    
    def test_mock_mindmap(self):
        """测试模拟思维导图生成"""
        generator = MindMapGenerator()
        
        mindmap = generator._generate_mock_mindmap(["足球"])
        
        assert "nodes" in mindmap
        assert "edges" in mindmap
        assert len(mindmap["nodes"]) > 0
        assert len(mindmap["edges"]) > 0
        
        # 检查节点ID的唯一性
        node_ids = [node["id"] for node in mindmap["nodes"]]
        assert len(node_ids) == len(set(node_ids))
        
        # 检查有根节点
        assert any(node["type"] == "root" for node in mindmap["nodes"])


class TestImmersiveTextGenerator:
    """沉浸式文本生成器测试"""
    
    @pytest.mark.skip(reason="需要 LLM API 调用")
    async def test_generate_immersive(self):
        """测试生成沉浸式文本"""
        generator = ImmersiveTextGenerator()
        
        content = "光合作用是植物利用光能将二氧化碳和水转化为葡萄糖和氧气的过程。"
        profile = {
            "grade": 5,
            "interests": ["足球", "科学实验"]
        }
        
        result = await generator.generate(content, profile)
        
        assert "sections" in result
        assert len(result["sections"]) > 0
        assert generator.validate(result)
    
    def test_validate_immersive(self):
        """测试沉浸式文本验证"""
        generator = ImmersiveTextGenerator()
        
        # 有效的沉浸式文本
        valid_immersive = {
            "sections": [
                {
                    "title": "章节标题",
                    "paragraphs": ["段落1", "段落2"]
                }
            ]
        }
        assert generator.validate(valid_immersive) is True
        
        # 缺少sections
        invalid_immersive = {
            "data": []
        }
        assert generator.validate(invalid_immersive) is False
        
        # 缺少必需字段
        invalid_section = {
            "sections": [
                {
                    "title": "章节标题"
                }
            ]
        }
        assert generator.validate(invalid_section) is False
    
    def test_mock_immersive(self):
        """测试模拟沉浸式文本生成"""
        generator = ImmersiveTextGenerator()
        
        immersive = generator._generate_mock_immersive(["足球"])
        
        assert "sections" in immersive
        assert len(immersive["sections"]) > 0
        
        # 检查每个章节的结构
        for section in immersive["sections"]:
            assert "title" in section
            assert "paragraphs" in section
            assert isinstance(section["paragraphs"], list)
            assert len(section["paragraphs"]) > 0
        
        # 检查是否包含插图占位符
        all_paragraphs = []
        for section in immersive["sections"]:
            all_paragraphs.extend(section["paragraphs"])
        
        has_image_placeholder = any("{{image:" in p for p in all_paragraphs)
        assert has_image_placeholder, "应该包含插图占位符"
        
        # 检查是否融入了兴趣
        all_text = " ".join(all_paragraphs)
        assert "足球" in all_text


def test_generator_singletons():
    """测试生成器单例"""
    quiz_gen1 = get_quiz_generator()
    quiz_gen2 = get_quiz_generator()
    assert quiz_gen1 is quiz_gen2
    
    mindmap_gen1 = get_mindmap_generator()
    mindmap_gen2 = get_mindmap_generator()
    assert mindmap_gen1 is mindmap_gen2
    
    immersive_gen1 = get_immersive_generator()
    immersive_gen2 = get_immersive_generator()
    assert immersive_gen1 is immersive_gen2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

