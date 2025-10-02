# LearnYourWay 文档导航（API 演示版）

> **当前阶段**：专注后端 API 开发，暂不开发移动端应用

- [01 项目总览与执行顺序（API 演示版）](01_项目总览与执行顺序.md)
- [02 环境与项目初始化（Python 后端）](02_环境与项目初始化.md)
- [03 数据摄取与PDF解析](03_数据摄取与PDF解析.md)
- [04 个性化与阅读等级调整](04_个性化与阅读等级调整.md)
- [05 学习素材生成](05_学习素材生成.md)
- [06 Web 演示界面](06_Web演示界面.md)
- [07 测试策略（后端为主）](07_移动端应用与测试.md)
- [08 部署与CI/CD](08_部署与CI_CD.md)
- [09 提示词库与风格规范](09_提示词库与风格规范.md)

## 快速开始

```bash
# 1. 初始化后端环境
conda create -n project_learn_your_way python=3.11
conda activate project_learn_your_way
cd server
pip install -r requirements.txt

# 2. 配置环境变量
# 编辑 server/.env 填入 API Key

# 3. 启动后端服务
uvicorn app.main:app --reload

# 4. 启动 Web 界面（新终端）
cd web
python -m http.server 3000

# 5. 访问
# API 文档: http://localhost:8000/docs
# Web 界面: http://localhost:3000
```