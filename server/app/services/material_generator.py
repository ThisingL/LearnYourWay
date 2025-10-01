"""学习素材生成服务

提供测验题、思维导图、沉浸式文本等多种学习素材的生成
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from app.config import get_settings
from app.services.llm_provider import get_llm_provider

settings = get_settings()


class MaterialGenerator(ABC):
    """素材生成器基类"""
    
    def __init__(self):
        self.llm_provider = get_llm_provider()
    
    @abstractmethod
    async def generate(self, content: str, profile: Dict, **kwargs) -> Any:
        """生成素材的抽象方法"""
        pass
    
    @abstractmethod
    def validate(self, result: Any) -> bool:
        """验证生成结果的有效性"""
        pass


class QuizGenerator(MaterialGenerator):
    """测验题生成器"""
    
    QUESTION_TYPES = ["single", "multi", "tf", "short"]
    
    def build_quiz_prompt(
        self, content: str, grade: int, interests: List[str], count: int = 10
    ) -> List[Dict[str, str]]:
        """构建测验题生成提示词"""
        
        interests_text = "、".join(interests) if interests else "日常生活"
        
        system_prompt = f"""你是一位专业的教育测评专家，擅长根据学习内容生成高质量的测验题。

你的任务是：
1. 根据提供的学习内容生成 {count} 道测验题
2. 题型分布：单选题、多选题、判断题、简答题
3. 难度分级：1（容易）到 5（困难）
4. 适合 {grade} 年级学生的认知水平
5. 在适当的地方融入与「{interests_text}」相关的场景

**题型要求**：
- **单选题 (single)**：4个选项，只有1个正确答案
- **多选题 (multi)**：4-5个选项，2-3个正确答案
- **判断题 (tf)**：对或错
- **简答题 (short)**：需要文字回答

**必须包含**：
- 题目描述 (stem)
- 选项 (options)，判断题和简答题可为空数组
- 正确答案 (answer)
- 详细解析 (explanation)
- 难度等级 (difficulty: 1-5)

**质量要求**：
- 题目紧扣学习内容的核心概念
- 干扰项设计合理，避免过于明显
- 解析清晰，帮助学生理解
- 覆盖不同认知层次（记忆、理解、应用）"""

        user_prompt = f"""请根据以下学习内容生成 {count} 道测验题：

**学习内容**：
{content}

**目标年级**：{grade} 年级
**学生兴趣**：{interests_text}

请以 JSON 格式输出，格式如下：
```json
{{
    "questions": [
        {{
            "id": "q1",
            "type": "single",
            "stem": "题目描述",
            "options": ["选项A", "选项B", "选项C", "选项D"],
            "answer": "选项A",
            "explanation": "详细解析",
            "difficulty": 3
        }},
        {{
            "id": "q2",
            "type": "multi",
            "stem": "题目描述（可以包含多个正确答案）",
            "options": ["选项A", "选项B", "选项C", "选项D"],
            "answer": ["选项A", "选项C"],
            "explanation": "详细解析",
            "difficulty": 4
        }},
        {{
            "id": "q3",
            "type": "tf",
            "stem": "判断题描述",
            "options": [],
            "answer": true,
            "explanation": "详细解析",
            "difficulty": 2
        }},
        {{
            "id": "q4",
            "type": "short",
            "stem": "简答题描述",
            "options": [],
            "answer": "参考答案",
            "explanation": "评分要点",
            "difficulty": 4
        }}
    ]
}}
```

请直接输出 JSON，不要添加额外说明。"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    
    async def generate(
        self, content: str, profile: Dict, count: int = 10, **kwargs
    ) -> Dict:
        """
        生成测验题
        
        Args:
            content: 学习内容
            profile: 用户画像
            count: 题目数量
            
        Returns:
            {
                "questions": [
                    {
                        "id": str,
                        "type": str,
                        "stem": str,
                        "options": List[str],
                        "answer": Any,
                        "explanation": str,
                        "difficulty": int
                    }
                ]
            }
        """
        grade = profile.get("grade", 5)
        interests = profile.get("interests", [])
        
        # 构建提示词
        messages = self.build_quiz_prompt(content, grade, interests, count)
        
        # 调用 LLM
        response = await self.llm_provider.chat(messages, temperature=0.8)
        
        # TODO: 解析 JSON 响应
        # 目前返回模拟数据
        questions = self._generate_mock_questions(count, grade, interests)
        
        return {"questions": questions}
    
    def _generate_mock_questions(
        self, count: int, grade: int, interests: List[str]
    ) -> List[Dict]:
        """生成模拟测验题（用于测试）"""
        interest_example = interests[0] if interests else "日常生活"
        
        mock_questions = [
            {
                "id": "q1",
                "type": "single",
                "stem": f"光合作用主要在植物的哪个部位进行？（想想{interest_example}场上的小草）",
                "options": ["根部", "茎部", "叶片", "花朵"],
                "answer": "叶片",
                "explanation": "光合作用主要在叶片的叶绿体中进行，因为叶片能接收到更多阳光。",
                "difficulty": 2,
            },
            {
                "id": "q2",
                "type": "multi",
                "stem": "光合作用需要哪些条件？（选出所有正确答案）",
                "options": ["阳光", "水分", "二氧化碳", "氮气"],
                "answer": ["阳光", "水分", "二氧化碳"],
                "explanation": "光合作用需要光能、水和二氧化碳，不需要氮气。",
                "difficulty": 3,
            },
            {
                "id": "q3",
                "type": "tf",
                "stem": "光合作用会产生氧气，这些氧气对地球上的生物很重要。",
                "options": [],
                "answer": True,
                "explanation": "正确！光合作用产生的氧气是地球上大多数生物呼吸所必需的。",
                "difficulty": 1,
            },
            {
                "id": "q4",
                "type": "short",
                "stem": f"请用自己的话解释什么是光合作用，可以用{interest_example}的例子来说明。",
                "options": [],
                "answer": "光合作用是植物利用阳光、水和二氧化碳制造食物（葡萄糖）的过程，同时释放氧气。",
                "explanation": "要点：提到阳光、水、二氧化碳、制造食物、释放氧气等关键要素。",
                "difficulty": 4,
            },
        ]
        
        # 根据 count 返回相应数量
        return mock_questions[:count] if count < len(mock_questions) else mock_questions * ((count // len(mock_questions)) + 1)
    
    def validate(self, result: Dict) -> bool:
        """验证测验题结果"""
        if "questions" not in result:
            return False
        
        for q in result["questions"]:
            # 检查必需字段
            required_fields = ["id", "type", "stem", "answer", "explanation", "difficulty"]
            if not all(field in q for field in required_fields):
                return False
            
            # 检查题型
            if q["type"] not in self.QUESTION_TYPES:
                return False
            
            # 检查难度范围
            if not (1 <= q["difficulty"] <= 5):
                return False
        
        return True


class MindMapGenerator(MaterialGenerator):
    """思维导图生成器"""
    
    def build_mindmap_prompt(
        self, content: str, grade: int, interests: List[str]
    ) -> List[Dict[str, str]]:
        """构建思维导图生成提示词"""
        
        interests_text = "、".join(interests) if interests else "日常生活"
        
        system_prompt = f"""你是一位专业的知识可视化专家，擅长将学习内容转化为思维导图。

你的任务是：
1. 识别学习内容中的核心概念和关键关系
2. 构建清晰的层次结构
3. 适合 {grade} 年级学生理解
4. 在适当的地方融入与「{interests_text}」相关的类比

**思维导图要求**：
- **节点 (nodes)**：包含核心概念、子概念、具体事例
  - `id`: 唯一标识符（如 "node1", "node2"）
  - `label`: 节点显示的文本
  - `type`: 节点类型（"root"根节点, "concept"概念, "example"示例）
  
- **连接 (edges)**：表示概念之间的关系
  - `source`: 起始节点 ID
  - `target`: 目标节点 ID
  - `label`: 关系描述（如"包含"、"导致"、"需要"）

**设计原则**：
- 保持层次清晰，避免过于复杂
- 确保所有节点都连通（无孤立节点）
- 关系标签简洁明了
- 覆盖学习内容的关键概念"""

        user_prompt = f"""请根据以下学习内容生成思维导图的 JSON 数据：

**学习内容**：
{content}

**目标年级**：{grade} 年级
**学生兴趣**：{interests_text}

请以 JSON 格式输出，格式如下：
```json
{{
    "nodes": [
        {{
            "id": "root",
            "label": "光合作用",
            "type": "root"
        }},
        {{
            "id": "node1",
            "label": "必需条件",
            "type": "concept"
        }},
        {{
            "id": "node2",
            "label": "阳光",
            "type": "example"
        }}
    ],
    "edges": [
        {{
            "source": "root",
            "target": "node1",
            "label": "需要"
        }},
        {{
            "source": "node1",
            "target": "node2",
            "label": "包含"
        }}
    ]
}}
```

请直接输出 JSON，不要添加额外说明。"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    
    async def generate(self, content: str, profile: Dict, **kwargs) -> Dict:
        """
        生成思维导图
        
        Args:
            content: 学习内容
            profile: 用户画像
            
        Returns:
            {
                "nodes": [{"id": str, "label": str, "type": str}],
                "edges": [{"source": str, "target": str, "label": str}]
            }
        """
        grade = profile.get("grade", 5)
        interests = profile.get("interests", [])
        
        # 构建提示词
        messages = self.build_mindmap_prompt(content, grade, interests)
        
        # 调用 LLM
        response = await self.llm_provider.chat(messages, temperature=0.7)
        
        # TODO: 解析 JSON 响应
        # 目前返回模拟数据
        mindmap_data = self._generate_mock_mindmap(interests)
        
        return mindmap_data
    
    def _generate_mock_mindmap(self, interests: List[str]) -> Dict:
        """生成模拟思维导图（用于测试）"""
        interest_example = interests[0] if interests else "植物"
        
        return {
            "nodes": [
                {"id": "root", "label": "光合作用", "type": "root"},
                {"id": "node1", "label": "必需条件", "type": "concept"},
                {"id": "node2", "label": "阳光", "type": "example"},
                {"id": "node3", "label": "水", "type": "example"},
                {"id": "node4", "label": "二氧化碳", "type": "example"},
                {"id": "node5", "label": "过程", "type": "concept"},
                {"id": "node6", "label": "叶绿体吸收光能", "type": "example"},
                {"id": "node7", "label": "化学反应", "type": "example"},
                {"id": "node8", "label": "产物", "type": "concept"},
                {"id": "node9", "label": "葡萄糖", "type": "example"},
                {"id": "node10", "label": "氧气", "type": "example"},
                {"id": "node11", "label": f"类比：像{interest_example}需要能量一样", "type": "example"},
            ],
            "edges": [
                {"source": "root", "target": "node1", "label": "需要"},
                {"source": "node1", "target": "node2", "label": "包含"},
                {"source": "node1", "target": "node3", "label": "包含"},
                {"source": "node1", "target": "node4", "label": "包含"},
                {"source": "root", "target": "node5", "label": "经过"},
                {"source": "node5", "target": "node6", "label": "首先"},
                {"source": "node5", "target": "node7", "label": "然后"},
                {"source": "root", "target": "node8", "label": "产生"},
                {"source": "node8", "target": "node9", "label": "生成"},
                {"source": "node8", "target": "node10", "label": "释放"},
                {"source": "node9", "target": "node11", "label": "提供能量"},
            ],
        }
    
    def validate(self, result: Dict) -> bool:
        """验证思维导图结果"""
        if "nodes" not in result or "edges" not in result:
            return False
        
        # 检查节点
        node_ids = set()
        for node in result["nodes"]:
            if not all(field in node for field in ["id", "label", "type"]):
                return False
            node_ids.add(node["id"])
        
        # 检查边的连通性
        for edge in result["edges"]:
            if not all(field in edge for field in ["source", "target"]):
                return False
            if edge["source"] not in node_ids or edge["target"] not in node_ids:
                return False
        
        return True


class ImmersiveTextGenerator(MaterialGenerator):
    """沉浸式文本生成器"""
    
    def build_immersive_prompt(
        self, content: str, grade: int, interests: List[str]
    ) -> List[Dict[str, str]]:
        """构建沉浸式文本生成提示词"""
        
        interests_text = "、".join(interests) if interests else "日常生活"
        
        system_prompt = f"""你是一位优秀的教育内容创作者，擅长将学习内容改写为引人入胜的沉浸式文本。

你的任务是：
1. 将学习内容改写为生动、有趣的故事化表达
2. 分成多个小节，每节有清晰的标题
3. 适合 {grade} 年级学生阅读
4. 融入与「{interests_text}」相关的场景和例子
5. 为关键位置添加插图占位符

**沉浸式文本特点**：
- 使用第二人称（"你"）或故事叙述的方式
- 创造情境感，让学生身临其境
- 保留所有关键概念和定义
- 语言生动，富有画面感

**插图占位符格式**：
- 在需要插图的地方使用：`{{image:插图描述}}`
- 例如：`{{image:一片绿色的叶子在阳光下闪闪发光}}`

**输出格式**：
每个小节包含：
- `title`: 小节标题
- `paragraphs`: 段落数组
- 在适当段落中包含插图占位符"""

        user_prompt = f"""请将以下学习内容改写为沉浸式文本：

**学习内容**：
{content}

**目标年级**：{grade} 年级
**学生兴趣**：{interests_text}

请以 JSON 格式输出，格式如下：
```json
{{
    "sections": [
        {{
            "title": "小节标题",
            "paragraphs": [
                "第一段文本内容...",
                "{{{{image:插图描述}}}}",
                "第二段文本内容..."
            ]
        }},
        {{
            "title": "另一个小节标题",
            "paragraphs": [
                "段落内容..."
            ]
        }}
    ]
}}
```

请直接输出 JSON，不要添加额外说明。"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    
    async def generate(self, content: str, profile: Dict, **kwargs) -> Dict:
        """
        生成沉浸式文本
        
        Args:
            content: 学习内容
            profile: 用户画像
            
        Returns:
            {
                "sections": [
                    {
                        "title": str,
                        "paragraphs": List[str]
                    }
                ]
            }
        """
        grade = profile.get("grade", 5)
        interests = profile.get("interests", [])
        
        # 构建提示词
        messages = self.build_immersive_prompt(content, grade, interests)
        
        # 调用 LLM
        response = await self.llm_provider.chat(messages, temperature=0.9)
        
        # TODO: 解析 JSON 响应
        # 目前返回模拟数据
        immersive_data = self._generate_mock_immersive(interests)
        
        return immersive_data
    
    def _generate_mock_immersive(self, interests: List[str]) -> Dict:
        """生成模拟沉浸式文本（用于测试）"""
        interest_example = interests[0] if interests else "运动"
        
        return {
            "sections": [
                {
                    "title": "神奇的绿色工厂",
                    "paragraphs": [
                        f"想象一下，你正在{interest_example}场边休息，看着周围绿油油的小草。你知道吗？这些看似普通的小草，其实都是一座座神奇的「绿色工厂」！",
                        "{{image:阳光照射在绿色叶片上，叶片闪闪发光}}",
                        "当阳光洒在叶片上时，一场奇妙的化学魔法就开始了。这个过程有一个很酷的名字——光合作用。",
                    ]
                },
                {
                    "title": "光合作用的三大原料",
                    "paragraphs": [
                        "就像你需要食物才有力气一样，植物也需要「原料」才能制造自己的食物。光合作用需要三样东西：",
                        "第一样是阳光。植物就像太阳能充电器，需要吸收阳光的能量。",
                        "第二样是水。植物通过根部从土壤中吸收水分，就像你用吸管喝水一样。",
                        "{{image:植物的根部从土壤中吸收水分}}",
                        "第三样是二氧化碳。这是我们呼出的气体，植物却把它当成宝贝！",
                    ]
                },
                {
                    "title": "叶绿体——绿色工厂的核心",
                    "paragraphs": [
                        "在叶片里，有无数个微小的「工厂车间」，叫做叶绿体。",
                        "叶绿体里有一种特殊的绿色物质——叶绿素。正是叶绿素让叶片变成绿色，也正是它负责吸收阳光。",
                        "{{image:显微镜下的叶绿体，里面有许多绿色的小颗粒}}",
                        f"你可以把叶绿素想象成{interest_example}运动员的装备，有了它，植物才能完成光合作用这场「比赛」。",
                    ]
                },
                {
                    "title": "产物：食物和氧气",
                    "paragraphs": [
                        "经过一系列复杂的化学反应，光合作用生产出两样重要的东西：",
                        "第一样是葡萄糖，这是植物的食物，给植物提供能量，让它能够生长。",
                        f"第二样是氧气！没错，就是我们呼吸需要的氧气。可以说，植物通过光合作用，给地球上所有动物（包括正在{interest_example}的你）提供了新鲜空气！",
                        "{{image:植物释放氧气泡泡，小动物们在旁边快乐地呼吸}}",
                    ]
                },
            ]
        }
    
    def validate(self, result: Dict) -> bool:
        """验证沉浸式文本结果"""
        if "sections" not in result:
            return False
        
        for section in result["sections"]:
            if not all(field in section for field in ["title", "paragraphs"]):
                return False
            if not isinstance(section["paragraphs"], list):
                return False
        
        return True


# 单例实例
_quiz_generator: QuizGenerator | None = None
_mindmap_generator: MindMapGenerator | None = None
_immersive_generator: ImmersiveTextGenerator | None = None


def get_quiz_generator() -> QuizGenerator:
    """获取测验题生成器单例"""
    global _quiz_generator
    if _quiz_generator is None:
        _quiz_generator = QuizGenerator()
    return _quiz_generator


def get_mindmap_generator() -> MindMapGenerator:
    """获取思维导图生成器单例"""
    global _mindmap_generator
    if _mindmap_generator is None:
        _mindmap_generator = MindMapGenerator()
    return _mindmap_generator


def get_immersive_generator() -> ImmersiveTextGenerator:
    """获取沉浸式文本生成器单例"""
    global _immersive_generator
    if _immersive_generator is None:
        _immersive_generator = ImmersiveTextGenerator()
    return _immersive_generator

