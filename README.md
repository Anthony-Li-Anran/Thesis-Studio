# Thesis Studio

面向本科/研究生毕业论文生成的开源 AI 研究助手。本地优先，免费开源，模块化。

## 定位

**场景B**：用户带着明确的研究题目入场，AI 辅助完成从文献探索、研究规划、研究实施、论文撰写到打磨交付的全流程。系统不负责"帮用户找题目"，而是帮用户**把已有的题目落地为一篇高质量学术论文**。

## 文档索引

| 文档 | 说明 |
|------|------|
| [技术栈](doc/TECH_STACK.md) | 核心技术选型与依赖管理 |
| [工作流程](doc/WORKFLOW.md) | 论文生成全流程设计（四阶段 7 状态机） |
| [文献探索](doc/EXPLORING.md) | EXPLORING 阶段设计（输入输出、工作流） |
| [研究规划](doc/DESIGNING.md) | DESIGNING 阶段设计（多 Agent 辩论、大纲协同编辑） |
| [研究实施](doc/RESEARCHING.md) | RESEARCHING 阶段设计（数据收集/分析、代码执行、推导） |
| [开发路线图](doc/ROADMAP.md) | 开发阶段与里程碑 |
| [系统架构](doc/ARCHITECTURE.md) | 模块结构与数据流 |

## 当前功能

- **项目管理**: 创建、查看、编辑、删除项目（CRUD），7 状态机全生命周期
- **搜索**: 正则匹配标题、描述、关键词（防抖 0.4s）
- **排序**: 按名称 / 最近编辑时间升降序切换
- **视图**: 列表 / 网格双视图切换
- **认证**: 登录 / 注册 / 游客模式
- **用户隔离**: 每个帐号只能看到自己的项目，游客数据退出即清空
- **主题**: 暗色 / 亮色主题切换
- **国际化**: 中英文界面切换
- **项目状态**: 7 状态机（初始 → 文献探索 → 研究规划 → 研究实施 → 论文撰写 → 打磨交付 → 已完成），首页彩色标签
- **AI 配置**: 多模型配置管理（API Endpoint / Key / Model），Agent 角色分配，游客模式内存存储
- **文献探索 (EXPLORING)**: 微信式聊天室 + 知识图谱 + 文献详情面板 + 文献库，Researcher Agent 自动检索/聚类/综述
- **研究规划 (DESIGNING)**: 多 Agent 辩论（Researcher/Debater/Reviewer）+ @mention 协作 + 大纲协同编辑器 + 格式要求抽屉 + 粒度校验门禁
- **研究实施 (RESEARCHING)**: 阶段设计文档完成，子问题拆解/代码执行/LaTeX 推导/沙箱执行（实现中）

## 快速开始

```bash
git clone https://github.com/yourusername/thesis_studio.git
cd thesis_studio
conda activate thesis_studio
pip install -e ".[dev]"
python main.py
```

## 项目结构

```
thesis_studio/
├── src/thesis_studio/
│   ├── domain/              # 领域层：实体、端口协议、Agent/Skill/Workflow
│   ├── application/         # 应用层：用例编排（exploring）
│   ├── infrastructure/      # 基础设施层：LLM 适配器、搜索客户端、DB 仓储、沙箱
│   ├── presentation/        # 接口层：FastAPI + NiceGUI 管理面板 + Chainlit
│   └── config/              # 配置管理（Pydantic Settings）
├── tests/                   # 单元测试 + 集成测试
├── doc/                     # 设计文档
├── data/                    # 运行时数据（项目文件、文献库）
├── pyproject.toml           # 项目元数据与工具配置
└── main.py                  # 应用入口
```

## 架构

基于 **Clean Architecture + Hexagonal Architecture + SOLID** 原则：

```
Presentation → Application → Domain ← Infrastructure
                                  ↑
                         (端口/适配器模式)
```

- 领域层零外部依赖，纯 Python dataclass + Protocol
- 应用层只依赖领域端口抽象，通过构造函数注入
- 基础设施层实现所有端口，组合根统一装配
- 接口层通过桥接模块获取服务，不直接依赖基础设施

## 质量门禁

| 工具 | 配置 | 状态 |
|------|------|------|
| ruff | 行宽 100, py311, E/F/W/I/N/UP/B/SIM | ✅ |
| mypy | strict=true | ✅ |
| pytest | asyncio_mode=auto | ✅ |

## 许可协议

MIT
