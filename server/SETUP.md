# 本地开发环境设置指南

## Windows 环境（使用 Conda）

### 第一步：创建 Conda 环境

```powershell
# 创建名为 learn_your_way 的 Python 3.11 环境
conda create -n learn_your_way python=3.11

# 激活环境
conda activate learn_your_way

# 验证 Python 版本
python --version  # 应该显示 Python 3.11.x
```

### 第二步：安装 Python 依赖

```powershell
# 确保在 server 目录下
cd server

# 安装依赖
pip install -r requirements.txt

# 验证安装
pip list | findstr fastapi  # 应该看到 fastapi
```

### 第三步：配置环境变量

```powershell
# 复制环境变量模板
copy .env.local.example .env

# 编辑 .env 文件
notepad .env

# 至少需要配置：
# OPENAI_API_KEY=sk-your-actual-key-here
```

### 第四步：启动依赖服务（Docker）

```powershell
# 确保 Docker Desktop 已启动

# 启动 Redis 和 PostgreSQL
docker-compose -f docker-compose.deps.yml up -d

# 验证服务运行
docker ps
# 应该看到 learnyourway_redis 和 learnyourway_postgres

# 查看日志（可选）
docker-compose -f docker-compose.deps.yml logs -f
```

### 第五步：启动 API 服务

```powershell
# 在 server 目录下
# 确保 conda 环境已激活
conda activate learn_your_way

# 启动 FastAPI 服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 你应该看到：
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 第六步：启动 Celery Worker（新终端）

```powershell
# 打开新的 PowerShell 终端
cd server

# 激活 conda 环境
conda activate learn_your_way

# 启动 Celery（Windows 需要 --pool=solo）
celery -A app.tasks.worker worker -l info --pool=solo

# 你应该看到 Celery worker 启动日志
```

### 第七步：访问 API 文档

打开浏览器访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **根路径**: http://localhost:8000/

### 第八步：运行测试（可选）

```powershell
# 运行测试
pytest tests/ -v

# 运行测试并生成覆盖率
pytest tests/ --cov=app --cov-report=html

# 查看覆盖率报告
start htmlcov/index.html
```

## 日常开发流程

### 每天开始工作

```powershell
# 1. 激活环境
conda activate learn_your_way

# 2. 拉取最新代码
git pull origin dev

# 3. 确保依赖服务运行
docker-compose -f docker-compose.deps.yml ps

# 4. 启动 API（终端 1）
uvicorn app.main:app --reload

# 5. 启动 Celery（终端 2）
celery -A app.tasks.worker worker -l info --pool=solo
```

### 每天结束工作

```powershell
# 1. Ctrl+C 停止 API 和 Celery

# 2. 提交代码
git add .
git commit -m "feat: 完成xxx功能"
git push origin dev

# 3. 依赖服务可以保持运行（可选停止）
docker-compose -f docker-compose.deps.yml down
```

## 常见问题

### Q: Celery 启动报错？
A: Windows 上必须加 `--pool=solo` 参数：
```powershell
celery -A app.tasks.worker worker -l info --pool=solo
```

### Q: Docker 容器启动失败？
A: 检查 Docker Desktop 是否运行，端口是否被占用：
```powershell
netstat -ano | findstr "6379"  # 检查 Redis 端口
netstat -ano | findstr "5432"  # 检查 PostgreSQL 端口
```

### Q: 如何重启依赖服务？
A:
```powershell
docker-compose -f docker-compose.deps.yml restart
```

### Q: 如何查看数据库内容？
A: 使用任何 PostgreSQL 客户端连接：
- Host: localhost
- Port: 5432
- Database: learnyourway_dev
- User: dev
- Password: dev

推荐工具：DBeaver, pgAdmin, VSCode PostgreSQL 扩展

### Q: pip 安装依赖很慢？
A: 使用国内镜像：
```powershell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 下一步

完成环境搭建后，可以：

1. 查看 [README.md](README.md) 了解项目结构
2. 查看 [../docs/](../docs/) 了解开发文档
3. 开始开发第一个功能！

## 需要帮助？

- 查看项目文档：[../docs/README.md](../docs/README.md)
- 查看 API 文档：http://localhost:8000/docs
- 联系团队成员
