# Thesis Studio 开发路线图

做到什么写什么，不画饼。

## Phase 1: 基础框架搭建

- [x] DDD 分层架构（Clean Architecture + Hexagonal）
- [x] Poetry/uv 依赖管理（pyproject.toml）
- [x] conda 虚拟环境（thesis_studio）
- [x] Chainlit 配置预留（.chainlit/）
- [x] NiceGUI 入口框架（nicegui_app.py）
- [x] 配置管理模块（config/settings.py）

## Phase 2: 主页和项目管理

- [x] Prism 风格首页布局（桌面端）
- [x] 暗色 / 亮色主题切换
- [x] 中英文语言切换
- [x] 可折叠 / 可拖拽侧边栏
- [x] 项目列表骨架屏
- [x] 排序功能（Name / Last edited 升降序切换）
- [x] 列表 / 网格视图切换按钮
- [x] Import / New 按钮组
- [x] Sign in 按钮
- [x] 项目 CRUD（创建 / 详情 / 编辑 / 删除确认）
- [x] 项目三点菜单（编辑 / 删除，删除红字 + 二次确认）
- [x] 正则搜索（匹配标题 / 描述 / 关键词，防抖 0.4s）
- [x] 用户认证（登录 / 注册 / 游客模式）
- [x] 用户隔离（每个帐号只能看到自己的项目，游客数据退出即清空）
- [x] 设置齿轮入口（侧边栏右下角，Phase 3 完成）

## Phase 3: 设置与 AI 配置

- [x] 设置卡片 UI（AI Config CRUD：添加/编辑/删除配置）
- [x] 多 Agent 角色分配（Researcher / Executor 等）
- [x] API Key 显隐切换
- [x] 游客模式设置（内存存储，退出即清空）
- [x] 编码修复（BOM 移除、乱码文档字符串替换）

## Phase 4: 项目内工作流

- [x] 7 状态机模型（INIT → EXPLORING → DESIGNING → RESEARCHING → WRITING → POLISHING → COMPLETED）
- [x] 首页项目卡片彩色状态标签（列表/网格双视图，7 色区分，中英文）
- [x] 项目详情页改造：从纯展示变为工作流交互界面
- [x] 阶段进度条组件（7 状态圆点+连线，当前高亮，完成打勾）
- [x] EXPLORING 页面布局（左侧聊天室 + 右侧知识图谱，三区联动）
- [x] 微信式聊天室（流式消息、@Agent 内联选择、头像+气泡）
- [x] EXPLORING 后端核心（AgentProtocol + Skill 协议 + Sandbox + 4 Skill 实现）
- [x] 学术搜索客户端（Semantic Scholar + arXiv API 对接）
- [x] Researcher Agent 实现（LangGraph 工作流：意图路由→查询扩展→检索→解析→AI 聚类→综述→报告）
- [x] AgentService（消息路由 + 流式 SSE 桥接 + 7 意图分发 + 前端集成）
- [x] 文献知识图谱（echarts 力导向图，聚类节点+论文连线，双区联动）
- [x] 文献详情面板（右侧滑出，标题/作者/摘要/方法/结论/关联）
- [x] 文献综述材料输出（HTML 报告生成 + 下载按钮，按主题聚类）
- [x] EXPLORING 阶段持久化（论文落库 PaperRepository、项目状态推进、确认按钮接入）
- [x] DESIGNING 阶段（研究问题定义、方法设计、开题报告生成）
- [ ] RESEARCHING 阶段（数据收集、清洗、分析、假设验证）
- [ ] WRITING 阶段（IMRaD 大纲、逐章撰写、引用管理、图表生成）
- [ ] POLISHING 阶段（润色、查重、格式规范、答辩 PPT 生成）
