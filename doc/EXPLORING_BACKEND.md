# Thesis Studio — EXPLORING 阶段后端技术说明

## 依赖包

EXPLORING 阶段不需要新增 Python 包。已有依赖即可覆盖全部需求：

| 包名 | 用途 | 状态 |
|------|------|------|
| `httpx` | HTTP 客户端（Semantic Scholar / arXiv API 调用） | 已有 |
| `pydantic` | 数据模型（Agent/Skill 协议、配置） | 已有 |
| Ollama / OpenAI 适配器 | LLM 调用（查询扩展、聚类分析、综述生成） | 已有 |

AI 聚类由 LLM 直接判断（主题分析+JSON 输出），不依赖 scikit-learn 等算法包。

## API 接口

### Semantic Scholar API
- **Base URL**: `https://api.semanticscholar.org/graph/v1`
- **搜索端点**: `GET /paper/search?query=...&limit=...&fields=...`
- **认证**: 可选，在 HTTP Header 加 `x-api-key`。免费 key 申请地址：https://www.semanticscholar.org/product/api
- **限流**: 无 key 100 req/5min，有 key 100 req/s
- **配置**: 在 `.env` 中设置 `THESIS_STUDIO_SEMANTIC_SCHOLAR_API_KEY=your_key`

### arXiv API
- **Base URL**: `http://export.arxiv.org/api/query`
- **参数**: `search_query`, `start`, `max_results`, `sortBy`
- **认证**: 无需认证
- **限流**: 无硬性限制，建议请求间隔 ≥3s
- **注意**: 国内可能需科学上网

### LLM (Ollama / OpenAI)
- **Ollama**: 本地运行，默认 `http://localhost:11434`，模型 `qwen2.5`
- **OpenAI**: 需在 `.env` 中配置 `THESIS_STUDIO_OPENAI_API_KEY`

## 架构概览

```
domain/
  agent/
    base.py         → SandboxConfig + AgentProtocol
    researcher.py   → Paper, PaperCluster, LiteratureReview (纯数据)
  skill/
    base.py         → Skill 协议 (Pydantic)
    interfaces.py   → 4 个 Skill 输入输出模型

infrastructure/
  sandbox.py        → 路径/API 访问控制 + 超时
  search/
    semantic_scholar.py → Semantic Scholar 客户端
    arxiv_client.py     → arXiv 客户端
  skill/
    skills.py        → 4 个 Skill 实现 (AcademicSearch, PaperParser, Cluster, ReviewGen)
  agent/
    researcher_impl.py → Researcher Agent 实现 (LLM + Skills)

application/
  exploring/
    agent_service.py → 消息路由 + 流式 SSE 桥接 + 完整 pipeline
```

## 使用方式

```python
from thesis_studio.infrastructure.llm.factory import LLMFactory
from thesis_studio.application.exploring.agent_service import AgentService

llm = LLMFactory().create()
svc = AgentService(llm)

# 发送消息
msg = await svc.send_message("机器学习在医疗诊断中的应用", "researcher")

# 或流式 pipeline
async for event in svc.run_explore_pipeline("深度学习图像识别"):
    print(event)  # {"type": "progress", "stage": "search", ...}
```
