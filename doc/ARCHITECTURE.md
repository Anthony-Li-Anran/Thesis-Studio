# Thesis Studio 架构文档

> 基于 **Clean Architecture + Hexagonal Architecture + SOLID** 原则构建的 AI 论文研究助手。场景B：用户带明确题目入场，系统辅助全流程落地。

---

## 一、架构总览

```
┌──────────────────────────────────────────────────────────────────┐
│                    接口层 (Presentation)                          │
│  FastAPI REST API  │  NiceGUI 管理面板  │  Chainlit 对话          │
│  exploring/ (聊天室+知识图谱+文献库)  │  designing/ (辩论+大纲编辑) │
├──────────────────────────────────────────────────────────────────┤
│                    应用层 (Application)                           │
│  exploring/agent_service.py  (消息路由 + 流式 SSE + 意图分发)      │
├──────────────────────────────────────────────────────────────────┤
│                    领域层 (Domain)                                │
│  实体 (models/)  │  端口协议 (ports/)  │  领域异常 (exceptions.py) │
│  Agent 协议 (agent/)  │  Skill 协议 (skill/)  │  工作流 (workflow/) │
├──────────────────────────────────────────────────────────────────┤
│                 基础设施层 (Infrastructure)                        │
│  LLM 适配器  │  DB 仓储  │  ChromaDB  │  搜索客户端  │  沙箱       │
│  Agent 实现  │  Skill 实现  │  组合根 (bootstrap/)                 │
└──────────────────────────────────────────────────────────────────┘
```

**依赖方向**: 外层依赖内层抽象，内层不感知外层。所有依赖指向领域层。

```
Presentation → Application → Domain ← Infrastructure
                                  ↑
                         (端口/适配器)
```

---

## 二、分层详解

### 2.1 领域层 (`domain/`) — 最内层，零外部依赖

```
domain/
├── __init__.py
├── exceptions.py             # 领域异常层级
├── models/
│   ├── __init__.py
│   ├── paper.py              # Paper 实体 + PaperStatus 枚举
│   ├── project.py            # Project 实体 + ProjectStatus 7 状态机
│   ├── search.py             # SearchQuery / SearchResult 值对象
│   ├── settings.py           # 设置相关值对象
│   └── user.py               # User 实体
├── ports/
│   ├── __init__.py
│   ├── llm_port.py           # LLMProvider 协议 (generate + generate_stream)
│   ├── embedding_port.py     # EmbeddingProvider 协议
│   ├── repository_port.py    # PaperRepository + ProjectRepository 协议
│   ├── search_port.py        # LiteratureSearchProvider 协议
│   └── auth_port.py          # AuthProvider 协议
├── agent/
│   ├── __init__.py
│   ├── base.py               # AgentProtocol 协议 + AgentMessage 数据模型
│   └── researcher.py         # ResearcherAgent 协议
├── skill/
│   ├── __init__.py
│   ├── base.py               # Skill 基类
│   ├── interfaces.py         # Skill 接口定义
│   └── designing.py          # DESIGNING 阶段专用 Skill
└── workflow/
    ├── __init__.py
    ├── base.py               # Workflow 基类
    ├── exploring_state.py    # EXPLORING 阶段状态定义
    ├── exploring_graph.py    # EXPLORING LangGraph 工作流图
    └── granularity_check.py  # 大纲粒度校验（DESIGNING 门禁）
```

**设计原则**:
- 所有实体是纯 Python `dataclass`，无 ORM 注解、无框架依赖
- 端口接口使用 `typing.Protocol`（结构化类型），不依赖具体实现
- Agent/Skill/Workflow 均为协议定义，具体实现由基础设施层提供
- 异常层级清晰：`ThesisStudioError → LLMError → LLMUnavailableError`

### 2.2 应用层 (`application/`) — 用例编排

```
application/
├── __init__.py
└── exploring/
    ├── __init__.py
    └── agent_service.py      # AgentService: 消息路由→意图分类→流式 SSE 桥接
```

**设计原则**:
- 只依赖 `domain.ports.*` 和 `domain.agent.*` 抽象接口
- 通过构造函数注入依赖（DIP）
- 抛出领域异常而非 Python 内置异常

### 2.3 基础设施层 (`infrastructure/`) — 适配器实现

```
infrastructure/
├── __init__.py
├── logging.py                # 结构化日志
├── sandbox.py                # 代码执行沙箱（安全隔离）
├── bootstrap/                # 组合根：DI 装配与服务工厂
├── db/
│   ├── __init__.py
│   ├── sqlite.py             # SQLite 异步引擎 + ORM + 会话管理
│   ├── chroma.py             # ChromaDB 向量数据库客户端
│   └── repositories.py       # SQLitePaperRepository / SQLiteProjectRepository
├── llm/
│   ├── __init__.py
│   ├── ollama_adapter.py     # OllamaAdapter: 实现 LLMProvider
│   ├── openai_adapter.py     # OpenAIAdapter: 实现 LLMProvider
│   └── factory.py            # LLMFactory: 按配置创建适配器
├── embedding/                # 嵌入适配器
├── search/
│   ├── __init__.py
│   ├── semantic_scholar.py   # Semantic Scholar API 客户端
│   └── arxiv.py              # arXiv API 客户端
├── agent/
│   ├── __init__.py
│   └── researcher_impl.py    # ResearcherAgent 实现（LangGraph 工作流）
└── skill/                    # Skill 实现（检索/聚类/综述/搜索等）
```

**设计原则**:
- 每个适配器实现 `domain.ports.*` 中定义的 Protocol
- `LLMFactory` 遵循开闭原则：新增 Provider 只需加一个 case 分支
- 组合根（`bootstrap/`）是唯一知道所有具体实现的模块
- 沙箱模块提供安全的代码执行隔离环境

### 2.4 接口层 (`presentation/`) — 对外接口

```
presentation/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── app.py                # FastAPI 应用工厂 + CORS + 异常处理
│   ├── routes.py             # REST 路由
│   └── dependencies.py       # DI 重导出（桥接 infrastructure.bootstrap）
└── ui/
    ├── __init__.py
    ├── nicegui_app.py        # NiceGUI 应用入口
    ├── chainlit_app.py       # Chainlit 对话入口
    ├── home_page.py          # 首页（项目列表/搜索/排序/视图切换）
    ├── auth_card.py          # 登录/注册/游客认证卡片
    ├── new_project_card.py   # 新建项目卡片
    ├── edit_project_card.py  # 项目编辑卡片
    ├── delete_confirm_card.py # 删除确认卡片
    ├── project_menu.py       # 项目三点菜单
    ├── project_page.py       # 项目详情页（工作流交互界面）
    ├── settings_card.py      # 设置卡片（AI 配置 CRUD）
    ├── theme.py              # 主题 & 样式系统
    ├── i18n.py               # 中英文国际化
    ├── exploring/            # EXPLORING 阶段 UI
    │   ├── __init__.py
    │   ├── exploring_page.py # 主页面（双栏布局）
    │   ├── chat_room.py      # 微信式聊天室
    │   ├── config.py         # 阶段配置
    │   ├── knowledge_graph.py # 知识图谱（echarts 力导向图）
    │   ├── literature_library.py # 文献库面板
    │   ├── paper_detail.py   # 文献详情面板
    │   └── stage_progress.py # 阶段进度条
    └── designing/            # DESIGNING 阶段 UI
        ├── __init__.py
        ├── designing_page.py # 主页面（35/65 双栏）
        ├── designing_chat.py # 聊天室（多 Agent 辩论 + @mention）
        ├── chat_renderer.py  # 消息渲染器
        ├── at_mention.js     # @mention 前端 JS
        ├── outline_editor.py # 大纲协同编辑器（三模式）
        ├── checklist.py      # 进度检查清单
        ├── format_requirements.py # 格式要求抽屉
        ├── diff_card.py      # Diff 建议卡片
        └── debate_orchestrator.py # 辩论编排器
```

### 2.5 配置层 (`config/`)

```
config/
├── __init__.py
└── settings.py               # Pydantic Settings: LLM/DB/API/Agent 全局配置
```

---

## 三、依赖注入与组合根

所有服务的组装集中在 `infrastructure/bootstrap/`：

```python
# 组合根：唯一知道所有具体实现的模块
def get_services() -> Services:
    llm = LLMFactory(get_settings()).create()
    paper_repo = SQLitePaperRepository()
    project_repo = SQLiteProjectRepository()
    return Services(
        literature_search = LiteratureSearchService([], paper_repo),
        literature_manage = LiteratureManageService(paper_repo, llm),
        writing = WritingService(llm, project_repo, paper_repo),
        analysis = AnalysisService(llm),
    )
```

Presentation 层通过 `dependencies.py` 桥接获取服务，不直接依赖 Infrastructure。

---

## 四、工作流与 Agent 协作

### 4.1 7 状态机

```
INIT → EXPLORING → DESIGNING → RESEARCHING → WRITING → POLISHING → COMPLETED
```

每个状态对应一个工作流阶段，阶段间线性推进，阶段内允许多轮迭代。

### 4.2 Agent 团队

| Agent | 职责 | 活跃阶段 |
|-------|------|----------|
| **Researcher** | 文献检索、聚类分析、算法建议、研究背景 | EXPLORING, DESIGNING, RESEARCHING |
| **Debater** | 质疑研究设计、提出反例、挑战假设 | DESIGNING |
| **Reviewer** | 审查输出质量、粒度校验、合规检查 | DESIGNING, RESEARCHING |
| **Executor** | 代码编写、沙箱执行、自修复、LaTeX 推导 | RESEARCHING |
| **Writer** | 章节撰写、润色、引用管理 | WRITING |

### 4.3 多 Agent 协作模式

- **EXPLORING**: 单 Agent（Researcher）检索→聚类→综述
- **DESIGNING**: 多 Agent 辩论（R→D→R 循环，最多 3 轮）+ Reviewer 审查 + 用户确认
- **RESEARCHING**: IDE 模式（Executor 写代码 + Researcher 建议 + Reviewer 审查）或 LaTeX 模式（理论推导）

---

## 五、SOLID 合规

| 原则 | 实现方式 |
|------|----------|
| **SRP** 单一职责 | 仓储与引擎分离；路由与工厂分离；映射逻辑提取为 `from_dict()` |
| **OCP** 开闭原则 | `LLMFactory` 新增 Provider 不改旧代码；端口/适配器分离允许新实现 |
| **LSP** 里氏替换 | 所有适配器通过 Protocol 端口可替换（Ollama ↔ OpenAI） |
| **ISP** 接口隔离 | 端口接口精简：`LLMProvider` 仅 2 个方法，`EmbeddingProvider` 仅 2 个方法 |
| **DIP** 依赖反转 | Application 只依赖 `domain.ports.*`；Repository 通过构造函数注入 |

---

## 六、数据流

```
用户请求 → FastAPI routes.py / NiceGUI / Chainlit
              ↓
         dependencies.py (DI 桥接)
              ↓
         infrastructure/bootstrap (组合根)
              ↓
         application/*Service (用例编排)
              ↓
         domain/ports/* (抽象端口)
              ↓
         infrastructure/* (适配器实现)
              ↓
         外部服务 (Ollama/OpenAI/SQLite/ChromaDB/Semantic Scholar/arXiv)
```

---

## 七、质量门禁

| 工具 | 配置 | 状态 |
|------|------|------|
| **ruff** | 行宽 100, py311, E/F/W/I/N/UP/B/SIM | ✅ All checks passed |
| **mypy** | strict=true | ✅ No issues found |
| **pytest** | asyncio_mode=auto | ✅ |

---

## 八、关键设计决策

1. **Protocol 而非 ABC**: 使用 `typing.Protocol` 定义端口，支持结构化子类型（无需显式继承）
2. **组合根在 Infrastructure**: 遵循 Clean Architecture——组合根在最外层，Presentation 通过重导出桥接
3. **领域实体含 `id`**: `Paper` 和 `Project` 自带 `uuid4` 生成的 `id`，Repository 的 `update()` 按 id 定位
4. **`from_dict()` 在领域层**: 检索结果到实体的映射逻辑归属领域层，避免应用层包含数据转换代码
5. **Agent/Skill/Workflow 协议化**: 领域层定义协议，基础设施层实现，支持多 Agent 协作与阶段编排
6. **沙箱隔离代码执行**: RESEARCHING 阶段代码在独立沙箱中执行，保证安全性
7. **阶段状态持久化**: 每个阶段的状态序列化到 Project 实体，支持中断恢复
