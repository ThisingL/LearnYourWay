# LearnYourWay

> **个性化学习内容生成平台 - API 演示版**

基于生成式 AI 的个性化学习内容生成系统，将 PDF 教材转化为适合不同年级和兴趣的学习素材。

**当前阶段**：专注后端 API 开发 + Web 演示界面。

## ✨ 核心功能

- 📄 **PDF 智能解析**：将教材转换为结构化知识块
- 🎯 **个性化改写**：根据年级和兴趣调整内容难度和例子
- 📚 **多样化素材生成**：
  - 沉浸式文本（适合阅读理解）
  - 章节测验（多选/判断/简答）
  - 思维导图（知识结构可视化）

## 🏗️ 技术栈

- **后端框架**：Python 3.11 + FastAPI
- **异步任务**：Celery + Redis（可选）
- **LLM 调用**：硅基流动 API（Qwen2.5，256K 上下文）
- **向量数据库**：pgvector / Qdrant
- **数据校验**：Pydantic
- **前端界面**：HTML + Tailwind CSS + ECharts

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Conda（推荐）
- 硅基流动 API Key（https://cloud.siliconflow.cn）

### 5 分钟快速体验

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/LearnYourWay.git
cd LearnYourWay

# 2. 创建 Conda 环境
conda create -n project_learn_your_way python=3.11
conda activate project_learn_your_way

# 3. 安装依赖
cd server
pip install -r requirements.txt

# 4. 配置 API Key ⭐ 重要
copy .env.example .env
# 编辑 .env 文件：
#   OPENAI_API_KEY=你的硅基流动APIKey

# 5. 启动后端服务
uvicorn app.main:app --reload

# 6. 启动 Web 界面（新终端）
cd ../web
python -m http.server 3000
```

### 访问服务

- **🌐 Web 演示界面**: http://localhost:3000 ⭐ 推荐
- **📖 API 文档**: http://localhost:8000/docs

---

## 🌐 Web 演示界面使用

### 操作流程：

1. **设置学习者画像**
   - 输入用户 ID（如：xiaoming）
   - 选择年级（1-12）
   - 添加兴趣标签（如：足球、恐龙、科学）
   - 点击"💾 保存画像"

2. **输入学习内容**
   - 方式 A：📄 上传 PDF 文件（自动提取文本）
   - 方式 B：✍️ 直接输入或粘贴文本

3. **生成学习素材**
   - 点击 **⚡ 一键生成全部**（推荐）
   - 或分别生成：测验题、思维导图、沉浸式文本

4. **查看结果**
   - 📝 测验题（可展开查看答案）
   - 🧠 思维导图（可交互缩放拖拽）
   - 📖 沉浸式文本（分章节展示）

详见 [web/USAGE.md](web/USAGE.md)

---

## 📖 API 文档

### 核心接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/healthz` | GET | 健康检查 |
| `/profiles` | POST | 创建用户画像 |
| `/profiles/{user_id}` | GET | 查询用户画像 |
| `/ingest/pdf` | POST | 上传 PDF |
| `/ingest/tasks/{task_id}` | GET | 查询解析状态 |
| `/materials/quiz` | POST | 生成测验题 |
| `/materials/mindmap` | POST | 生成思维导图 |
| `/materials/immersive` | POST | 生成沉浸式文本 |

### API 使用示例

```bash
# 1. 创建用户画像
curl -X POST http://localhost:8000/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "grade": 5,
    "interests": ["足球", "科学实验", "恐龙"]
  }'

# 2. 生成测验题
curl -X POST http://localhost:8000/materials/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "chunk_id": "test_001",
    "profile_id": "demo_user",
    "content": "光合作用是植物利用光能将二氧化碳和水转化为葡萄糖和氧气的过程...",
    "count": 5
  }'
```

---

## 📁 项目结构

```
LearnYourWay/
├── docs/                      # 📚 开发文档
│   ├── README.md             # 文档导航
│   ├── 01-05.md              # 后端功能文档
│   └── 06_Web演示界面.md     # Web 界面文档
├── server/                    # 🔧 后端代码
│   ├── app/
│   │   ├── api/              # API 路由
│   │   ├── services/         # 业务逻辑
│   │   ├── tasks/            # Celery 任务
│   │   └── models/           # 数据模型
│   ├── tests/                # 测试代码
│   ├── .env.example          # ⭐ 配置模板
│   ├── requirements.txt      # Python 依赖
│   └── README.md
├── web/                       # 🌐 Web 界面
│   ├── index.html            # 主页面
│   ├── app.js                # 业务逻辑
│   ├── debug.html            # 调试工具
│   └── README.md
└── README.md                  # 本文件
```

---

## 🧪 测试

```bash
# 运行所有测试
cd server
pytest tests/ -v

# 运行测试并生成覆盖率报告
pytest tests/ --cov=app --cov-report=html
```

---

## 📚 开发文档

详细的开发文档请查看 [docs/README.md](docs/README.md)

- [项目总览与执行顺序](docs/01_项目总览与执行顺序.md)
- [环境与项目初始化](docs/02_环境与项目初始化.md)
- [数据摄取与 PDF 解析](docs/03_数据摄取与PDF解析.md)
- [个性化与阅读等级调整](docs/04_个性化与阅读等级调整.md)
- [学习素材生成](docs/05_学习素材生成.md)
- [Web 演示界面](docs/06_Web演示界面.md) ⭐
- [测试策略](docs/07_移动端应用与测试.md)
- [部署与 CI/CD](docs/08_部署与CI_CD.md)
- [提示词库与风格规范](docs/09_提示词库与风格规范.md)

---

## 🚢 部署

### 推荐平台

- **Railway**：https://railway.app （最简单）
- **Render**：https://render.com
- **Fly.io**：https://fly.io

详细部署指南请参考 [部署与 CI/CD 文档](docs/08_部署与CI_CD.md)

---

## 🛣️ 开发进度

- [x] 项目架构设计
- [x] 开发文档编写
- [x] 后端 API 实现
  - [x] PDF 解析服务（PyMuPDF）
  - [x] 个性化改写服务
  - [x] 学习素材生成服务
  - [x] LLM Provider 抽象层
  - [x] 硅基流动 API 集成（Qwen2.5-7B）
- [x] Web 演示界面 ⭐
  - [x] 用户画像设置
  - [x] PDF 上传与解析
  - [x] 内容生成界面
  - [x] 结果可视化展示（测验题、思维导图、沉浸式文本）
- [ ] 测试与质量保障
- [ ] 部署演示环境
- [ ] （未来）移动端应用开发

---

## 🤝 团队协作

### 新成员加入流程

1. **克隆项目**
   ```bash
   git clone <项目地址>
   cd LearnYourWay
   ```

2. **配置环境**
   ```bash
   conda create -n project_learn_your_way python=3.11
   conda activate project_learn_your_way
   cd server
   pip install -r requirements.txt
   ```

3. **配置 API Key** ⭐ 重要
   ```bash
   copy .env.example .env
   # 编辑 .env，填入自己的 API Key
   ```

4. **启动开发**
   ```bash
   uvicorn app.main:app --reload
   ```

详见 [server/SETUP_ENV.md](server/SETUP_ENV.md)

---

## 🔒 安全说明

### API Key 管理

- ✅ `.env` 文件不会被提交到 Git
- ✅ `.env.example` 是配置模板（不含真实 Key）
- ⚠️ 每个开发者使用自己的 API Key
- ⚠️ 不要在代码、Issues、聊天中分享 API Key
- ⚠️ 如果 Key 泄露，立即在平台重新生成

### 获取新的 API Key

如果 API Key 泄露或需要更换：
1. 登录 https://cloud.siliconflow.cn
2. 删除旧的 Key
3. 生成新的 Key
4. 更新 `.env` 文件
5. 重启服务

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 提交前检查清单

- [ ] 代码符合项目规范
- [ ] 已添加必要的测试
- [ ] 文档已更新
- [ ] **.env 文件没有被提交** ⭐

---

**注意**：本项目当前为 API + Web 演示版本，暂不包含移动端应用。