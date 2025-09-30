# 数据摄取与 PDF 解析（服务端 + Celery 队列）

目标：将 PDF/教材转换为结构化的段落、标题、注释与图片占位，为后续个性化与生成提供稳定输入。能力在服务端实现；通过 **API 接口**接收文件上传、查询解析状态与获取结果。

## 队列编排与任务划分
- 任务列表：
  - `ingest_pdf(file)`：存储文件、提取文本/版式元素，输出 `PageBlock[]`
  - `clean_and_chunk(blocks)`：清洗与分块，输出 `Chunk[]`
  - `embed_chunks(chunks)`：生成向量，写入向量库
  - `index_chunks(chunks)`：将分块与元数据入库（便于回溯）
- 状态机：`PENDING -> STARTED -> RETRY -> FAILURE | SUCCESS`
- 进度上报：维护 `stage`（upload/parse/clean/chunk/embed/index）与 `progress(0-100)`，GET 轮询返回
- 重试策略：`tenacity/backoff` 指数退避，对 OCR/模型/存储等外部依赖失败时有限重试

## 实现与提示词

### 1) 上传与导入（API 接口）
- **接口设计**：
  - `POST /ingest/pdf`：上传 PDF 文件（multipart/form-data）
  - 返回：`{ taskId, status: "pending" }`
  - `GET /ingest/tasks/:id`：轮询任务状态与进度
  
- **测试方式**：
```bash
# cURL 测试
curl -F file=@sample.pdf http://localhost:8000/ingest/pdf | jq .
curl http://localhost:8000/ingest/tasks/<taskId> | jq .

# Postman 测试
# 创建 POST 请求，Body 选择 form-data，key=file，type=File

# Python 测试脚本
import requests
with open('sample.pdf', 'rb') as f:
    response = requests.post('http://localhost:8000/ingest/pdf', files={'file': f})
    task_id = response.json()['data']['taskId']
    # 轮询状态
    status = requests.get(f'http://localhost:8000/ingest/tasks/{task_id}').json()
```

### 2) 解析 PDF（服务端）
- 工具：`pdfminer.six`/`pymupdf`（Python）或 `pdf-parse`（Node）
- 约定输出：`PageBlock{ pageNumber, blocks:[{type:'heading'|'paragraph'|'list', text, bbox}] }[]`
- 单测：多版式样例，断言页数、标题层级、断行合并

### 3) 清洗与分块
- 策略：去页眉页脚、合并断行、按语义/长度分块（token 友好）
- 接口：`cleanAndChunk(blocks, {targetTokens: 400, overlap: 50})`
- 单测：边界条件（空页、表格、脚注）与 Chunk 边界

### 4) 向量化与检索
- 起步：pgvector；进阶：Qdrant/MongoDB Atlas Vector
- 接口：`embedChunks(chunks)` / `search(query, topK)`
- 单测：固定 query 与人工标注 Top-K 一致性

### 5) 图片与 OCR（可选）
- 工具：`tesseract`、`PaddleOCR`
- 单测：关键词召回/相似度阈值

## 验收
- 3 份不同排版 PDF 的解析、清洗、分块稳定；
- 单测>95% 通过，关键函数边界覆盖充分；
- API 接口上传/轮询流程稳定，支持重试与错误处理；
- Swagger UI 文档完整，可直接在线测试。

