"""阅读等级评估服务

提供可读性指标计算、年级词汇表匹配等功能
"""

import re
from typing import Dict, List, Tuple


class ReadabilityService:
    """阅读等级评估服务"""
    
    # 年级词汇表（简化示例，实际应从文件加载）
    GRADE_VOCABULARIES = {
        1: ["是", "的", "了", "我", "你", "他", "有", "在", "个", "人"],
        2: ["说", "会", "到", "来", "去", "看", "吃", "喝", "玩", "学"],
        3: ["因为", "所以", "但是", "虽然", "如果", "就", "还", "也", "都"],
        4: ["然而", "而且", "不仅", "而且", "因此", "所以", "然后", "接着"],
        5: ["显然", "实际上", "基本上", "事实上", "尤其", "特别", "尽管"],
    }
    
    # 简单句式模式（用于句子复杂度评估）
    COMPLEX_PATTERNS = [
        r"虽然.*但是",
        r"不仅.*而且",
        r"因为.*所以",
        r"如果.*就",
        r"只有.*才",
    ]
    
    def __init__(self):
        """初始化服务"""
        self.vocab_cache: Dict[int, set] = {}
        self._build_vocab_cache()
    
    def _build_vocab_cache(self):
        """构建词汇表缓存（累积式：高年级包含低年级词汇）"""
        accumulated_vocab = set()
        for grade in sorted(self.GRADE_VOCABULARIES.keys()):
            accumulated_vocab.update(self.GRADE_VOCABULARIES[grade])
            self.vocab_cache[grade] = accumulated_vocab.copy()
    
    def calculate_flesch_reading_ease(self, text: str) -> float:
        """
        计算 Flesch 阅读容易度（中文简化版）
        
        分数越高越容易阅读：
        - 90-100: 非常容易（小学低年级）
        - 60-90: 容易（小学高年级）
        - 30-60: 较难（中学）
        - 0-30: 很难（大学及以上）
        
        Args:
            text: 待评估文本
            
        Returns:
            可读性分数 (0-100)
        """
        # 去除标点和空格
        clean_text = re.sub(r'[^\u4e00-\u9fa5]', '', text)
        
        if len(clean_text) == 0:
            return 0.0
        
        # 统计字数
        char_count = len(clean_text)
        
        # 统计句子数（简化：按句号、问号、感叹号分割）
        sentences = re.split(r'[。！？]', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        if sentence_count == 0:
            sentence_count = 1
        
        # 计算平均句长
        avg_sentence_length = char_count / sentence_count
        
        # 计算复杂句式比例
        complex_count = sum(
            len(re.findall(pattern, text)) for pattern in self.COMPLEX_PATTERNS
        )
        complex_ratio = complex_count / sentence_count if sentence_count > 0 else 0
        
        # 简化的 Flesch 公式（针对中文调整）
        # 基础分数 100，减去句长和复杂度惩罚
        score = 100 - (avg_sentence_length * 1.5) - (complex_ratio * 20)
        
        return max(0.0, min(100.0, score))
    
    def estimate_grade_level(self, text: str) -> Tuple[int, float]:
        """
        估算文本的年级水平
        
        Args:
            text: 待评估文本
            
        Returns:
            (年级, 置信度)
        """
        flesch_score = self.calculate_flesch_reading_ease(text)
        
        # 根据 Flesch 分数映射到年级
        if flesch_score >= 80:
            grade = 1
        elif flesch_score >= 70:
            grade = 2
        elif flesch_score >= 60:
            grade = 3
        elif flesch_score >= 50:
            grade = 4
        elif flesch_score >= 40:
            grade = 5
        elif flesch_score >= 30:
            grade = 6
        else:
            grade = 7
        
        # 简化的置信度计算
        confidence = min(0.95, flesch_score / 100)
        
        return grade, confidence
    
    def calculate_vocab_coverage(self, text: str, target_grade: int) -> float:
        """
        计算文本在目标年级词汇表中的覆盖率
        
        Args:
            text: 待评估文本
            target_grade: 目标年级 (1-12)
            
        Returns:
            覆盖率 (0-1)
        """
        # 简化分词（实际应使用 jieba 等工具）
        # 这里使用字符级别的简化版本
        clean_text = re.sub(r'[^\u4e00-\u9fa5]', '', text)
        
        if len(clean_text) == 0:
            return 0.0
        
        # 获取目标年级的词汇表
        target_vocab = self.vocab_cache.get(min(target_grade, 5), set())
        
        if not target_vocab:
            return 0.5  # 默认值
        
        # 计算覆盖率（简化版：统计字符覆盖）
        matched_chars = sum(1 for char in clean_text if char in target_vocab)
        coverage = matched_chars / len(clean_text)
        
        return coverage
    
    def analyze_readability(self, text: str, target_grade: int) -> Dict:
        """
        综合分析文本可读性
        
        Args:
            text: 待评估文本
            target_grade: 目标年级
            
        Returns:
            {
                "flesch_score": float,
                "estimated_grade": int,
                "confidence": float,
                "vocab_coverage": float,
                "avg_sentence_length": float,
                "assessment": str,
                "suggestions": List[str]
            }
        """
        flesch_score = self.calculate_flesch_reading_ease(text)
        estimated_grade, confidence = self.estimate_grade_level(text)
        vocab_coverage = self.calculate_vocab_coverage(text, target_grade)
        
        # 计算平均句长
        clean_text = re.sub(r'[^\u4e00-\u9fa5]', '', text)
        sentences = re.split(r'[。！？]', text)
        sentence_count = len([s for s in sentences if s.strip()])
        avg_sentence_length = len(clean_text) / sentence_count if sentence_count > 0 else 0
        
        # 生成评估和建议
        assessment = self._generate_assessment(
            estimated_grade, target_grade, vocab_coverage, flesch_score
        )
        suggestions = self._generate_suggestions(
            estimated_grade, target_grade, vocab_coverage, avg_sentence_length
        )
        
        return {
            "flesch_score": round(flesch_score, 2),
            "estimated_grade": estimated_grade,
            "confidence": round(confidence, 2),
            "vocab_coverage": round(vocab_coverage, 2),
            "avg_sentence_length": round(avg_sentence_length, 1),
            "assessment": assessment,
            "suggestions": suggestions,
        }
    
    def _generate_assessment(
        self, estimated_grade: int, target_grade: int, vocab_coverage: float, flesch_score: float
    ) -> str:
        """生成评估结论"""
        grade_diff = estimated_grade - target_grade
        
        if abs(grade_diff) <= 1 and vocab_coverage >= 0.7:
            return f"✅ 文本难度适合{target_grade}年级学生阅读"
        elif grade_diff > 1:
            return f"⚠️ 文本难度偏高（约{estimated_grade}年级水平），建议简化"
        elif grade_diff < -1:
            return f"⚠️ 文本难度偏低（约{estimated_grade}年级水平），可适当提升"
        elif vocab_coverage < 0.7:
            return f"⚠️ 词汇覆盖率较低（{vocab_coverage:.1%}），建议调整用词"
        else:
            return "✅ 文本难度基本合适"
    
    def _generate_suggestions(
        self, estimated_grade: int, target_grade: int, vocab_coverage: float, avg_sentence_length: float
    ) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if estimated_grade > target_grade + 1:
            suggestions.append("使用更简单的词汇和表达方式")
        
        if avg_sentence_length > 20:
            suggestions.append("将长句拆分为短句，降低阅读难度")
        
        if vocab_coverage < 0.7:
            suggestions.append(f"增加{target_grade}年级常用词汇的使用比例")
        
        if not suggestions:
            suggestions.append("文本质量良好，保持当前风格")
        
        return suggestions


# 单例
_readability_service: ReadabilityService | None = None


def get_readability_service() -> ReadabilityService:
    """获取阅读等级评估服务单例"""
    global _readability_service
    if _readability_service is None:
        _readability_service = ReadabilityService()
    return _readability_service

