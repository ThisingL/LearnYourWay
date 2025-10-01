"""个性化改写服务

负责将原始文本改写到目标阅读等级，并融入用户兴趣
"""

from typing import Dict, List

from app.config import get_settings
from app.services.llm_provider import get_llm_provider
from app.services.readability_service import get_readability_service

settings = get_settings()


class PersonalizeService:
    """个性化改写服务"""
    
    def __init__(self):
        """初始化服务"""
        self.llm_provider = get_llm_provider()
        self.readability_service = get_readability_service()
    
    def build_personalize_prompt(
        self,
        original_text: str,
        grade: int,
        interests: List[str],
        must_keep_terms: List[str] | None = None,
    ) -> List[Dict[str, str]]:
        """
        构建个性化改写提示词
        
        Args:
            original_text: 原始文本
            grade: 目标年级
            interests: 用户兴趣列表
            must_keep_terms: 必须保留的术语列表
            
        Returns:
            消息列表（用于 LLM Chat API）
        """
        terms_instruction = ""
        if must_keep_terms:
            terms_instruction = f"\n\n**必须保留的术语**（不可替换或简化）：\n{', '.join(must_keep_terms)}"
        
        interests_text = "、".join(interests) if interests else "日常生活"
        
        system_prompt = f"""你是一位优秀的教育内容改编专家，擅长将学习材料调整到适合不同年级学生的阅读水平。

你的任务是：
1. 将原始文本改写到适合 **{grade} 年级** 学生的阅读水平
2. 在例子和类比中融入学生的兴趣领域：**{interests_text}**
3. 保持学科范畴和核心概念不变
4. 确保事实准确性，不编造内容
5. 保持原文的逻辑结构和关键信息

**改写原则**：
- 使用 {grade} 年级学生能理解的词汇和句式
- 将抽象概念用具体例子解释（最好来自学生的兴趣领域）
- 句子长度适中，避免复杂的从句
- 保留所有关键术语和概念{terms_instruction}

**禁止事项**：
- 不得删除或遗漏重要信息
- 不得过度简化而丧失准确性
- 不得编造事实或数据
- 不得改变学科范畴"""

        user_prompt = f"""请将以下文本改写到适合 {grade} 年级学生的阅读水平，并在适当的地方融入与「{interests_text}」相关的例子或类比。

**原始文本**：
{original_text}

**改写后的文本**（请直接输出改写结果，不要添加额外说明）："""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    
    async def personalize_text(
        self,
        original_text: str,
        grade: int,
        interests: List[str],
        must_keep_terms: List[str] | None = None,
    ) -> Dict:
        """
        个性化改写文本
        
        Args:
            original_text: 原始文本
            grade: 目标年级
            interests: 用户兴趣列表
            must_keep_terms: 必须保留的术语列表
            
        Returns:
            {
                "personalized_text": str,
                "original_readability": Dict,
                "personalized_readability": Dict,
                "improvement": Dict
            }
        """
        # 分析原文可读性
        original_readability = self.readability_service.analyze_readability(
            original_text, grade
        )
        
        # 构建提示词
        messages = self.build_personalize_prompt(
            original_text, grade, interests, must_keep_terms
        )
        
        # 调用 LLM 进行改写
        personalized_text = await self.llm_provider.chat(messages, temperature=0.7)
        
        # 分析改写后的可读性
        personalized_readability = self.readability_service.analyze_readability(
            personalized_text, grade
        )
        
        # 计算改进指标
        improvement = self._calculate_improvement(
            original_readability, personalized_readability
        )
        
        # 验证术语保留
        if must_keep_terms:
            missing_terms = [
                term for term in must_keep_terms if term not in personalized_text
            ]
            if missing_terms:
                improvement["warnings"] = improvement.get("warnings", [])
                improvement["warnings"].append(
                    f"以下术语未在改写文本中找到：{', '.join(missing_terms)}"
                )
        
        return {
            "personalized_text": personalized_text,
            "original_readability": original_readability,
            "personalized_readability": personalized_readability,
            "improvement": improvement,
        }
    
    def _calculate_improvement(
        self, original: Dict, personalized: Dict
    ) -> Dict:
        """计算改进指标"""
        return {
            "flesch_score_change": round(
                personalized["flesch_score"] - original["flesch_score"], 2
            ),
            "grade_level_change": personalized["estimated_grade"] - original["estimated_grade"],
            "vocab_coverage_change": round(
                personalized["vocab_coverage"] - original["vocab_coverage"], 2
            ),
            "sentence_length_change": round(
                personalized["avg_sentence_length"] - original["avg_sentence_length"], 1
            ),
        }
    
    async def validate_personalization(
        self,
        original_text: str,
        personalized_text: str,
        must_keep_terms: List[str] | None = None,
    ) -> Dict:
        """
        验证个性化改写的质量
        
        Args:
            original_text: 原始文本
            personalized_text: 改写后的文本
            must_keep_terms: 必须保留的术语
            
        Returns:
            {
                "is_valid": bool,
                "issues": List[str],
                "term_coverage": float
            }
        """
        issues = []
        
        # 检查长度（改写后不应该过短或过长）
        len_ratio = len(personalized_text) / len(original_text)
        if len_ratio < 0.5:
            issues.append("改写后的文本过短，可能丢失了重要信息")
        elif len_ratio > 2.0:
            issues.append("改写后的文本过长，可能添加了额外内容")
        
        # 检查术语保留
        term_coverage = 1.0
        if must_keep_terms:
            preserved_count = sum(
                1 for term in must_keep_terms if term in personalized_text
            )
            term_coverage = preserved_count / len(must_keep_terms)
            
            if term_coverage < 1.0:
                missing = [
                    term for term in must_keep_terms if term not in personalized_text
                ]
                issues.append(f"缺失必须保留的术语：{', '.join(missing)}")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "term_coverage": round(term_coverage, 2),
            "length_ratio": round(len_ratio, 2),
        }


# 单例
_personalize_service: PersonalizeService | None = None


def get_personalize_service() -> PersonalizeService:
    """获取个性化服务单例"""
    global _personalize_service
    if _personalize_service is None:
        _personalize_service = PersonalizeService()
    return _personalize_service

