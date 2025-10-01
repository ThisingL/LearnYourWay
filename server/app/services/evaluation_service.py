"""评测服务

负责评估个性化改写的质量，提供多维度评分
"""

from typing import Dict, List

from app.config import get_settings
from app.services.llm_provider import get_llm_provider

settings = get_settings()


class EvaluationService:
    """评测服务"""
    
    # 评测维度和权重
    EVALUATION_DIMENSIONS = {
        "correctness": {"name": "正确性", "weight": 0.3, "description": "事实准确，无错误信息"},
        "coverage": {"name": "覆盖度", "weight": 0.2, "description": "保留原文所有关键信息"},
        "readability": {"name": "可读性", "weight": 0.2, "description": "符合目标年级阅读水平"},
        "interest_fit": {"name": "兴趣贴合度", "weight": 0.15, "description": "成功融入用户兴趣"},
        "length_control": {"name": "长度控制", "weight": 0.15, "description": "长度适中，不过长或过短"},
    }
    
    def __init__(self):
        """初始化服务"""
        self.llm_provider = get_llm_provider()
    
    def build_evaluation_prompt(
        self,
        original_text: str,
        personalized_text: str,
        grade: int,
        interests: List[str],
    ) -> List[Dict[str, str]]:
        """
        构建评测提示词
        
        Args:
            original_text: 原始文本
            personalized_text: 改写后的文本
            grade: 目标年级
            interests: 用户兴趣列表
            
        Returns:
            消息列表（用于 LLM Chat API）
        """
        dimensions_desc = "\n".join([
            f"- **{key}（{info['name']}）**: {info['description']}，权重 {info['weight']}"
            for key, info in self.EVALUATION_DIMENSIONS.items()
        ])
        
        interests_text = "、".join(interests) if interests else "无"
        
        system_prompt = f"""你是一位严格的教育内容评测专家，负责评估文本改写的质量。

你的任务是根据以下评测维度，对改写后的文本进行评分（每个维度 1-5 分）：

{dimensions_desc}

**评分标准**：
- 5 分：优秀，完全达标
- 4 分：良好，基本达标
- 3 分：合格，有改进空间
- 2 分：不合格，存在明显问题
- 1 分：很差，严重偏离目标

请客观、公正地评分，并为每个维度提供简短的评价理由。"""

        user_prompt = f"""请评测以下文本改写的质量：

**目标年级**：{grade} 年级
**用户兴趣**：{interests_text}

**原始文本**：
{original_text}

**改写后的文本**：
{personalized_text}

请按以下 JSON 格式输出评测结果：
```json
{{
    "scores": {{
        "correctness": 4.5,
        "coverage": 4.0,
        "readability": 4.2,
        "interest_fit": 4.3,
        "length_control": 4.5
    }},
    "comments": {{
        "correctness": "事实准确，无明显错误",
        "coverage": "保留了大部分关键信息，略有遗漏",
        "readability": "用词和句式适合5年级学生",
        "interest_fit": "成功融入了足球相关的例子",
        "length_control": "长度适中，与原文接近"
    }},
    "overall_score": 4.3,
    "summary": "改写质量良好，建议...",
    "strengths": ["融入兴趣例子自然", "可读性提升明显"],
    "weaknesses": ["个别专业术语可以进一步解释"]
}}
```"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    
    async def evaluate_personalization(
        self,
        original_text: str,
        personalized_text: str,
        grade: int,
        interests: List[str],
    ) -> Dict:
        """
        评测个性化改写质量
        
        Args:
            original_text: 原始文本
            personalized_text: 改写后的文本
            grade: 目标年级
            interests: 用户兴趣列表
            
        Returns:
            {
                "scores": Dict[str, float],
                "comments": Dict[str, str],
                "overall_score": float,
                "summary": str,
                "strengths": List[str],
                "weaknesses": List[str]
            }
        """
        # 构建评测提示词
        messages = self.build_evaluation_prompt(
            original_text, personalized_text, grade, interests
        )
        
        # 调用 LLM 进行评测
        response = await self.llm_provider.chat(messages, temperature=0.3)
        
        # 解析评测结果（TODO: 实际应使用 JSON 解析）
        # 这里返回模拟数据
        evaluation_result = {
            "scores": {
                "correctness": 4.5,
                "coverage": 4.0,
                "readability": 4.2,
                "interest_fit": 4.3,
                "length_control": 4.5,
            },
            "comments": {
                "correctness": "事实准确，无明显错误",
                "coverage": "保留了大部分关键信息",
                "readability": f"用词和句式适合{grade}年级学生",
                "interest_fit": f"成功融入了{interests[0] if interests else ''}相关的例子",
                "length_control": "长度适中，与原文接近",
            },
            "overall_score": 4.3,
            "summary": "改写质量良好，达到预期目标",
            "strengths": ["融入兴趣例子自然", "可读性提升明显"],
            "weaknesses": ["个别专业术语可以进一步解释"],
        }
        
        return evaluation_result
    
    def calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """
        计算加权总分
        
        Args:
            scores: 各维度得分
            
        Returns:
            加权总分 (1-5)
        """
        total_score = 0.0
        total_weight = 0.0
        
        for dimension, score in scores.items():
            if dimension in self.EVALUATION_DIMENSIONS:
                weight = self.EVALUATION_DIMENSIONS[dimension]["weight"]
                total_score += score * weight
                total_weight += weight
        
        return round(total_score / total_weight, 2) if total_weight > 0 else 0.0
    
    def check_quality_threshold(
        self, scores: Dict[str, float], threshold: float = 3.0
    ) -> Dict:
        """
        检查评分是否达到质量阈值
        
        Args:
            scores: 各维度得分
            threshold: 质量阈值（默认 3.0）
            
        Returns:
            {
                "passed": bool,
                "overall_score": float,
                "failed_dimensions": List[str]
            }
        """
        overall_score = self.calculate_weighted_score(scores)
        
        failed_dimensions = [
            self.EVALUATION_DIMENSIONS[dim]["name"]
            for dim, score in scores.items()
            if score < threshold and dim in self.EVALUATION_DIMENSIONS
        ]
        
        return {
            "passed": overall_score >= threshold and len(failed_dimensions) == 0,
            "overall_score": overall_score,
            "failed_dimensions": failed_dimensions,
        }


# 单例
_evaluation_service: EvaluationService | None = None


def get_evaluation_service() -> EvaluationService:
    """获取评测服务单例"""
    global _evaluation_service
    if _evaluation_service is None:
        _evaluation_service = EvaluationService()
    return _evaluation_service

