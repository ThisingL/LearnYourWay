# 部署与 CI/CD

目标：提供可重复部署流程，并以自动化测试作为门禁，确保质量。当前阶段专注**后端服务部署**。

## 任务清单
1. Docker 化后端；多阶段构建
2. 环境配置与密钥注入
3. CI：安装依赖、构建、测试、产物缓存
4. CD：后端部署（Cloud Run/Fly.io/Render/Railway 等）
5. 监控与告警（日志、指标、健康检查）

## Docker 化后端

### Dockerfile（多阶段构建）
```dockerfile
# 构建阶段
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 运行阶段
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# 使用 Gunicorn + Uvicorn workers
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--workers", "4"]
```

### docker-compose.yml（本地开发）
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - redis
      - postgres
    volumes:
      - ./app:/app/app
    command: uvicorn app.main:app --host 0.0.0.0 --reload

  celery:
    build: .
    env_file:
      - .env
    depends_on:
      - redis
    command: celery -A app.tasks.worker worker -l info

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: learnyourway
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## CI/CD 流水线（GitHub Actions）

### .github/workflows/ci.yml
```yaml
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: 设置 Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: 安装依赖
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: 运行测试
        env:
          REDIS_URL: redis://localhost:6379/0
          DB_URL: postgresql://test:test@localhost:5432/test_db
        run: |
          pytest tests/ -v --cov=app --cov-report=xml --cov-report=term
      
      - name: 上传覆盖率
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: 登录 Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: 构建并推送镜像
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKER_USERNAME }}/learnyourway:latest
            ${{ secrets.DOCKER_USERNAME }}/learnyourway:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: 部署到生产环境
        # 根据选择的平台配置
        # 示例：Render/Railway/Fly.io 通常支持自动部署
        run: echo "部署完成"
```

## 部署平台选择

### 推荐平台（按复杂度）
1. **Railway/Render**（最简单）
   - 一键部署，自动检测 Dockerfile
   - 内置数据库与 Redis
   - 免费额度适合演示

2. **Fly.io**（轻量级）
   - 全球边缘部署
   - 支持多区域
   - 配置文件部署

3. **Cloud Run**（Google Cloud）
   - 按需扩容
   - 容器化部署
   - 与 GCP 生态集成

4. **AWS ECS/Fargate**（企业级）
   - 完全控制
   - VPC 网络隔离
   - 适合生产环境

### 环境变量配置
```bash
# 在部署平台配置以下环境变量
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-xxx
REDIS_URL=redis://...
DB_URL=postgresql://...
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

## 监控与观测

### 健康检查端点
```python
# app/api/health.py
@router.get("/healthz")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": os.getenv("APP_VERSION", "unknown")
    }

@router.get("/readyz")
async def readiness_check():
    # 检查关键依赖
    redis_ok = await check_redis()
    db_ok = await check_database()
    
    if redis_ok and db_ok:
        return {"status": "ready"}
    else:
        raise HTTPException(status_code=503, detail="Not ready")
```

### 日志与指标
```python
# 结构化日志
import structlog

logger = structlog.get_logger()

logger.info("task_started", 
    task_id=task_id, 
    task_type="pdf_ingest",
    user_id=user_id
)
```

### 可选：OpenTelemetry 追踪
```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

FastAPIInstrumentor.instrument_app(app)
```

## 质量门禁
- **测试覆盖率**：> 80%
- **API 契约测试**：100% 端点覆盖
- **性能基准**：P95 < 2s
- **安全扫描**：无高危漏洞

## 发布流程
1. 开发分支 → PR 到 `main`
2. 自动运行 CI（测试 + 构建）
3. Code Review 通过后合并
4. 自动部署到演示环境
5. 手动验证后推广到生产环境（如需要）

