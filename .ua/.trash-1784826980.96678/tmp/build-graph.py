#!/usr/bin/env python3
"""生成 Thesis Studio 知识图谱 JSON。"""

import json
from datetime import datetime, timezone
from pathlib import Path

UA_DIR = Path(r"E:\AutoResearch\Thesis Studio\.ua")
INTER = UA_DIR / "intermediate"

# ── 节点 ──────────────────────────────────────────────
nodes: list[dict] = []


def add(node_id: str, ntype: str, name: str, path: str, summary: str, tags: list[str], complexity: str | None = None):
    n = {"id": node_id, "type": ntype, "name": name, "filePath": path, "summary": summary, "tags": tags}
    if complexity:
        n["complexity"] = complexity
    nodes.append(n)


# ── 文件节点 (code) ───────────────────────────────────
add("file:main.py", "file", "main.py", "main.py",
    "项目入口：创建 FastAPI 应用并启动 Uvicorn 服务", ["entry-point", "fastapi", "uvicorn"])
add("file:src/thesis_studio/__init__.py", "file", "__init__.py", "src/thesis_studio/__init__.py",
    "Thesis Studio 包初始化，定义版本号", ["package-init"])
add("file:src/thesis_studio/api/__init__.py", "file", "api/__init__.py", "src/thesis_studio/api/__init__.py",
    "API 包入口，导出 create_app", ["package-init", "api"])
add("file:src/thesis_studio/api/app.py", "file", "app.py", "src/thesis_studio/api/app.py",
    "FastAPI 应用工厂：健康检查端点与全局异常处理", ["fastapi", "factory", "api"], "low")
add("file:src/thesis_studio/config/__init__.py", "file", "config/__init__.py", "src/thesis_studio/config/__init__.py",
    "配置包入口，导出 Settings 和 get_settings", ["package-init", "config"])
add("file:src/thesis_studio/config/settings.py", "file", "settings.py", "src/thesis_studio/config/settings.py",
    "全局配置：Pydantic Settings，从 .env 加载，环境变量前缀 THESISOS_", ["pydantic", "config", "settings"], "low")
add("file:src/thesis_studio/core/__init__.py", "file", "core/__init__.py", "src/thesis_studio/core/__init__.py",
    "核心抽象层包初始化", ["package-init", "core"])
add("file:src/thesis_studio/core/exceptions.py", "file", "exceptions.py", "src/thesis_studio/core/exceptions.py",
    "领域异常层级：所有业务异常继承 Thesis StudioError", ["exceptions", "error-handling"], "low")
add("file:src/thesis_studio/core/logging.py", "file", "logging.py", "src/thesis_studio/core/logging.py",
    "结构化日志配置，输出到 stderr", ["logging", "core"], "low")
add("file:src/thesis_studio/db/__init__.py", "file", "db/__init__.py", "src/thesis_studio/db/__init__.py",
    "数据库包入口，导出 SQLite 引擎与 ChromaDB 客户端", ["package-init", "database"])
add("file:src/thesis_studio/db/chroma.py", "file", "chroma.py", "src/thesis_studio/db/chroma.py",
    "ChromaDB 向量数据库客户端单例（线程安全）", ["chromadb", "vector-db", "singleton"], "low")
add("file:src/thesis_studio/db/sqlite.py", "file", "sqlite.py", "src/thesis_studio/db/sqlite.py",
    "SQLite 异步引擎与会话管理，基于 SQLAlchemy async", ["sqlite", "sqlalchemy", "async"], "low")
add("file:src/thesis_studio/embedding/__init__.py", "file", "embedding/__init__.py", "src/thesis_studio/embedding/__init__.py",
    "嵌入模型包入口，导出 EmbeddingProvider", ["package-init", "embedding"])
add("file:src/thesis_studio/embedding/base.py", "file", "base.py", "src/thesis_studio/embedding/base.py",
    "嵌入模型统一接口 Protocol，定义 embed 和 embed_batch", ["protocol", "embedding", "interface"], "low")
add("file:src/thesis_studio/literature/__init__.py", "file", "literature/__init__.py", "src/thesis_studio/literature/__init__.py",
    "文献检索与管理模块（占位）", ["placeholder", "literature"])
add("file:src/thesis_studio/llm/__init__.py", "file", "llm/__init__.py", "src/thesis_studio/llm/__init__.py",
    "LLM 包入口，导出 LLMProvider 和 create_llm", ["package-init", "llm"])
add("file:src/thesis_studio/llm/base.py", "file", "base.py", "src/thesis_studio/llm/base.py",
    "LLM 提供商统一接口 Protocol，定义 generate 方法", ["protocol", "llm", "interface"], "low")
add("file:src/thesis_studio/llm/factory.py", "file", "factory.py", "src/thesis_studio/llm/factory.py",
    "LLM 工厂：根据配置创建 Ollama 或 OpenAI 提供商实例", ["factory", "llm", "config-driven"], "low")
add("file:src/thesis_studio/llm/ollama.py", "file", "ollama.py", "src/thesis_studio/llm/ollama.py",
    "Ollama 本地模型提供商，通过 httpx 调用 Ollama API", ["ollama", "llm", "httpx"], "low")
add("file:src/thesis_studio/llm/openai.py", "file", "openai.py", "src/thesis_studio/llm/openai.py",
    "OpenAI 云端模型提供商，通过 httpx 调用 Chat Completions API", ["openai", "llm", "httpx"], "low")
add("file:src/thesis_studio/models/__init__.py", "file", "models/__init__.py", "src/thesis_studio/models/__init__.py",
    "领域模型包入口，导出 ORM 基类 Base", ["package-init", "models"])
add("file:src/thesis_studio/models/base.py", "file", "base.py", "src/thesis_studio/models/base.py",
    "SQLAlchemy ORM 基类 DeclarativeBase", ["sqlalchemy", "orm", "base"], "low")
add("file:src/thesis_studio/ui/__init__.py", "file", "ui/__init__.py", "src/thesis_studio/ui/__init__.py",
    "用户界面包：Chainlit 对话 + NiceGUI 管理面板", ["package-init", "ui"])
add("file:src/thesis_studio/ui/chainlit_app.py", "file", "chainlit_app.py", "src/thesis_studio/ui/chainlit_app.py",
    "Chainlit 对话交互界面，处理用户消息并调用 LLM 生成回复", ["chainlit", "chat-ui", "llm"], "low")
add("file:src/thesis_studio/ui/nicegui_app.py", "file", "nicegui_app.py", "src/thesis_studio/ui/nicegui_app.py",
    "NiceGUI 管理面板：文献库、项目进度、数据分析、设置", ["nicegui", "admin-ui"], "low")
add("file:src/thesis_studio/workflow/__init__.py", "file", "workflow/__init__.py", "src/thesis_studio/workflow/__init__.py",
    "工作流包入口，导出 WorkflowStep、WorkflowContext、StepResult", ["package-init", "workflow"])
add("file:src/thesis_studio/workflow/base.py", "file", "base.py", "src/thesis_studio/workflow/base.py",
    "工作流阶段接口与上下文：WorkflowContext 传递数据，StepResult 记录结果", ["workflow", "protocol", "dataclass"], "low")
add("file:src/thesis_studio/utils/__init__.py", "file", "utils/__init__.py", "src/thesis_studio/utils/__init__.py",
    "通用工具函数模块（占位）", ["placeholder", "utils"])
add("file:src/thesis_studio/writing/__init__.py", "file", "writing/__init__.py", "src/thesis_studio/writing/__init__.py",
    "论文撰写与文档生成模块（占位）", ["placeholder", "writing"])
add("file:src/thesis_studio/analysis/__init__.py", "file", "analysis/__init__.py", "src/thesis_studio/analysis/__init__.py",
    "数据分析与可视化模块（占位）", ["placeholder", "analysis"])

# ── 测试文件 ──────────────────────────────────────────
add("file:tests/conftest.py", "file", "conftest.py", "tests/conftest.py",
    "pytest 全局 fixtures：清除配置缓存、临时测试配置", ["test", "fixture", "config"])
add("file:tests/unit/test_config.py", "file", "test_config.py", "tests/unit/test_config.py",
    "配置模块测试：默认配置应使用 Ollama", ["test", "config"])
add("file:tests/unit/test_llm.py", "file", "test_llm.py", "tests/unit/test_llm.py",
    "LLM 模块测试：工厂创建 OllamaProvider、协议满足性", ["test", "llm", "factory"])
add("file:tests/unit/test_workflow.py", "file", "test_workflow.py", "tests/unit/test_workflow.py",
    "工作流模块测试：WorkflowContext 默认数据、StepResult 字段", ["test", "workflow"])
add("file:tests/__init__.py", "file", "tests/__init__.py", "tests/__init__.py", "测试包初始化", ["test"])
add("file:tests/unit/__init__.py", "file", "tests/unit/__init__.py", "tests/unit/__init__.py", "单元测试包初始化", ["test"])
add("file:tests/integration/__init__.py", "file", "tests/integration/__init__.py", "tests/integration/__init__.py", "集成测试包初始化", ["test"])

# ── 配置文件 ──────────────────────────────────────────
add("config:pyproject.toml", "config", "pyproject.toml", "pyproject.toml",
    "项目配置：Python 3.11+，hatchling 构建，ruff/mypy/pytest 工具链", ["config", "build", "linting"])
add("config:.env.example", "config", ".env.example", ".env.example",
    "环境变量示例：LLM、数据库、服务、文献检索配置", ["config", "env", "example"])

# ── 文档文件 ──────────────────────────────────────────
add("document:README.md", "document", "README.md", "README.md",
    "项目说明：面向毕业论文生成的 AI 研究助手", ["readme", "overview"])
add("document:AGENTS.md", "document", "AGENTS.md", "AGENTS.md",
    "AI 代码规范总纲：Adaptive、Brief、Logic 等十条原则，conda 环境约束", ["guidelines", "ai", "coding-standards"])
add("document:CONTRIBUTING.md", "document", "CONTRIBUTING.md", "CONTRIBUTING.md",
    "贡献指南（待编写）", ["contributing", "empty"])
add("document:doc/TECH_STACK.md", "document", "TECH_STACK.md", "doc/TECH_STACK.md",
    "技术栈选型表：FastAPI、Chainlit、NiceGUI、SQLite、ChromaDB、Ollama 等", ["doc", "tech-stack"])
add("document:doc/WORKFLOW.md", "document", "WORKFLOW.md", "doc/WORKFLOW.md",
    "十阶段工作流设计：选题→文献→问题→方法→数据→分析→框架→撰写→修改→答辩", ["doc", "workflow", "design"])
add("document:doc/ROADMAP.md", "document", "ROADMAP.md", "doc/ROADMAP.md",
    "开发路线图：六阶段计划（基础框架→文献管理→AI写作→数据分析→文档输出→完善发布）", ["doc", "roadmap"])
add("document:doc/ARCHITECTURE.md", "document", "ARCHITECTURE.md", "doc/ARCHITECTURE.md",
    "系统架构文档（待编写）", ["doc", "architecture", "empty"])

# ── 函数/类节点 ───────────────────────────────────────
add("function:src/thesis_studio/api/app.py:create_app", "function", "create_app", "src/thesis_studio/api/app.py",
    "创建并配置 FastAPI 应用实例，注册健康检查和异常处理", ["factory", "fastapi"])
add("class:src/thesis_studio/config/settings.py:Settings", "class", "Settings", "src/thesis_studio/config/settings.py",
    "全局配置类，从 .env 加载，包含 LLM、数据库、服务、文献检索配置", ["pydantic", "settings", "config"])
add("function:src/thesis_studio/config/settings.py:get_settings", "function", "get_settings", "src/thesis_studio/config/settings.py",
    "获取全局配置单例（lru_cache 缓存）", ["singleton", "config", "lru-cache"])
add("class:src/thesis_studio/core/exceptions.py:Thesis StudioError", "class", "Thesis StudioError", "src/thesis_studio/core/exceptions.py",
    "所有 Thesis Studio 领域异常的基类", ["exception", "base"])
add("class:src/thesis_studio/core/exceptions.py:ConfigError", "class", "ConfigError", "src/thesis_studio/core/exceptions.py",
    "配置相关错误", ["exception", "config"])
add("class:src/thesis_studio/core/exceptions.py:LLMError", "class", "LLMError", "src/thesis_studio/core/exceptions.py",
    "LLM 调用相关错误", ["exception", "llm"])
add("class:src/thesis_studio/core/exceptions.py:LLMUnavailableError", "class", "LLMUnavailableError", "src/thesis_studio/core/exceptions.py",
    "LLM 服务不可用（如 Ollama 未启动）", ["exception", "llm", "unavailable"])
add("class:src/thesis_studio/core/exceptions.py:DatabaseError", "class", "DatabaseError", "src/thesis_studio/core/exceptions.py",
    "数据库操作相关错误", ["exception", "database"])
add("class:src/thesis_studio/core/exceptions.py:WorkflowError", "class", "WorkflowError", "src/thesis_studio/core/exceptions.py",
    "工作流执行相关错误", ["exception", "workflow"])
add("function:src/thesis_studio/core/logging.py:setup_logging", "function", "setup_logging", "src/thesis_studio/core/logging.py",
    "配置全局日志，输出到 stderr", ["logging", "setup"])
add("function:src/thesis_studio/core/logging.py:get_logger", "function", "get_logger", "src/thesis_studio/core/logging.py",
    "获取模块日志器", ["logging", "logger"])
add("function:src/thesis_studio/db/chroma.py:get_chroma_client", "function", "get_chroma_client", "src/thesis_studio/db/chroma.py",
    "获取 ChromaDB 客户端单例（线程安全双重检查锁）", ["chromadb", "singleton", "thread-safe"])
add("function:src/thesis_studio/db/sqlite.py:get_engine", "function", "get_engine", "src/thesis_studio/db/sqlite.py",
    "获取全局异步 SQLite 引擎单例", ["sqlite", "sqlalchemy", "singleton", "async"])
add("function:src/thesis_studio/db/sqlite.py:get_session_factory", "function", "get_session_factory", "src/thesis_studio/db/sqlite.py",
    "获取异步会话工厂", ["sqlalchemy", "session", "factory"])
add("function:src/thesis_studio/db/sqlite.py:get_session", "function", "get_session", "src/thesis_studio/db/sqlite.py",
    "FastAPI 依赖：获取数据库会话（异步生成器）", ["fastapi", "dependency", "session", "async"])
add("class:src/thesis_studio/embedding/base.py:EmbeddingProvider", "class", "EmbeddingProvider", "src/thesis_studio/embedding/base.py",
    "嵌入模型接口 Protocol，定义 embed 和 embed_batch 方法", ["protocol", "embedding", "interface"])
add("class:src/thesis_studio/llm/base.py:LLMProvider", "class", "LLMProvider", "src/thesis_studio/llm/base.py",
    "LLM 提供商接口 Protocol，定义 generate 方法", ["protocol", "llm", "interface"])
add("function:src/thesis_studio/llm/factory.py:create_llm", "function", "create_llm", "src/thesis_studio/llm/factory.py",
    "根据配置创建 LLM 提供商实例（Ollama 或 OpenAI）", ["factory", "llm", "config-driven"])
add("class:src/thesis_studio/llm/ollama.py:OllamaProvider", "class", "OllamaProvider", "src/thesis_studio/llm/ollama.py",
    "Ollama 本地模型提供商实现，通过 httpx 调用 Ollama API", ["ollama", "llm", "httpx", "provider"])
add("class:src/thesis_studio/llm/openai.py:OpenAIProvider", "class", "OpenAIProvider", "src/thesis_studio/llm/openai.py",
    "OpenAI 云端模型提供商实现，通过 httpx 调用 Chat Completions API", ["openai", "llm", "httpx", "provider"])
add("class:src/thesis_studio/models/base.py:Base", "class", "Base", "src/thesis_studio/models/base.py",
    "SQLAlchemy ORM 基类 DeclarativeBase", ["sqlalchemy", "orm", "base"])
add("function:src/thesis_studio/ui/chainlit_app.py:on_chat_start", "function", "on_chat_start", "src/thesis_studio/ui/chainlit_app.py",
    "Chainlit 对话初始化回调", ["chainlit", "callback"])
add("function:src/thesis_studio/ui/chainlit_app.py:on_message", "function", "on_message", "src/thesis_studio/ui/chainlit_app.py",
    "处理用户消息，调用 LLM 生成回复", ["chainlit", "callback", "llm"])
add("function:src/thesis_studio/ui/nicegui_app.py:build_ui", "function", "build_ui", "src/thesis_studio/ui/nicegui_app.py",
    "构建 NiceGUI 管理面板界面", ["nicegui", "ui"])
add("function:src/thesis_studio/ui/nicegui_app.py:main", "function", "main", "src/thesis_studio/ui/nicegui_app.py",
    "启动 NiceGUI 管理面板", ["nicegui", "entry"])
add("class:src/thesis_studio/workflow/base.py:WorkflowContext", "class", "WorkflowContext", "src/thesis_studio/workflow/base.py",
    "工作流上下文，在阶段间传递数据", ["dataclass", "workflow", "context"])
add("class:src/thesis_studio/workflow/base.py:StepResult", "class", "StepResult", "src/thesis_studio/workflow/base.py",
    "单个工作流阶段的执行结果", ["dataclass", "workflow", "result"])
add("class:src/thesis_studio/workflow/base.py:WorkflowStep", "class", "WorkflowStep", "src/thesis_studio/workflow/base.py",
    "工作流阶段接口 Protocol，定义 execute 方法", ["protocol", "workflow", "interface"])

# ── 边 ────────────────────────────────────────────────
edges: list[dict] = []


def edge(src: str, tgt: str, etype: str, weight: float | None = None):
    e = {"source": src, "target": tgt, "type": etype}
    if weight is not None:
        e["weight"] = weight
    edges.append(e)


# imports
edge("file:main.py", "file:src/thesis_studio/api/app.py", "imports", 0.7)
edge("file:main.py", "file:src/thesis_studio/config/settings.py", "imports", 0.7)
edge("file:src/thesis_studio/api/app.py", "file:src/thesis_studio/core/exceptions.py", "imports", 0.7)
edge("file:src/thesis_studio/api/__init__.py", "file:src/thesis_studio/api/app.py", "imports", 0.7)
edge("file:src/thesis_studio/config/__init__.py", "file:src/thesis_studio/config/settings.py", "imports", 0.7)
edge("file:src/thesis_studio/db/__init__.py", "file:src/thesis_studio/db/chroma.py", "imports", 0.7)
edge("file:src/thesis_studio/db/__init__.py", "file:src/thesis_studio/db/sqlite.py", "imports", 0.7)
edge("file:src/thesis_studio/db/chroma.py", "file:src/thesis_studio/config/settings.py", "imports", 0.7)
edge("file:src/thesis_studio/db/chroma.py", "file:src/thesis_studio/core/logging.py", "imports", 0.7)
edge("file:src/thesis_studio/db/sqlite.py", "file:src/thesis_studio/config/settings.py", "imports", 0.7)
edge("file:src/thesis_studio/db/sqlite.py", "file:src/thesis_studio/core/logging.py", "imports", 0.7)
edge("file:src/thesis_studio/embedding/__init__.py", "file:src/thesis_studio/embedding/base.py", "imports", 0.7)
edge("file:src/thesis_studio/llm/__init__.py", "file:src/thesis_studio/llm/base.py", "imports", 0.7)
edge("file:src/thesis_studio/llm/__init__.py", "file:src/thesis_studio/llm/factory.py", "imports", 0.7)
edge("file:src/thesis_studio/llm/factory.py", "file:src/thesis_studio/config/settings.py", "imports", 0.7)
edge("file:src/thesis_studio/llm/factory.py", "file:src/thesis_studio/core/exceptions.py", "imports", 0.7)
edge("file:src/thesis_studio/llm/factory.py", "file:src/thesis_studio/llm/base.py", "imports", 0.7)
edge("file:src/thesis_studio/llm/factory.py", "file:src/thesis_studio/llm/ollama.py", "imports", 0.7)
edge("file:src/thesis_studio/llm/factory.py", "file:src/thesis_studio/llm/openai.py", "imports", 0.7)
edge("file:src/thesis_studio/llm/ollama.py", "file:src/thesis_studio/core/exceptions.py", "imports", 0.7)
edge("file:src/thesis_studio/llm/ollama.py", "file:src/thesis_studio/core/logging.py", "imports", 0.7)
edge("file:src/thesis_studio/llm/openai.py", "file:src/thesis_studio/core/logging.py", "imports", 0.7)
edge("file:src/thesis_studio/models/__init__.py", "file:src/thesis_studio/models/base.py", "imports", 0.7)
edge("file:src/thesis_studio/ui/chainlit_app.py", "file:src/thesis_studio/llm/factory.py", "imports", 0.7)
edge("file:src/thesis_studio/ui/nicegui_app.py", "file:src/thesis_studio/config/settings.py", "imports", 0.7)
edge("file:src/thesis_studio/workflow/__init__.py", "file:src/thesis_studio/workflow/base.py", "imports", 0.7)

# contains (file -> function/class)
edge("file:src/thesis_studio/api/app.py", "function:src/thesis_studio/api/app.py:create_app", "contains", 1.0)
edge("file:src/thesis_studio/config/settings.py", "class:src/thesis_studio/config/settings.py:Settings", "contains", 1.0)
edge("file:src/thesis_studio/config/settings.py", "function:src/thesis_studio/config/settings.py:get_settings", "contains", 1.0)
edge("file:src/thesis_studio/core/exceptions.py", "class:src/thesis_studio/core/exceptions.py:Thesis StudioError", "contains", 1.0)
edge("file:src/thesis_studio/core/exceptions.py", "class:src/thesis_studio/core/exceptions.py:ConfigError", "contains", 1.0)
edge("file:src/thesis_studio/core/exceptions.py", "class:src/thesis_studio/core/exceptions.py:LLMError", "contains", 1.0)
edge("file:src/thesis_studio/core/exceptions.py", "class:src/thesis_studio/core/exceptions.py:LLMUnavailableError", "contains", 1.0)
edge("file:src/thesis_studio/core/exceptions.py", "class:src/thesis_studio/core/exceptions.py:DatabaseError", "contains", 1.0)
edge("file:src/thesis_studio/core/exceptions.py", "class:src/thesis_studio/core/exceptions.py:WorkflowError", "contains", 1.0)
edge("file:src/thesis_studio/core/logging.py", "function:src/thesis_studio/core/logging.py:setup_logging", "contains", 1.0)
edge("file:src/thesis_studio/core/logging.py", "function:src/thesis_studio/core/logging.py:get_logger", "contains", 1.0)
edge("file:src/thesis_studio/db/chroma.py", "function:src/thesis_studio/db/chroma.py:get_chroma_client", "contains", 1.0)
edge("file:src/thesis_studio/db/sqlite.py", "function:src/thesis_studio/db/sqlite.py:get_engine", "contains", 1.0)
edge("file:src/thesis_studio/db/sqlite.py", "function:src/thesis_studio/db/sqlite.py:get_session_factory", "contains", 1.0)
edge("file:src/thesis_studio/db/sqlite.py", "function:src/thesis_studio/db/sqlite.py:get_session", "contains", 1.0)
edge("file:src/thesis_studio/embedding/base.py", "class:src/thesis_studio/embedding/base.py:EmbeddingProvider", "contains", 1.0)
edge("file:src/thesis_studio/llm/base.py", "class:src/thesis_studio/llm/base.py:LLMProvider", "contains", 1.0)
edge("file:src/thesis_studio/llm/factory.py", "function:src/thesis_studio/llm/factory.py:create_llm", "contains", 1.0)
edge("file:src/thesis_studio/llm/ollama.py", "class:src/thesis_studio/llm/ollama.py:OllamaProvider", "contains", 1.0)
edge("file:src/thesis_studio/llm/openai.py", "class:src/thesis_studio/llm/openai.py:OpenAIProvider", "contains", 1.0)
edge("file:src/thesis_studio/models/base.py", "class:src/thesis_studio/models/base.py:Base", "contains", 1.0)
edge("file:src/thesis_studio/ui/chainlit_app.py", "function:src/thesis_studio/ui/chainlit_app.py:on_chat_start", "contains", 1.0)
edge("file:src/thesis_studio/ui/chainlit_app.py", "function:src/thesis_studio/ui/chainlit_app.py:on_message", "contains", 1.0)
edge("file:src/thesis_studio/ui/nicegui_app.py", "function:src/thesis_studio/ui/nicegui_app.py:build_ui", "contains", 1.0)
edge("file:src/thesis_studio/ui/nicegui_app.py", "function:src/thesis_studio/ui/nicegui_app.py:main", "contains", 1.0)
edge("file:src/thesis_studio/workflow/base.py", "class:src/thesis_studio/workflow/base.py:WorkflowContext", "contains", 1.0)
edge("file:src/thesis_studio/workflow/base.py", "class:src/thesis_studio/workflow/base.py:StepResult", "contains", 1.0)
edge("file:src/thesis_studio/workflow/base.py", "class:src/thesis_studio/workflow/base.py:WorkflowStep", "contains", 1.0)

# calls
edge("file:main.py", "function:src/thesis_studio/api/app.py:create_app", "calls", 0.8)
edge("file:main.py", "function:src/thesis_studio/config/settings.py:get_settings", "calls", 0.8)
edge("function:src/thesis_studio/ui/chainlit_app.py:on_message", "function:src/thesis_studio/llm/factory.py:create_llm", "calls", 0.8)
edge("function:src/thesis_studio/llm/factory.py:create_llm", "class:src/thesis_studio/llm/ollama.py:OllamaProvider", "calls", 0.8)
edge("function:src/thesis_studio/llm/factory.py:create_llm", "class:src/thesis_studio/llm/openai.py:OpenAIProvider", "calls", 0.8)
edge("function:src/thesis_studio/db/chroma.py:get_chroma_client", "function:src/thesis_studio/config/settings.py:get_settings", "calls", 0.8)
edge("function:src/thesis_studio/db/sqlite.py:get_engine", "function:src/thesis_studio/config/settings.py:get_settings", "calls", 0.8)
edge("function:src/thesis_studio/ui/nicegui_app.py:main", "function:src/thesis_studio/config/settings.py:get_settings", "calls", 0.8)

# inherits
edge("class:src/thesis_studio/core/exceptions.py:ConfigError", "class:src/thesis_studio/core/exceptions.py:Thesis StudioError", "inherits", 0.9)
edge("class:src/thesis_studio/core/exceptions.py:LLMError", "class:src/thesis_studio/core/exceptions.py:Thesis StudioError", "inherits", 0.9)
edge("class:src/thesis_studio/core/exceptions.py:LLMUnavailableError", "class:src/thesis_studio/core/exceptions.py:LLMError", "inherits", 0.9)
edge("class:src/thesis_studio/core/exceptions.py:DatabaseError", "class:src/thesis_studio/core/exceptions.py:Thesis StudioError", "inherits", 0.9)
edge("class:src/thesis_studio/core/exceptions.py:WorkflowError", "class:src/thesis_studio/core/exceptions.py:Thesis StudioError", "inherits", 0.9)

# implements (structural conformance to Protocol)
edge("class:src/thesis_studio/llm/ollama.py:OllamaProvider", "class:src/thesis_studio/llm/base.py:LLMProvider", "implements", 0.9)
edge("class:src/thesis_studio/llm/openai.py:OpenAIProvider", "class:src/thesis_studio/llm/base.py:LLMProvider", "implements", 0.9)

# configures
edge("config:.env.example", "file:src/thesis_studio/config/settings.py", "configures", 0.6)
edge("config:pyproject.toml", "file:src/thesis_studio/__init__.py", "configures", 0.6)

# documents
edge("document:README.md", "file:main.py", "documents", 0.5)
edge("document:AGENTS.md", "file:src/thesis_studio/__init__.py", "documents", 0.5)
edge("document:doc/TECH_STACK.md", "config:pyproject.toml", "documents", 0.5)
edge("document:doc/WORKFLOW.md", "file:src/thesis_studio/workflow/base.py", "documents", 0.5)
edge("document:doc/ROADMAP.md", "file:src/thesis_studio/__init__.py", "documents", 0.5)

# tested_by
edge("file:tests/unit/test_config.py", "file:src/thesis_studio/config/settings.py", "tested_by", 0.5)
edge("file:tests/unit/test_llm.py", "file:src/thesis_studio/llm/factory.py", "tested_by", 0.5)
edge("file:tests/unit/test_llm.py", "file:src/thesis_studio/llm/ollama.py", "tested_by", 0.5)
edge("file:tests/unit/test_workflow.py", "file:src/thesis_studio/workflow/base.py", "tested_by", 0.5)
edge("file:tests/conftest.py", "file:src/thesis_studio/config/settings.py", "tested_by", 0.5)

# ── 层 ────────────────────────────────────────────────
layers = [
    {"id": "layer:entry-point", "name": "入口层", "description": "项目启动入口，创建应用并启动服务",
     "nodeIds": ["file:main.py"]},
    {"id": "layer:api", "name": "API 层", "description": "FastAPI 应用工厂、路由与异常处理",
     "nodeIds": ["file:src/thesis_studio/api/__init__.py", "file:src/thesis_studio/api/app.py"]},
    {"id": "layer:config", "name": "配置层", "description": "全局配置管理，从 .env 加载，环境变量前缀 THESISOS_",
     "nodeIds": ["file:src/thesis_studio/config/__init__.py", "file:src/thesis_studio/config/settings.py", "config:.env.example", "config:pyproject.toml"]},
    {"id": "layer:core", "name": "核心层", "description": "领域异常层级与结构化日志",
     "nodeIds": ["file:src/thesis_studio/core/__init__.py", "file:src/thesis_studio/core/exceptions.py", "file:src/thesis_studio/core/logging.py"]},
    {"id": "layer:database", "name": "数据库层", "description": "SQLite 异步引擎与会话管理、ChromaDB 向量数据库客户端",
     "nodeIds": ["file:src/thesis_studio/db/__init__.py", "file:src/thesis_studio/db/chroma.py", "file:src/thesis_studio/db/sqlite.py"]},
    {"id": "layer:llm", "name": "LLM 层", "description": "大语言模型统一接口、工厂模式、Ollama/OpenAI 双实现",
     "nodeIds": ["file:src/thesis_studio/llm/__init__.py", "file:src/thesis_studio/llm/base.py", "file:src/thesis_studio/llm/factory.py", "file:src/thesis_studio/llm/ollama.py", "file:src/thesis_studio/llm/openai.py"]},
    {"id": "layer:embedding", "name": "嵌入层", "description": "文本嵌入模型统一接口 Protocol",
     "nodeIds": ["file:src/thesis_studio/embedding/__init__.py", "file:src/thesis_studio/embedding/base.py"]},
    {"id": "layer:models", "name": "模型层", "description": "SQLAlchemy ORM 基类",
     "nodeIds": ["file:src/thesis_studio/models/__init__.py", "file:src/thesis_studio/models/base.py"]},
    {"id": "layer:workflow", "name": "工作流层", "description": "十阶段工作流接口与上下文传递",
     "nodeIds": ["file:src/thesis_studio/workflow/__init__.py", "file:src/thesis_studio/workflow/base.py"]},
    {"id": "layer:ui", "name": "界面层", "description": "Chainlit 对话交互 + NiceGUI 管理面板",
     "nodeIds": ["file:src/thesis_studio/ui/__init__.py", "file:src/thesis_studio/ui/chainlit_app.py", "file:src/thesis_studio/ui/nicegui_app.py"]},
    {"id": "layer:placeholders", "name": "占位模块", "description": "待开发的功能模块：文献检索、数据分析、论文撰写、通用工具",
     "nodeIds": ["file:src/thesis_studio/literature/__init__.py", "file:src/thesis_studio/analysis/__init__.py", "file:src/thesis_studio/writing/__init__.py", "file:src/thesis_studio/utils/__init__.py"]},
    {"id": "layer:tests", "name": "测试层", "description": "单元测试与全局 fixtures",
     "nodeIds": ["file:tests/__init__.py", "file:tests/unit/__init__.py", "file:tests/integration/__init__.py", "file:tests/conftest.py", "file:tests/unit/test_config.py", "file:tests/unit/test_llm.py", "file:tests/unit/test_workflow.py"]},
    {"id": "layer:docs", "name": "文档层", "description": "项目说明、AI 代码规范、技术栈、工作流、路线图",
     "nodeIds": ["document:README.md", "document:AGENTS.md", "document:CONTRIBUTING.md", "document:doc/TECH_STACK.md", "document:doc/WORKFLOW.md", "document:doc/ROADMAP.md", "document:doc/ARCHITECTURE.md"]},
    {"id": "layer:package-init", "name": "包初始化", "description": "Thesis Studio 顶层包初始化",
     "nodeIds": ["file:src/thesis_studio/__init__.py"]},
]

# ── 导览 ──────────────────────────────────────────────
tour = [
    {"order": 1, "title": "项目概览", "description": "从 README 和 AGENTS.md 了解项目定位与 AI 代码规范",
     "nodeIds": ["document:README.md", "document:AGENTS.md"]},
    {"order": 2, "title": "启动入口", "description": "main.py 创建 FastAPI 应用并启动 Uvicorn 服务",
     "nodeIds": ["file:main.py"]},
    {"order": 3, "title": "配置管理", "description": "Pydantic Settings 从 .env 加载全局配置，lru_cache 单例",
     "nodeIds": ["file:src/thesis_studio/config/settings.py", "config:.env.example"]},
    {"order": 4, "title": "核心异常", "description": "领域异常层级，所有业务异常继承 Thesis StudioError",
     "nodeIds": ["file:src/thesis_studio/core/exceptions.py"]},
    {"order": 5, "title": "日志配置", "description": "结构化日志，输出到 stderr",
     "nodeIds": ["file:src/thesis_studio/core/logging.py"]},
    {"order": 6, "title": "LLM 抽象层", "description": "Protocol 接口 + 工厂模式 + Ollama/OpenAI 双实现，配置驱动切换",
     "nodeIds": ["file:src/thesis_studio/llm/base.py", "file:src/thesis_studio/llm/factory.py", "file:src/thesis_studio/llm/ollama.py", "file:src/thesis_studio/llm/openai.py"]},
    {"order": 7, "title": "数据库层", "description": "SQLite 异步引擎与会话管理、ChromaDB 向量数据库客户端",
     "nodeIds": ["file:src/thesis_studio/db/sqlite.py", "file:src/thesis_studio/db/chroma.py"]},
    {"order": 8, "title": "工作流引擎", "description": "十阶段工作流接口与上下文传递机制",
     "nodeIds": ["file:src/thesis_studio/workflow/base.py"]},
    {"order": 9, "title": "API 层", "description": "FastAPI 应用工厂：健康检查端点与全局异常处理",
     "nodeIds": ["file:src/thesis_studio/api/app.py"]},
    {"order": 10, "title": "界面层", "description": "Chainlit 对话交互 + NiceGUI 管理面板",
     "nodeIds": ["file:src/thesis_studio/ui/chainlit_app.py", "file:src/thesis_studio/ui/nicegui_app.py"]},
    {"order": 11, "title": "项目文档", "description": "技术栈选型、十阶段工作流设计、六阶段开发路线图",
     "nodeIds": ["document:doc/TECH_STACK.md", "document:doc/WORKFLOW.md", "document:doc/ROADMAP.md"]},
]

# ── 组装并写入 ─────────────────────────────────────────
graph = {
    "version": "1.0.0",
    "project": {
        "name": "Thesis Studio",
        "languages": ["Python"],
        "frameworks": ["FastAPI", "Pydantic", "SQLAlchemy", "Chainlit", "NiceGUI", "ChromaDB"],
        "description": "面向本科/研究生毕业论文生成的个人开源 AI 研究助手。本地优先，免费开源，模块化。",
        "analyzedAt": datetime.now(timezone.utc).isoformat(),
        "gitCommitHash": "unknown",
    },
    "nodes": nodes,
    "edges": edges,
    "layers": layers,
    "tour": tour,
}

INTER.mkdir(parents=True, exist_ok=True)
out = INTER / "assembled-graph.json"
out.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"写入 {out}：{len(nodes)} 节点，{len(edges)} 边，{len(layers)} 层，{len(tour)} 导览步骤")
print(f"节点类型分布: { {t: sum(1 for n in nodes if n['type'] == t) for t in set(n['type'] for n in nodes)} }")
print(f"边类型分布: { {t: sum(1 for e in edges if e['type'] == t) for t in set(e['type'] for e in edges)} }")
print(f"层: {', '.join(l['name'] for l in layers)}")
