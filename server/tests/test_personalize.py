"""个性化改写功能测试

测试文档 04 部分的功能实现
"""

import pytest

from app.services.readability_service import ReadabilityService
from app.services.personalize_service import PersonalizeService


class TestReadabilityService:
    """阅读等级评估服务测试"""
    
    def test_flesch_reading_ease(self):
        """测试 Flesch 阅读容易度计算"""
        service = ReadabilityService()
        
        # 简单文本（小学低年级）
        simple_text = "小明去公园玩。他看到了很多花。花很漂亮。"
        score1 = service.calculate_flesch_reading_ease(simple_text)
        assert score1 > 60, "简单文本的可读性分数应该较高"
        
        # 复杂文本（中学）
        complex_text = "虽然光合作用的过程非常复杂，但是如果我们深入研究就会发现，它不仅能够将光能转化为化学能，而且还能够维持大气中氧气和二氧化碳的平衡。"
        score2 = service.calculate_flesch_reading_ease(complex_text)
        assert score2 < score1, "复杂文本的可读性分数应该较低"
    
    def test_estimate_grade_level(self):
        """测试年级水平估算"""
        service = ReadabilityService()
        
        # 简单文本
        simple_text = "小猫很可爱。它有白色的毛。"
        grade, confidence = service.estimate_grade_level(simple_text)
        assert grade <= 3, f"简单文本应该是低年级水平，但得到 {grade} 年级"
        assert confidence > 0, "置信度应该大于 0"
    
    def test_vocab_coverage(self):
        """测试词汇覆盖率计算"""
        service = ReadabilityService()
        
        # 使用目标年级的词汇
        text = "这是一个测试"
        coverage = service.calculate_vocab_coverage(text, target_grade=3)
        assert 0 <= coverage <= 1, "覆盖率应该在 0-1 之间"
    
    def test_analyze_readability(self):
        """测试综合可读性分析"""
        service = ReadabilityService()
        
        text = "地球围绕太阳转动。这个过程叫做公转。公转需要一年的时间。"
        result = service.analyze_readability(text, target_grade=4)
        
        assert "flesch_score" in result
        assert "estimated_grade" in result
        assert "confidence" in result
        assert "vocab_coverage" in result
        assert "avg_sentence_length" in result
        assert "assessment" in result
        assert "suggestions" in result
        assert isinstance(result["suggestions"], list)


class TestPersonalizeService:
    """个性化改写服务测试（需要 LLM，暂时跳过）"""
    
    @pytest.mark.skip(reason="需要 LLM API 调用")
    async def test_personalize_text(self):
        """测试个性化改写"""
        service = PersonalizeService()
        
        original_text = "光合作用是植物利用光能将二氧化碳和水转化为葡萄糖和氧气的过程。"
        result = await service.personalize_text(
            original_text=original_text,
            grade=5,
            interests=["足球", "科学实验"],
            must_keep_terms=["光合作用", "二氧化碳", "葡萄糖"],
        )
        
        assert "personalized_text" in result
        assert "original_readability" in result
        assert "personalized_readability" in result
        assert "improvement" in result
        
        # 验证术语保留
        personalized = result["personalized_text"]
        assert "光合作用" in personalized
        assert "二氧化碳" in personalized
        assert "葡萄糖" in personalized
    
    @pytest.mark.skip(reason="需要 LLM API 调用")
    async def test_validate_personalization(self):
        """测试改写质量验证"""
        service = PersonalizeService()
        
        original_text = "牛顿第一定律指出，物体在不受外力作用时保持静止或匀速直线运动。"
        personalized_text = "牛顿第一定律说的是：如果没有力推或拉一个物体，它就会保持不动，或者一直按照同样的速度走直线。就像在足球场上，如果你不踢球，球就会停在那里。"
        
        result = await service.validate_personalization(
            original_text=original_text,
            personalized_text=personalized_text,
            must_keep_terms=["牛顿第一定律"],
        )
        
        assert "is_valid" in result
        assert "issues" in result
        assert "term_coverage" in result
        assert result["term_coverage"] == 1.0, "所有术语都应该被保留"


def test_readability_service_singleton():
    """测试可读性服务单例"""
    from app.services.readability_service import get_readability_service
    
    service1 = get_readability_service()
    service2 = get_readability_service()
    
    assert service1 is service2, "应该返回同一个实例"


def test_personalize_service_singleton():
    """测试个性化服务单例"""
    from app.services.personalize_service import get_personalize_service
    
    service1 = get_personalize_service()
    service2 = get_personalize_service()
    
    assert service1 is service2, "应该返回同一个实例"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

