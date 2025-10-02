# LearnYourWay Web 演示界面

简单美观的 Web 界面，用于演示个性化学习内容生成功能。

## 快速开始

### 方式 1：直接打开（无需服务器）

```bash
# 确保后端 API 已启动
cd ../server
uvicorn app.main:app --reload

# 直接在浏览器打开 web/index.html
# 或使用 Python 简单服务器
cd web
python -m http.server 3000

# 访问 http://localhost:3000
```

### 方式 2：集成到 FastAPI

将 web 目录复制到 server 下，作为静态文件服务。

## 功能说明

### 1. 用户画像设置
- 输入用户 ID
- 选择年级（1-12）
- 添加兴趣标签
- 保存到 localStorage 和后端

### 2. 内容生成
- 输入学习内容
- 一键生成：
  - 📝 测验题（单选/多选/判断/简答）
  - 🧠 思维导图（可视化知识结构）
  - 📖 沉浸式文本（故事化表达）

### 3. 结果展示
- Tab 切换查看不同素材
- 折叠式答案展示
- 思维导图交互式可视化

## 技术栈

- **纯前端**：HTML + CSS + JavaScript
- **UI**：Tailwind CSS (CDN)
- **HTTP**：Axios (CDN)
- **图表**：ECharts (CDN)
- **无需构建**：直接打开即可使用

## 文件结构

```
web/
├── index.html    # 主页面
├── app.js        # 业务逻辑
└── README.md     # 本文档
```

## 配置

确保后端 API 允许跨域访问（已在 FastAPI 中配置 CORS）。

API 地址配置在 `app.js` 第一行：
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

## 使用流程

1. 启动后端 API
2. 打开 web/index.html
3. 设置用户画像（年级、兴趣）
4. 输入学习内容
5. 点击生成按钮
6. 查看 AI 生成的学习素材

## 截图

（可在此添加界面截图）

## 未来优化

- [ ] 添加 PDF 上传功能
- [ ] 添加历史记录
- [ ] 导出功能（PDF、Word）
- [ ] 更丰富的思维导图样式
- [ ] 暗色模式
