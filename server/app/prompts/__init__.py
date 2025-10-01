"""提示词模板库"""

from typing import Dict, List


class PromptTemplates:
    """提示词模板集合"""
    
    # ============ 个性化改写提示词 ============
    
    PERSONALIZE_SYSTEM = """你是一位优秀的教育内容改编专家，擅长将学习材料调整到适合不同年级学生的阅读水平。

你的任务是：
1. 将原始文本改写到适合 **{grade} 年级** 学生的阅读水平
2. 在例子和类比中融入学生的兴趣领域：**{interests}**
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

    PERSONALIZE_USER = """请将以下文本改写到适合 {grade} 年级学生的阅读水平，并在适当的地方融入与「{interests}」相关的例子或类比。

**原始文本**：
{original_text}

**改写后的文本**（请直接输出改写结果，不要添加额外说明）："""

    # ============ 评测提示词 ============
    
    EVALUATION_SYSTEM = """你是一位严格的教育内容评测专家，负责评估文本改写的质量。

你的任务是根据以下评测维度，对改写后的文本进行评分（每个维度 1-5 分）：

- **correctness（正确性）**: 事实准确，无错误信息，权重 0.3
- **coverage（覆盖度）**: 保留原文所有关键信息，权重 0.2
- **readability（可读性）**: 符合目标年级阅读水平，权重 0.2
- **interest_fit（兴趣贴合度）**: 成功融入用户兴趣，权重 0.15
- **length_control（长度控制）**: 长度适中，不过长或过短，权重 0.15

**评分标准**：
- 5 分：优秀，完全达标
- 4 分：良好，基本达标
- 3 分：合格，有改进空间
- 2 分：不合格，存在明显问题
- 1 分：很差，严重偏离目标

请客观、公正地评分，并为每个维度提供简短的评价理由。"""

    EVALUATION_USER = """请评测以下文本改写的质量：

**目标年级**：{grade} 年级
**用户兴趣**：{interests}

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
        "readability": "用词和句式适合{grade}年级学生",
        "interest_fit": "成功融入了相关的例子",
        "length_control": "长度适中，与原文接近"
    }},
    "overall_score": 4.3,
    "summary": "改写质量良好，建议...",
    "strengths": ["融入兴趣例子自然", "可读性提升明显"],
    "weaknesses": ["个别专业术语可以进一步解释"]
}}
```"""

    # ============ 术语提取提示词 ============
    
    TERM_EXTRACTION_SYSTEM = """你是一位专业的教育内容分析专家，擅长识别文本中的关键学术术语。"""

    TERM_EXTRACTION_USER = """请从以下文本中提取所有重要的学术术语（专业概念、定理、公式等），这些术语在改写时必须保留原样。

**文本**：
{text}

**要求**：
- 只提取学术性的专业术语
- 不要提取通用词汇
- 以 JSON 数组格式返回

**示例输出**：
```json
{{
    "terms": ["光合作用", "叶绿素", "ATP", "NADPH"]
}}
```"""

    @classmethod
    def format_personalize_prompt(
        cls,
        grade: int,
        interests: List[str],
        original_text: str,
        must_keep_terms: List[str] | None = None,
    ) -> List[Dict[str, str]]:
        """格式化个性化改写提示词"""
        terms_instruction = ""
        if must_keep_terms:
            terms_instruction = f"\n\n**必须保留的术语**（不可替换或简化）：\n{', '.join(must_keep_terms)}"
        
        interests_text = "、".join(interests) if interests else "日常生活"
        
        system = cls.PERSONALIZE_SYSTEM.format(
            grade=grade,
            interests=interests_text,
            terms_instruction=terms_instruction,
        )
        
        user = cls.PERSONALIZE_USER.format(
            grade=grade,
            interests=interests_text,
            original_text=original_text,
        )
        
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
    
    @classmethod
    def format_evaluation_prompt(
        cls,
        grade: int,
        interests: List[str],
        original_text: str,
        personalized_text: str,
    ) -> List[Dict[str, str]]:
        """格式化评测提示词"""
        interests_text = "、".join(interests) if interests else "无"
        
        user = cls.EVALUATION_USER.format(
            grade=grade,
            interests=interests_text,
            original_text=original_text,
            personalized_text=personalized_text,
        )
        
        return [
            {"role": "system", "content": cls.EVALUATION_SYSTEM},
            {"role": "user", "content": user},
        ]
    
    @classmethod
    def format_term_extraction_prompt(cls, text: str) -> List[Dict[str, str]]:
        """格式化术语提取提示词"""
        user = cls.TERM_EXTRACTION_USER.format(text=text)
        
        return [
            {"role": "system", "content": cls.TERM_EXTRACTION_SYSTEM},
            {"role": "user", "content": user},
        ]

