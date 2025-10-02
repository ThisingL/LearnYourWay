# LearnYourWay

> **个性化学习内容生成平台 - API 演示版**

基于生成式 AI 的个性化学习内容生成系统，将 PDF 教材转化为适合不同年级和兴趣的学习素材。

**当前阶段**：专注后端 API 开发，提供完整的 RESTful API 接口用于演示核心功能。

## ✨ 核心功能

- 📄 **PDF 智能解析**：将教材转换为结构化知识块
- 🎯 **个性化改写**：根据年级和兴趣调整内容难度和例子
- 📚 **多样化素材生成**：
  - 沉浸式文本（适合阅读理解）
  - 章节测验（多选/判断/简答）
  - 思维导图（知识结构可视化）

## 🏗️ 技术栈

- **后端框架**：Python 3.11 + FastAPI
- **异步任务**：Celery + Redis
- **LLM 调用**：托管 API（OpenAI/Anthropic/Gemini 等可切换）
- **向量数据库**：pgvector / Qdrant
- **数据校验**：Pydantic
- **部署**：Docker + Railway/Render/Fly.io

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Redis（任务队列）
- PostgreSQL（可选，用于向量存储）

### 本地开发

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/LearnYourWay.git
cd LearnYourWay

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 安装依赖
pip install -r server/requirements.txt

# 4. 配置环境变量
cp server/.env.example server/.env
# 编辑 .env 文件，填入必要的 API Key

# 5. 启动 Redis（使用 Docker）
docker run -d -p 6379:6379 redis:7-alpine

# 6. 启动后端服务
cd server
uvicorn app.main:app --reload

# 7. 启动 Celery Worker（新终端）
celery -A app.tasks.worker worker -l info
```

### 使用 Docker Compose

```bash
# 一键启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 🌐 Web 演示界面

简单美观的 Web 界面，可直接体验所有功能！

**访问地址**：http://localhost:3000

**功能**：
- 👤 设置学习者画像（年级、兴趣）
- ✍️ 输入学习内容
- 🎯 一键生成：测验题、思维导图、沉浸式文本
- 📊 美观的结果展示

详见 [web/USAGE.md](web/USAGE.md)

## 📖 API 文档

启动服务后访问：

- **Swagger UI**：http://localhost:8000/docs
- **ReDoc**：http://localhost:8000/redoc

### 核心接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/ingest/pdf` | POST | 上传 PDF 文件 |
| `/ingest/tasks/{id}` | GET | 查询解析进度 |
| `/profiles` | POST | 创建用户画像 |
| `/profiles/{userId}` | GET | 查询用户画像 |
| `/materials/immersive` | POST | 生成沉浸式文本 |
| `/materials/quiz` | POST | 生成章节测验 |
| `/materials/mindmap` | POST | 生成思维导图 |

### API 使用示例

```bash
# 1. 上传 PDF
curl -F file=@sample.pdf http://localhost:8000/ingest/pdf

# 2. 创建用户画像
curl -X POST http://localhost:8000/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "demo_user",
    "grade": 5,
    "interests": ["足球", "科学实验", "恐龙"]
  }'

# 3. 生成测验题
curl -X POST http://localhost:8000/materials/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "chunkId": "chunk_123",
    "profileId": "demo_user",
    "count": 10
  }'
```

## 📁 项目结构

```
LearnYourWay/
├── docs/                      # 开发文档
│   ├── README.md             # 文档导航
│   ├── 01_项目总览与执行顺序.md
│   ├── 02_环境与项目初始化.md
│   └── ...
├── server/                    # 后端代码（待创建）
│   ├── app/
│   │   ├── main.py           # FastAPI 入口
│   │   ├── api/              # API 路由
│   │   ├── services/         # 业务逻辑
│   │   ├── tasks/            # Celery 任务
│   │   └── models/           # Pydantic 模型
│   ├── tests/                # 测试代码
│   ├── requirements.txt      # Python 依赖
│   ├── Dockerfile
│   └── .env.example
├── demo/                      # 可选：演示页面
├── docker-compose.yml
└── README.md
```

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行测试并生成覆盖率报告
pytest tests/ --cov=app --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

## 📚 开发文档

详细的开发文档请查看 [docs/README.md](docs/README.md)

- [项目总览与执行顺序](docs/01_项目总览与执行顺序.md)
- [环境与项目初始化](docs/02_环境与项目初始化.md)
- [数据摄取与 PDF 解析](docs/03_数据摄取与PDF解析.md)
- [个性化与阅读等级调整](docs/04_个性化与阅读等级调整.md)
- [学习素材生成](docs/05_学习素材生成.md)
- [API 设计与集成](docs/06_API设计与集成.md)
- [测试策略](docs/07_移动端应用与测试.md)
- [部署与 CI/CD](docs/08_部署与CI_CD.md)
- [提示词库与风格规范](docs/09_提示词库与风格规范.md)

## 🚢 部署

### 推荐平台

- **Railway**：https://railway.app （最简单）
- **Render**：https://render.com
- **Fly.io**：https://fly.io
- **Google Cloud Run**

详细部署指南请参考 [部署与 CI/CD 文档](docs/08_部署与CI_CD.md)

## 🛣️ 路线图

- [x] 项目架构设计
- [x] 开发文档编写
- [x] 后端 API 实现
  - [x] PDF 解析服务
  - [x] 个性化改写服务
  - [x] 学习素材生成服务
  - [x] LLM Provider 抽象层
  - [x] 硅基流动 API 集成
- [x] Web 演示界面 ⭐
  - [x] 用户画像设置
  - [x] 内容生成界面
  - [x] 结果可视化展示
- [ ] 测试与质量保障
- [ ] 部署演示环境
- [ ] （未来）移动端应用开发

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**注意**：本项目当前为 API 演示版本，暂不包含移动端应用。后端开发完成并验证后，将根据需要考虑移动端开发。