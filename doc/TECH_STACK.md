# Thesis Studio 技术栈

## 概述

本文档列出 Thesis Studio 系统所需的核心技术栈，按功能模块分类，并提供推荐版本和选型理由。

---

## 一、核心架构层

### 1.1 后端框架

| 技术 | 推荐版本 | 用途 | 选型理由 |
|------|---------|------|---------|
| **FastAPI** | 0.100+ | Web 框架 | 轻量、快速、自动生成文档，适合个人项目 |
| **Uvicorn** | 0.23+ | ASGI 服务器 | 轻量级异步服务器 |
| **Pydantic** | 2.0+ | 数据验证 | 与 FastAPI 深度集成，简化数据校验 |

### 1.2 前端界面

| 技术 | 推荐版本 | 用途 | 选型理由 |
|------|---------|------|---------|
| **Chainlit** | 1.0+ | 对话交互 UI | 专为 LLM 应用设计，流式输出、多步骤对话、文件上传，论文生成天然适配 |
| **NiceGUI** | 1.4+ | 管理面板 | Python 原生，组件丰富（表格、表单、图表），适合文献管理、数据面板等复杂界面 |

**分工说明**：
- **Chainlit**：负责论文生成主流程（选题对话、文献综述生成、章节撰写等），消息式交互，引导用户逐步完成
- **NiceGUI**：负责管理面板（文献库浏览/管理、项目进度看板、数据分析面板、设置页面等）

### 1.3 数据库

| 技术 | 推荐版本 | 用途 | 选型理由 |
|------|---------|------|---------|
| **SQLite** | 3.40+ | 主数据库 | 零配置，单文件，适合个人使用，无需安装数据库服务 |
| **ChromaDB** | 0.4+ | 向量数据库 | 轻量级，本地运行，支持语义检索 |

---

## 二、AI/LLM 核心层

### 2.1 大语言模型（本地优先）

| 技术 | 用途 | 选型理由 |
|------|------|---------|
| **Ollama + Qwen2.5/Llama 3** | 本地模型部署 | 免费，数据隐私，离线可用，适合个人使用 |
| **OpenAI API (GPT-4)** | 云端备选 | 质量高，按需使用，控制成本 |
| **vLLM** | 本地推理加速（可选） | 提升本地模型推理速度 |

**推荐策略**：日常使用本地模型，复杂任务可选用云端 API

### 2.2 嵌入模型

| 技术 | 用途 | 选型理由 |
|------|------|---------|
| **sentence-transformers** | 文献向量化 | 开源免费，本地部署，支持中文 |
| **BGE-M3** | 多语言嵌入 | 中英双语支持好，开源免费，质量优秀 |

### 2.3 Agent 框架

| 技术 | 用途 | 选型理由 |
|------|------|---------|
| **LangChain** | Agent 工作流 | 生态完善，文档齐全，社区活跃 |
| **自研轻量级框架** | 定制化流程 | 简单可控，更贴合业务流程，减少依赖 |

---

## 三、文献处理层

### 3.1 学术数据库接口（免费优先）

| 技术 | 用途 | 选型理由 |
|------|------|---------|
| **Semantic Scholar API** | 英文文献检索 | 免费，覆盖广，API 友好 |
| **arXiv API** | 预印本检索 | 免费，CS/物理/数学领域覆盖全 |
| **CrossRef API** | DOI 元数据 | 免费，标准化元数据 |
| **OpenAlex API** | 开放学术图谱 | 免费，替代 Microsoft Academic |
| **DBLP API** | CS 领域文献 | 免费，计算机科学专业数据库 |
| **手动导入** | 中文文献 | 支持从 CNKI/万方手动下载后导入 |

### 3.2 PDF 处理

| 技术 | 用途 | 选型理由 |
|------|------|---------|
| **PyMuPDF (fitz)** | PDF 文本提取 | 速度快，功能全面，用户偏好 |
| **pdfplumber** | 表格提取 | 表格识别准确，基于 pdfminer |
| **marker** | PDF 转 Markdown | 保留格式结构，适合学术论文 |
| **Pillow** | 图像处理 | 轻量级，用户已在使用 |

### 3.3 文献管理

| 技术 | 用途 | 选型理由 |
|------|------|---------|
| **自建文献库** | 元数据存储 | SQLite，简单可控，无需外部依赖 |
| **bibtexparser** | BibTeX 处理 | 解析和生成 BibTeX 文件 |
| **Zotero 集成** | 可选导入导出 | 支持从 Zotero 导入文献库 |

---

## 四、数据分析层

### 4.1 数据处理

| 技术 | 推荐版本 | 用途 | 选型理由 |
|------|---------|------|---------|
| **pandas** | 2.0+ | 数据清洗、转换 | 数据分析标准库，功能强大 |
| **numpy** | 1.24+ | 数值计算 | 科学计算基础库 |

### 4.2 统计分析

| 技术 | 用途 | 选型理由 |
|------|------|---------|
| **scipy.stats** | 统计检验 | 科学计算标准库，轻量 |
| **statsmodels** | 回归分析 | 功能全面，文档完善 |
| **pingouin** | 心理统计学（可选） | 易于使用，输出美观 |

### 4.3 可视化

| 技术 | 用途 | 选型理由 |
|------|------|---------|
| **matplotlib** | 静态图表 | 标准绘图库，高度可定制 |
| **seaborn** | 统计可视化 | 基于 matplotlib，更美观 |
| **plotly** | 交互式图表（可选） | 交互性强，便于展示 |

---

## 五、文档生成层

### 5.1 论文排版

| 技术 | 用途 | 选型理由 |
|------|------|---------|
| **python-docx** | Word 文档生成 | 操作 Word 文档的标准库，本科生常用 |
| **Pandoc** | 格式转换 | Markdown → Word/PDF，简化排版流程 |

### 5.2 引用管理

| 技术 | 用途 | 选型理由 |
|------|------|---------|
| **bibtexparser** | BibTeX 处理 | 解析和生成 BibTeX 文件 |
| **自建引用管理器** | 引用格式化 | 简单可控，支持 GB/T 7714、APA 等格式 |

### 5.3 PPT 生成

| 技术 | 用途 | 选型理由 |
|------|------|---------|
| **python-pptx** | 答辩 PPT 生成 | 操作 PowerPoint 的标准库 |

---

## 六、辅助工具层

### 6.1 文件存储

| 技术 | 用途 | 选型理由 |
|------|------|---------|
| **本地文件系统** | 文件存储 | 简单直接，配合 SQLite 索引，无需额外服务 |

### 6.2 版本控制

| 技术 | 用途 | 选型理由 |
|------|------|---------|
| **Git** | 代码版本控制 | 标准版本控制工具，开源项目必备 |
| **GitHub** | 代码托管 | 开源社区标准平台 |

### 6.3 开发工具

| 技术 | 用途 | 选型理由 |
|------|------|---------|
| **Poetry/uv** | 依赖管理 | 现代化 Python 包管理，简化环境配置 |
| **pytest** | 单元测试 | 标准测试框架，保证代码质量 |
| **pre-commit** | 代码质量 | 自动化代码检查和格式化 |

---

## 七、推荐技术栈组合

```yaml
后端:
  - FastAPI + Uvicorn
  - SQLite（主数据库）
  - ChromaDB（向量存储）

前端:
  - Chainlit（对话交互 UI，论文生成主流程）
  - NiceGUI（管理面板，文献库/数据面板）

LLM:
  - Ollama + Qwen2.5/Llama 3（本地模型，默认）
  - OpenAI API（可选，按需使用）
  - sentence-transformers / BGE-M3（嵌入模型）

文献处理:
  - PyMuPDF + pdfplumber + marker
  - Semantic Scholar + arXiv + CrossRef + OpenAlex API
  - 手动导入（支持 CNKI/万方下载后导入）

数据分析:
  - pandas + numpy
  - scipy.stats + statsmodels
  - matplotlib + seaborn

文档生成:
  - python-docx（Word 输出）
  - python-pptx（PPT 输出）
  - Pandoc（格式转换）
  - bibtexparser（引用管理）

开发工具:
  - hatchling/pip（依赖管理）
  - Git + GitHub（版本控制）
  - pytest（测试）

部署:
  - 本地运行（python main.py 一键启动）
  - 可选 Docker 容器化（便于其他用户部署）
```

---

## 八、依赖管理

### pyproject.toml 结构（Poetry）

```toml
[tool.poetry]
name = "thesis_studio"
version = "0.1.0"
description = "面向本科毕业论文生成的 Thesis Studio 系统"
authors = ["Your Name <your.email@example.com>"]
license = "MIT"
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.10"

# 核心框架
fastapi = "^0.100.0"
uvicorn = "^0.23.0"
pydantic = "^2.0.0"
chainlit = "^1.0.0"
nicegui = "^1.4.0"

# 数据库
sqlalchemy = "^2.0.0"
chromadb = "^0.4.0"

# LLM & AI
openai = "^1.0.0"  # 可选，云端 API
langchain = "^0.0.300"
sentence-transformers = "^2.2.0"

# 文献处理
pymupdf = "^1.23.0"
pdfplumber = "^0.9.0"
marker-pdf = "^0.1.0"

# 数据分析
pandas = "^2.0.0"
numpy = "^1.24.0"
scipy = "^1.11.0"
statsmodels = "^0.14.0"

# 可视化
matplotlib = "^3.7.0"
seaborn = "^0.12.0"

# 文档生成
python-docx = "^0.8.11"
python-pptx = "^0.6.21"
pypandoc = "^1.11"
bibtexparser = "^1.4.0"

# 工具库
requests = "^2.31.0"
python-dotenv = "^1.0.0"
httpx = "^0.24.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
black = "^23.7.0"
ruff = "^0.0.285"
pre-commit = "^3.3.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### 快速安装

```bash
# 克隆项目
git clone https://github.com/yourusername/thesis_studio.git
cd thesis_studio

# 安装依赖
poetry install

# 或手动安装
pip install -r requirements.txt

# 启动应用
poetry run python main.py
# 或分别启动
chainlit run app.py  # 对话交互界面
nicegui run admin.py  # 管理面板
```
