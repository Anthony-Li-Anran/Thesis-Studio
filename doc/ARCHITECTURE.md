# Thesis Studio 架构文档

> 基于 **Clean Architecture + Hexagonal Architecture + SOLID** 原则构建的 AI 论文研究助手。

---

## 一、架构总览

```
┌──────────────────────────────────────────────────────────────┐
│                    接口层 (Presentation)                      │
│  FastAPI REST API  │  Chainlit 对话  │  NiceGUI 管理面板      │
├──────────────────────────────────────────────────────────────┤
│                    应用层 (Application)                       │
│  LiteratureSearch  │  LiteratureManage  │  Writing  │  Analysis │
├──────────────────────────────────────────────────────────────┤
│                    领域层 (Domain)                            │
│  实体 (Entities)  │  端口协议 (Ports)  │  领域异常             │
├──────────────────────────────────────────────────────────────┤
│                 基础设施层 (Infrastructure)                    │
│  LLM 适配器  │  DB 仓储  │  ChromaDB  │  组合根 (Bootstrap)    │
└──────────────────────────────────────────────────────────────┘
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
├── exceptions.py          # 13 种领域异常层级
├── models/
│   ├── __init__.py
│   ├── paper.py           # Paper 实体 + PaperStatus 枚举 + from_dict()
│   ├── project.py         # Project 实体 + ProjectStatus 枚举
│   └── search.py          # SearchQuery / SearchResult 值对象
└── ports/
    ├── __init__.py
    ├── llm_port.py         # LLMProvider 协议 (generate + generate_stream)
    ├── embedding_port.py   # EmbeddingProvider 协议 (embed + embed_batch)
    ├── repository_port.py  # PaperRepository + ProjectRepository 协议
    └── search_port.py      # LiteratureSearchProvider 协议
```

**设计原则**:
- 所有实体是纯 Python `dataclass`，无 ORM 注解、无框架依赖
- 端口接口使用 `typing.Protocol`（结构化类型），不依赖具体实现
- 异常层级清晰：`Thesis StudioError → LLMError → LLMUnavailableError`
- `Paper.from_dict()` 封装了检索结果到领域实体的映射逻辑

### 2.2 应用层 (`application/`) — 用例编排

```
application/
├── __init__.py
├── literature/
│   ├── __init__.py
│   ├── search_service.py   # LiteratureSearchService: 多源检索→去重→入库
│   └── manage_service.py   # LiteratureManageService: 筛选/分类/综述生成
├── analysis/
│   └── __init__.py          # AnalysisService: 数据理解/结果解释
└── writing/
    └── __init__.py           # WritingService: 大纲生成/章节撰写/润色
```

**设计原则**:
- 只依赖 `domain.ports.*` 抽象接口，不导入任何具体实现
- 每个 Service 通过构造函数注入依赖（DIP）
- 抛出领域异常（`ValidationError`）而非 Python 内置异常

### 2.3 基础设施层 (`infrastructure/`) — 适配器实现

```
infrastructure/
├── __init__.py
├── bootstrap/
?   ??? __init__.py          # ? ????get_services / get_current_user_repo / clear_guest_projects
├── db/
│   ├── __init__.py
│   ├── sqlite.py            # SQLite 异步引擎 + ORM 模型 + 会话管理
│   ├── chroma.py            # ChromaDB 向量数据库客户端（线程安全单例）
│   └── repositories.py      # SQLitePaperRepository / SQLiteProjectRepository
├── llm/
│   ├── __init__.py
│   ├── ollama_adapter.py    # OllamaAdapter: 实现 LLMProvider
│   ├── openai_adapter.py    # OpenAIAdapter: 实现 LLMProvider
│   └── factory.py           # LLMFactory: 按配置创建适配器
├── embedding/
│   └── __init__.py           # 嵌入适配器（Phase 2）
└── search/
    └── __init__.py           # 检索适配器（Phase 2）
```

**设计原则**:
- 所有适配器实现对应的 `domain.ports.*` 协议
- **组合根模式**: `bootstrap/__init__.py` 是唯一组装所有依赖的地方
- Repository 通过构造函数注入 `session_factory`（可测试）
- `LLMFactory` 遵循开闭原则：新增 Provider 只需加一个 case 分支

### 2.4 接口层 (`presentation/`) — 对外接口

```
presentation/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── app.py              # FastAPI 应用工厂 + CORS + 异常处理
│   ├── routes.py            # REST 路由: /health /papers /writing /analysis
│   └── dependencies.py      # DI 重导出（桥接 infrastructure.bootstrap）
└── ui/
    ├── __init__.py
    ??? auth_card.py          # 登录/注册/游客认证卡片
    ??? delete_confirm_card.py # ?????????
    ??? edit_project_card.py  # 项目编辑卡片
    ??? home_page.py          # 首页（项目列表/搜索/排序/视图切换）
    ??? i18n.py               # 中英文国际化
    ??? new_project_card.py   # 新建项目卡片
    ??? project_menu.py       # 项目三点菜单（编辑/删除）
    ??? project_page.py       # 项目详情页
    ??? settings_card.py      # 设置卡片（齿轮入口）
    ??? theme.py              # 主题 & 样式系统
```

**设计原则**:
- `dependencies.py` 不直接导入具体实现，而是从 `infrastructure.bootstrap` 重导出
- 异常处理器按异常类型映射 HTTP 状态码（`LLMUnavailableError → 503`）
- Chainlit 在 `on_chat_start` 中创建 LLM 实例并复用（避免每次消息重建）

### 2.5 配置与核心 (`config/` + `core/`)

```
config/
├── __init__.py
└── settings.py             # Pydantic Settings: LLM/DB/API 全局配置

core/
├── __init__.py
├── exceptions.py            # 兼容重导出 → domain.exceptions
└── logging.py               # 结构化日志（stderr 输出）
```

---

## 三、依赖注入与组合根

所有服务的组装集中在 `infrastructure/bootstrap/__init__.py`：

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

Presentation 层通过 `dependencies.py` 桥接获取服务，不直接依赖 Infrastructure：

```python
# presentation/api/dependencies.py
from ...infrastructure.bootstrap import get_services  # 纯重导出
```

---

## 四、兼容层

旧模块路径（`llm/`, `db/`, `api/`, `ui/`, `models/`, `embedding/`）保留为纯重导出：

```python
# llm/__init__.py
from ..domain.ports.llm_port import LLMProvider
from ..infrastructure.llm.factory import LLMFactory
```

保证渐进迁移，不破坏现有引用。

---

## 五、SOLID 合规

| 原则 | 实现方式 |
|------|----------|
| **SRP** 单一职责 | 仓储与引擎分离；路由与工厂分离；映射逻辑提取为 `from_dict()` |
| **OCP** 开闭原则 | `LLMFactory` 新增 Provider 不改旧代码；端口/适配器分离允许新实现 |
| **LSP** 里氏替换 | 所有适配器通过 Protocol 端口可替换（Ollama ↔ OpenAI） |
| **ISP** 接口隔离 | 端口接口精简：`LLMProvider` 仅 2 个方法，`EmbeddingProvider` 仅 2 个方法 |
| **DIP** 依赖反转 | Application 只依赖 `domain.ports.*`；Repository 通过构造函数注入 `session_factory` |

---

## 六、数据流

```
用户请求 → FastAPI routes.py
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
         外部服务 (Ollama/OpenAI/SQLite/ChromaDB)
```

---

## 七、质量门禁

| 工具 | 配置 | 状态 |
|------|------|------|
| **ruff** | 行宽 100, py311, E/F/W/I/N/UP/B/SIM | ✅ All checks passed |
| **mypy** | strict=true, 66 files | ✅ No issues found |
| **pytest** | asyncio_mode=auto, 5 tests | ✅ 5/5 passed |

---

## 八、关键设计决策

1. **Protocol 而非 ABC**: 使用 `typing.Protocol` 定义端口，支持结构化子类型（无需显式继承）
2. **组合根在 Infrastructure**: 遵循 Clean Architecture——组合根在最外层，Presentation 通过重导出桥接
3. **领域实体含 `id`**: `Paper` 和 `Project` 自带 `uuid4` 生成的 `id`，Repository 的 `update()` 按 id 定位
4. **`from_dict()` 在领域层**: 检索结果到实体的映射逻辑归属领域层，避免应用层包含数据转换代码

## 多Agents团队配置

Researcher / Executor / Reviewer / Writer / Debater