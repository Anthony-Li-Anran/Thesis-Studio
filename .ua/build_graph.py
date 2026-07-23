"""生成 ThesisOS 知识图谱 JSON。"""
import json
import os
from datetime import datetime

PROJECT_ROOT = r"e:\AutoResearch\ThesisOS"
UA_DIR = os.path.join(PROJECT_ROOT, ".ua")
os.makedirs(os.path.join(UA_DIR, "intermediate"), exist_ok=True)

graph = {
    "version": "1.0.0",
    "project": {
        "name": "ThesisOS",
        "languages": ["python", "markdown", "toml"],
        "frameworks": ["FastAPI", "Pydantic", "SQLAlchemy", "Chainlit", "NiceGUI", "ChromaDB", "Ollama", "OpenAI"],
        "description": "面向毕业论文生成的 AI 研究助手 — Clean Architecture + Hexagonal + SOLID",
        "analyzedAt": datetime.now().isoformat(),
        "gitCommitHash": "4d8244d2d429ff1508064f05db1c667674945ef8",
    },
    "nodes": [],
    "edges": [],
    "layers": [],
    "tour": [],
}

nodes = []

# --- Domain Layer ---
domain = [
    ("src/thesisos/domain/__init__.py", "领域层入口", ["domain", "entry"]),
    ("src/thesisos/domain/exceptions.py", "领域异常层级（13种异常）", ["domain", "exceptions"]),
    ("src/thesisos/domain/models/__init__.py", "领域实体导出", ["domain", "models"]),
    ("src/thesisos/domain/models/paper.py", "论文实体 + PaperStatus 枚举", ["domain", "entity", "paper"]),
    ("src/thesisos/domain/models/project.py", "项目实体 + ProjectStatus 枚举", ["domain", "entity", "project"]),
    ("src/thesisos/domain/models/search.py", "检索值对象 SearchQuery/SearchResult", ["domain", "value-object", "search"]),
    ("src/thesisos/domain/ports/__init__.py", "端口接口导出", ["domain", "ports"]),
    ("src/thesisos/domain/ports/llm_port.py", "LLMProvider 协议（generate + generate_stream）", ["domain", "port", "llm"]),
    ("src/thesisos/domain/ports/embedding_port.py", "EmbeddingProvider 协议", ["domain", "port", "embedding"]),
    ("src/thesisos/domain/ports/repository_port.py", "PaperRepository + ProjectRepository 协议", ["domain", "port", "repository"]),
    ("src/thesisos/domain/ports/search_port.py", "LiteratureSearchProvider 协议", ["domain", "port", "search"]),
]
for fp, summary, tags in domain:
    nodes.append({"id": f"file:{fp}", "type": "file", "name": os.path.basename(fp), "filePath": fp, "summary": summary, "tags": tags, "complexity": "simple"})

# --- Application Layer ---
app = [
    ("src/thesisos/application/__init__.py", "应用层入口", ["application"]),
    ("src/thesisos/application/literature/__init__.py", "文献用例导出", ["application", "literature"]),
    ("src/thesisos/application/literature/search_service.py", "文献检索用例：多源检索→去重→入库", ["application", "literature", "search"]),
    ("src/thesisos/application/literature/manage_service.py", "文献管理用例：筛选/分类/综述生成", ["application", "literature", "manage"]),
    ("src/thesisos/application/analysis/__init__.py", "数据分析用例：数据理解/结果解释", ["application", "analysis"]),
    ("src/thesisos/application/writing/__init__.py", "论文撰写用例：大纲/章节/润色", ["application", "writing"]),
]
for fp, summary, tags in app:
    nodes.append({"id": f"file:{fp}", "type": "file", "name": os.path.basename(fp), "filePath": fp, "summary": summary, "tags": tags, "complexity": "moderate"})

# --- Infrastructure Layer ---
infra = [
    ("src/thesisos/infrastructure/__init__.py", "基础设施层入口", ["infrastructure"]),
    ("src/thesisos/infrastructure/db/__init__.py", "数据库适配器导出", ["infrastructure", "db"]),
    ("src/thesisos/infrastructure/db/sqlite.py", "SQLite 异步引擎 + ORM 模型 + 会话管理", ["infrastructure", "db", "sqlite", "orm"]),
    ("src/thesisos/infrastructure/db/chroma.py", "ChromaDB 向量数据库客户端（线程安全单例）", ["infrastructure", "db", "chromadb", "vector"]),
    ("src/thesisos/infrastructure/db/repositories.py", "SQLite 仓储实现（PaperRepository + ProjectRepository）", ["infrastructure", "db", "repository"]),
    ("src/thesisos/infrastructure/llm/__init__.py", "LLM 适配器导出", ["infrastructure", "llm"]),
    ("src/thesisos/infrastructure/llm/ollama_adapter.py", "Ollama 本地模型适配器（实现 LLMProvider）", ["infrastructure", "llm", "ollama"]),
    ("src/thesisos/infrastructure/llm/openai_adapter.py", "OpenAI 云端模型适配器（实现 LLMProvider）", ["infrastructure", "llm", "openai"]),
    ("src/thesisos/infrastructure/llm/factory.py", "LLM 适配器工厂（按配置创建实例）", ["infrastructure", "llm", "factory"]),
    ("src/thesisos/infrastructure/embedding/__init__.py", "嵌入适配器（占位，Phase 2 实现）", ["infrastructure", "embedding"]),
    ("src/thesisos/infrastructure/search/__init__.py", "检索适配器（占位，Phase 2 实现）", ["infrastructure", "search"]),
]
for fp, summary, tags in infra:
    cpx = "complex" if "repositories" in fp else "moderate"
    nodes.append({"id": f"file:{fp}", "type": "file", "name": os.path.basename(fp), "filePath": fp, "summary": summary, "tags": tags, "complexity": cpx})

# --- Presentation Layer ---
pres = [
    ("src/thesisos/presentation/__init__.py", "接口层入口", ["presentation"]),
    ("src/thesisos/presentation/api/__init__.py", "API 模块导出", ["presentation", "api"]),
    ("src/thesisos/presentation/api/app.py", "FastAPI 应用工厂 + CORS + 异常处理", ["presentation", "api", "fastapi"]),
    ("src/thesisos/presentation/api/routes.py", "API 路由：/health, /papers, /writing, /analysis", ["presentation", "api", "routes"]),
    ("src/thesisos/presentation/api/dependencies.py", "依赖注入容器：Services 单例组装所有用例", ["presentation", "api", "di"]),
    ("src/thesisos/presentation/ui/__init__.py", "UI 模块导出", ["presentation", "ui"]),
    ("src/thesisos/presentation/ui/chainlit_app.py", "Chainlit 对话交互界面（复用 LLM 实例）", ["presentation", "ui", "chainlit"]),
    ("src/thesisos/presentation/ui/nicegui_app.py", "NiceGUI 管理面板（文献库/进度/分析/设置）", ["presentation", "ui", "nicegui"]),
]
for fp, summary, tags in pres:
    nodes.append({"id": f"file:{fp}", "type": "file", "name": os.path.basename(fp), "filePath": fp, "summary": summary, "tags": tags, "complexity": "moderate"})

# --- Config & Core ---
cc = [
    ("src/thesisos/config/__init__.py", "配置模块导出", ["config"]),
    ("src/thesisos/config/settings.py", "Pydantic Settings：LLM/DB/API 全局配置", ["config", "pydantic", "settings"]),
    ("src/thesisos/core/__init__.py", "核心工具导出", ["core"]),
    ("src/thesisos/core/logging.py", "结构化日志配置（stderr 输出）", ["core", "logging"]),
    ("src/thesisos/core/exceptions.py", "异常兼容重导出 → domain.exceptions", ["core", "exceptions", "compat"]),
]
for fp, summary, tags in cc:
    nodes.append({"id": f"file:{fp}", "type": "file", "name": os.path.basename(fp), "filePath": fp, "summary": summary, "tags": tags, "complexity": "simple"})

# --- Compat Layer ---
compat = [
    ("src/thesisos/api/__init__.py", "API 兼容重导出 → presentation.api", ["compat"]),
    ("src/thesisos/api/app.py", "旧 API 工厂（兼容）", ["compat"]),
    ("src/thesisos/ui/__init__.py", "UI 兼容重导出 → presentation.ui", ["compat"]),
    ("src/thesisos/ui/chainlit_app.py", "旧 Chainlit（兼容）", ["compat"]),
    ("src/thesisos/ui/nicegui_app.py", "旧 NiceGUI（兼容）", ["compat"]),
    ("src/thesisos/db/__init__.py", "DB 兼容重导出 → infrastructure.db", ["compat"]),
    ("src/thesisos/db/sqlite.py", "旧 SQLite 引擎（兼容）", ["compat"]),
    ("src/thesisos/db/chroma.py", "旧 ChromaDB（兼容）", ["compat"]),
    ("src/thesisos/llm/__init__.py", "LLM 兼容重导出 → infrastructure.llm", ["compat"]),
    ("src/thesisos/llm/base.py", "旧 LLMProvider 协议（兼容）", ["compat"]),
    ("src/thesisos/llm/ollama.py", "旧 OllamaProvider（兼容）", ["compat"]),
    ("src/thesisos/llm/openai.py", "旧 OpenAIProvider（兼容）", ["compat"]),
    ("src/thesisos/llm/factory.py", "旧 LLM 工厂（兼容）", ["compat"]),
    ("src/thesisos/embedding/__init__.py", "Embedding 兼容重导出", ["compat"]),
    ("src/thesisos/embedding/base.py", "旧 EmbeddingProvider 协议（兼容）", ["compat"]),
    ("src/thesisos/models/__init__.py", "Models 兼容重导出", ["compat"]),
    ("src/thesisos/models/base.py", "旧 ORM 基类（兼容）", ["compat"]),
]
for fp, summary, tags in compat:
    nodes.append({"id": f"file:{fp}", "type": "file", "name": os.path.basename(fp), "filePath": fp, "summary": summary, "tags": tags, "complexity": "simple"})

# --- Placeholder ---
ph = [
    ("src/thesisos/analysis/__init__.py", "分析模块（占位）", ["placeholder"]),
    ("src/thesisos/literature/__init__.py", "文献模块（占位）", ["placeholder"]),
    ("src/thesisos/writing/__init__.py", "写作模块（占位）", ["placeholder"]),
    ("src/thesisos/utils/__init__.py", "工具模块（占位）", ["placeholder"]),
    ("src/thesisos/workflow/__init__.py", "工作流模块（占位）", ["placeholder"]),
    ("src/thesisos/workflow/base.py", "工作流协议：WorkflowContext + StepResult + WorkflowStep", ["workflow", "protocol"]),
]
for fp, summary, tags in ph:
    nodes.append({"id": f"file:{fp}", "type": "file", "name": os.path.basename(fp), "filePath": fp, "summary": summary, "tags": tags, "complexity": "simple"})

# --- Root ---
root = [
    ("main.py", "启动入口：uvicorn + FastAPI 应用工厂", ["entry", "root"]),
]
for fp, summary, tags in root:
    nodes.append({"id": f"file:{fp}", "type": "file", "name": fp, "filePath": fp, "summary": summary, "tags": tags, "complexity": "simple"})

root_cfg = [
    ("pyproject.toml", "项目配置：hatchling 构建 + ruff + mypy + pytest", ["config", "root"]),
    (".env.example", "环境变量模板", ["config", "root"]),
    (".gitignore", "Git 忽略规则", ["config", "root"]),
]
for fp, summary, tags in root_cfg:
    nodes.append({"id": f"config:{fp}", "type": "config", "name": fp, "filePath": fp, "summary": summary, "tags": tags, "complexity": "simple"})

root_docs = [
    ("README.md", "项目说明文档", ["docs", "root"]),
    ("AGENTS.md", "AI 编码助手 10 条指导原则", ["docs", "root"]),
    ("CONTRIBUTING.md", "贡献指南（空）", ["docs", "root"]),
    ("LICENSE", "MIT 许可证", ["config", "root"]),
]
for fp, summary, tags in root_docs:
    nt = "document" if fp.endswith(".md") else "config"
    nodes.append({"id": f"{nt}:{fp}", "type": nt, "name": fp, "filePath": fp, "summary": summary, "tags": tags, "complexity": "simple"})

# --- Docs ---
docs = [
    ("doc/ARCHITECTURE.md", "架构文档（待编写）", ["docs"]),
    ("doc/ROADMAP.md", "6 阶段开发路线图（8-12 周）", ["docs", "roadmap"]),
    ("doc/TECH_STACK.md", "7 层技术栈详细说明", ["docs", "tech-stack"]),
    ("doc/WORKFLOW.md", "10 阶段论文生成工作流", ["docs", "workflow"]),
]
for fp, summary, tags in docs:
    nodes.append({"id": f"document:{fp}", "type": "document", "name": os.path.basename(fp), "filePath": fp, "summary": summary, "tags": tags, "complexity": "simple"})

# --- Tests ---
tests = [
    ("tests/conftest.py", "pytest 全局 fixtures（缓存清理 + 临时配置）", ["test", "fixtures"]),
    ("tests/unit/test_config.py", "配置模块测试", ["test", "unit", "config"]),
    ("tests/unit/test_llm.py", "LLM 模块测试（工厂 + 协议验证）", ["test", "unit", "llm"]),
    ("tests/unit/test_workflow.py", "工作流模块测试（Context + StepResult）", ["test", "unit", "workflow"]),
]
for fp, summary, tags in tests:
    nodes.append({"id": f"file:{fp}", "type": "file", "name": os.path.basename(fp), "filePath": fp, "summary": summary, "tags": tags, "complexity": "simple"})

graph["nodes"] = nodes

# ===== EDGES =====
edges = []

def e(src, tgt, etype, weight=0.7):
    edges.append({"source": f"file:{src}", "target": f"file:{tgt}", "type": etype, "weight": weight})

# Application → Domain ports
e("src/thesisos/application/literature/search_service.py", "src/thesisos/domain/ports/search_port.py", "imports")
e("src/thesisos/application/literature/search_service.py", "src/thesisos/domain/ports/repository_port.py", "imports")
e("src/thesisos/application/literature/search_service.py", "src/thesisos/domain/models/paper.py", "imports")
e("src/thesisos/application/literature/search_service.py", "src/thesisos/domain/models/search.py", "imports")
e("src/thesisos/application/literature/manage_service.py", "src/thesisos/domain/ports/repository_port.py", "imports")
e("src/thesisos/application/literature/manage_service.py", "src/thesisos/domain/ports/llm_port.py", "imports")
e("src/thesisos/application/writing/__init__.py", "src/thesisos/domain/ports/llm_port.py", "imports")
e("src/thesisos/application/writing/__init__.py", "src/thesisos/domain/ports/repository_port.py", "imports")
e("src/thesisos/application/analysis/__init__.py", "src/thesisos/domain/ports/llm_port.py", "imports")

# Infrastructure implements Domain ports
e("src/thesisos/infrastructure/llm/ollama_adapter.py", "src/thesisos/domain/ports/llm_port.py", "implements", 0.9)
e("src/thesisos/infrastructure/llm/openai_adapter.py", "src/thesisos/domain/ports/llm_port.py", "implements", 0.9)
e("src/thesisos/infrastructure/db/repositories.py", "src/thesisos/domain/ports/repository_port.py", "implements", 0.9)

# Infrastructure internal
e("src/thesisos/infrastructure/db/repositories.py", "src/thesisos/infrastructure/db/sqlite.py", "imports")
e("src/thesisos/infrastructure/llm/factory.py", "src/thesisos/infrastructure/llm/ollama_adapter.py", "imports")
e("src/thesisos/infrastructure/llm/factory.py", "src/thesisos/infrastructure/llm/openai_adapter.py", "imports")
e("src/thesisos/infrastructure/db/sqlite.py", "src/thesisos/config/settings.py", "imports")
e("src/thesisos/infrastructure/db/chroma.py", "src/thesisos/config/settings.py", "imports")
e("src/thesisos/infrastructure/llm/factory.py", "src/thesisos/config/settings.py", "imports")

# Presentation → Application + Infrastructure
e("src/thesisos/presentation/api/dependencies.py", "src/thesisos/application/literature/search_service.py", "imports")
e("src/thesisos/presentation/api/dependencies.py", "src/thesisos/application/literature/manage_service.py", "imports")
e("src/thesisos/presentation/api/dependencies.py", "src/thesisos/application/writing/__init__.py", "imports")
e("src/thesisos/presentation/api/dependencies.py", "src/thesisos/application/analysis/__init__.py", "imports")
e("src/thesisos/presentation/api/dependencies.py", "src/thesisos/infrastructure/llm/factory.py", "imports")
e("src/thesisos/presentation/api/dependencies.py", "src/thesisos/infrastructure/db/repositories.py", "imports")
e("src/thesisos/presentation/api/routes.py", "src/thesisos/presentation/api/dependencies.py", "imports")
e("src/thesisos/presentation/api/app.py", "src/thesisos/presentation/api/routes.py", "imports")
e("src/thesisos/presentation/ui/chainlit_app.py", "src/thesisos/presentation/api/dependencies.py", "imports")
e("src/thesisos/presentation/ui/nicegui_app.py", "src/thesisos/config/settings.py", "imports")

# Entry point
e("main.py", "src/thesisos/presentation/api/app.py", "imports")
e("main.py", "src/thesisos/config/settings.py", "imports")

# Compat → New
e("src/thesisos/api/__init__.py", "src/thesisos/presentation/api/app.py", "imports")
e("src/thesisos/llm/__init__.py", "src/thesisos/domain/ports/llm_port.py", "imports")
e("src/thesisos/llm/__init__.py", "src/thesisos/infrastructure/llm/factory.py", "imports")
e("src/thesisos/db/__init__.py", "src/thesisos/infrastructure/db/sqlite.py", "imports")
e("src/thesisos/db/__init__.py", "src/thesisos/infrastructure/db/chroma.py", "imports")
e("src/thesisos/models/__init__.py", "src/thesisos/domain/models/paper.py", "imports")
e("src/thesisos/models/__init__.py", "src/thesisos/domain/models/project.py", "imports")
e("src/thesisos/models/__init__.py", "src/thesisos/infrastructure/db/sqlite.py", "imports")
e("src/thesisos/embedding/__init__.py", "src/thesisos/domain/ports/embedding_port.py", "imports")

# Tests → source (tested_by)
e("tests/unit/test_llm.py", "src/thesisos/infrastructure/llm/factory.py", "tested_by", 0.5)
e("tests/unit/test_llm.py", "src/thesisos/domain/ports/llm_port.py", "tested_by", 0.5)
e("tests/unit/test_config.py", "src/thesisos/config/settings.py", "tested_by", 0.5)
e("tests/unit/test_workflow.py", "src/thesisos/workflow/base.py", "tested_by", 0.5)
e("tests/conftest.py", "src/thesisos/config/settings.py", "imports")

# Docs → code
edges.append({"source": "document:doc/ROADMAP.md", "target": "file:src/thesisos/infrastructure/db/sqlite.py", "type": "documents", "weight": 0.5})
edges.append({"source": "document:doc/TECH_STACK.md", "target": "file:src/thesisos/infrastructure/llm/ollama_adapter.py", "type": "documents", "weight": 0.5})
edges.append({"source": "document:doc/WORKFLOW.md", "target": "file:src/thesisos/application/writing/__init__.py", "type": "documents", "weight": 0.5})

graph["edges"] = edges

# ===== LAYERS =====
def ids_in(prefix):
    return [n["id"] for n in nodes if n.get("filePath", "").startswith(prefix)]

graph["layers"] = [
    {
        "id": "layer:domain",
        "name": "领域层 (Domain)",
        "description": "最内层，零外部依赖。领域实体（Paper/Project/SearchQuery）、端口接口（LLMProvider/Repository/SearchProvider）、领域异常。Clean Architecture 核心，不依赖任何框架。",
        "nodeIds": ids_in("src/thesisos/domain/"),
    },
    {
        "id": "layer:application",
        "name": "应用层 (Application)",
        "description": "用例/服务编排层。LiteratureSearchService、LiteratureManageService、AnalysisService、WritingService。只依赖领域端口（DIP），不依赖基础设施实现。",
        "nodeIds": ids_in("src/thesisos/application/"),
    },
    {
        "id": "layer:infrastructure",
        "name": "基础设施层 (Infrastructure)",
        "description": "端口适配器实现。OllamaAdapter/OpenAIAdapter 实现 LLMProvider、SQLitePaperRepository 实现 PaperRepository、ChromaDB 客户端、LLMFactory。依赖外部框架（httpx/SQLAlchemy/chromadb）。",
        "nodeIds": ids_in("src/thesisos/infrastructure/"),
    },
    {
        "id": "layer:presentation",
        "name": "接口层 (Presentation)",
        "description": "FastAPI REST API（app/routes/dependencies）+ Chainlit 对话界面 + NiceGUI 管理面板。依赖注入容器（Services）组装所有用例服务。",
        "nodeIds": ids_in("src/thesisos/presentation/"),
    },
    {
        "id": "layer:config-core",
        "name": "配置与核心 (Config & Core)",
        "description": "Pydantic Settings 全局配置管理（.env 加载，单例模式）+ 结构化日志 + 异常兼容层。",
        "nodeIds": ids_in("src/thesisos/config/") + ids_in("src/thesisos/core/"),
    },
    {
        "id": "layer:compat",
        "name": "兼容层 (Compat)",
        "description": "向后兼容的旧模块路径，全部重导出到新架构对应模块。保证渐进迁移不破坏现有引用。",
        "nodeIds": [n["id"] for n in nodes if "compat" in n.get("tags", [])],
    },
    {
        "id": "layer:tests",
        "name": "测试层 (Tests)",
        "description": "pytest 单元测试 + 集成测试（占位）。覆盖 config/llm/workflow 模块。",
        "nodeIds": ids_in("tests/"),
    },
]

# ===== TOUR =====
graph["tour"] = [
    {
        "order": 1,
        "title": "项目概览",
        "description": "从 README 和 AGENTS.md 了解项目定位、技术栈和 10 条编码规范。",
        "nodeIds": ["document:README.md", "document:AGENTS.md"],
    },
    {
        "order": 2,
        "title": "领域层 — 核心实体与端口",
        "description": "Clean Architecture 最内层：Paper/Project 领域实体、LLMProvider/Repository 端口协议、13 种领域异常层级。零外部依赖。",
        "nodeIds": [
            "file:src/thesisos/domain/models/paper.py",
            "file:src/thesisos/domain/models/project.py",
            "file:src/thesisos/domain/ports/llm_port.py",
            "file:src/thesisos/domain/ports/repository_port.py",
            "file:src/thesisos/domain/exceptions.py",
        ],
    },
    {
        "order": 3,
        "title": "应用层 — 用例编排",
        "description": "LiteratureSearchService 编排多源检索→去重→入库流程；WritingService 处理大纲生成和章节撰写。只依赖领域端口（DIP）。",
        "nodeIds": [
            "file:src/thesisos/application/literature/search_service.py",
            "file:src/thesisos/application/literature/manage_service.py",
            "file:src/thesisos/application/writing/__init__.py",
        ],
    },
    {
        "order": 4,
        "title": "基础设施层 — 适配器实现",
        "description": "OllamaAdapter/OpenAIAdapter 实现 LLMProvider 端口；SQLitePaperRepository 实现 PaperRepository 端口；LLMFactory 按配置创建对应适配器。",
        "nodeIds": [
            "file:src/thesisos/infrastructure/llm/ollama_adapter.py",
            "file:src/thesisos/infrastructure/llm/openai_adapter.py",
            "file:src/thesisos/infrastructure/llm/factory.py",
            "file:src/thesisos/infrastructure/db/repositories.py",
        ],
    },
    {
        "order": 5,
        "title": "接口层 — API 与依赖注入",
        "description": "FastAPI 应用工厂 + CORS + 异常处理；RESTful 路由（/health, /papers, /writing, /analysis）；Services 依赖注入容器组装所有用例。",
        "nodeIds": [
            "file:src/thesisos/presentation/api/app.py",
            "file:src/thesisos/presentation/api/routes.py",
            "file:src/thesisos/presentation/api/dependencies.py",
        ],
    },
    {
        "order": 6,
        "title": "配置与启动",
        "description": "Pydantic Settings 从 .env 加载配置，支持 Ollama/OpenAI 切换；main.py 启动 uvicorn；SQLite + ChromaDB 双数据库。",
        "nodeIds": ["file:src/thesisos/config/settings.py", "file:main.py", "config:pyproject.toml"],
    },
    {
        "order": 7,
        "title": "测试覆盖",
        "description": "pytest 单元测试覆盖 config/llm/workflow 模块。conftest.py 提供 fixtures 和缓存清理。ruff + mypy 零错误。",
        "nodeIds": [
            "file:tests/conftest.py",
            "file:tests/unit/test_llm.py",
            "file:tests/unit/test_config.py",
            "file:tests/unit/test_workflow.py",
        ],
    },
]

# Save
out_path = os.path.join(UA_DIR, "intermediate", "assembled-graph.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(graph, f, ensure_ascii=False, indent=2)

final_path = os.path.join(UA_DIR, "knowledge-graph.json")
with open(final_path, "w", encoding="utf-8") as f:
    json.dump(graph, f, ensure_ascii=False, indent=2)

meta = {
    "lastAnalyzedAt": datetime.now().isoformat(),
    "gitCommitHash": "4d8244d2d429ff1508064f05db1c667674945ef8",
    "version": "1.0.0",
    "analyzedFiles": len(nodes),
}
with open(os.path.join(UA_DIR, "meta.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)

print(f"OK: {len(nodes)} nodes, {len(edges)} edges, {len(graph['layers'])} layers, {len(graph['tour'])} tour steps")
print(f"Saved to: {final_path}")
