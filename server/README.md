# LearnYourWay 后端服务

基于 FastAPI + Celery 的个性化学习内容生成平台后端。

## 快速开始

### 使用 Conda 环境（推荐）

```bash
# 1. 创建 Conda 环境
conda create -n learn_your_way python=3.11
conda activate learn_your_way

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要的 API Key

# 4. 启动依赖服务（Redis + PostgreSQL）
docker-compose -f docker-compose.deps.yml up -d

# 5. 启动 API 服务
uvicorn app.main:app --reload

# 6. 启动 Celery Worker（新终端）
conda activate learn_your_way
celery -A app.tasks.worker worker -l info --pool=solo  # Windows
# celery -A app.tasks.worker worker -l info  # Linux/Mac
```

### 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
server/
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置管理
│   ├── api/                 # API 路由层
│   │   ├── health.py        # 健康检查
│   │   ├── profiles.py      # 用户画像
│   │   ├── ingest.py        # PDF 摄取
│   │   ├── personalize.py   # 个性化
│   │   └── materials.py     # 学习素材
│   ├── services/            # 业务逻辑层
│   │   ├── llm_provider.py  # LLM 抽象层
│   │   └── pdf_parser.py    # PDF 解析
│   ├── tasks/               # Celery 任务
│   │   ├── worker.py        # Worker 配置
│   │   ├── ingest_pdf.py    # PDF 摄取任务
│   │   ├── personalize.py   # 个性化任务
│   │   ├── materials.py     # 素材生成任务
│   │   └── scoring.py       # 评测任务
│   ├── models/              # Pydantic 模型
│   │   └── api_models.py    # API 数据模型
│   └── repos/               # 数据访问层
├── tests/                   # 测试
│   ├── unit/                # 单元测试
│   ├── integration/         # 集成测试
│   └── e2e/                 # 端到端测试
├── requirements.txt         # Python 依赖
├── .env.example            # 环境变量示例
└── docker-compose.deps.yml  # 依赖服务配置
```

## 核心 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/healthz` | GET | 健康检查 |
| `/profiles` | POST | 创建用户画像 |
| `/profiles/{user_id}` | GET | 获取用户画像 |
| `/ingest/pdf` | POST | 上传 PDF |
| `/ingest/tasks/{task_id}` | GET | 查询解析状态 |
| `/personalize` | POST | 个性化改写 |
| `/materials/quiz` | POST | 生成测验题 |
| `/materials/mindmap` | POST | 生成思维导图 |
| `/materials/immersive` | POST | 生成沉浸式文本 |

## 开发指南

### 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行测试并生成覆盖率
pytest tests/ --cov=app --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html  # Mac/Linux
start htmlcov/index.html  # Windows
```

### 代码格式化

```bash
# 格式化代码
black app/
isort app/

# 检查代码规范
flake8 app/
```

## 技术栈

- **Web 框架**: FastAPI 0.104+
- **异步任务**: Celery + Redis
- **LLM**: OpenAI/Anthropic/Google (可切换)
- **PDF 解析**: PyMuPDF + pdfplumber
- **数据校验**: Pydantic
- **数据库**: PostgreSQL + pgvector

## 部署

见主项目 [README](../README.md) 和 [部署文档](../docs/08_部署与CI_CD.md)。
