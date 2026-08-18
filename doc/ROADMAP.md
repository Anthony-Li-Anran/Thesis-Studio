# Thesis Studio 开发路线图

做到什么写什么，不画饼。

## Phase 1: 基础框架搭建

- [x] DDD 分层架构（Clean Architecture + Hexagonal）
- [x] pyproject.toml 依赖管理（hatchling）
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

### EXPLORING 阶段

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

### DESIGNING 阶段

- [x] 聊天室（多 Agent 辩论 + @mention + 辩论流程 + 粒度审查）
- [x] 消息渲染器（左对齐气泡 + @mention 高亮 + Markdown 格式）
- [x] @mention JS（输入框弹出 Agent 选择面板）
- [x] 大纲协同编辑器（编辑/预览/分屏三模式 + 滚动修复）
- [x] 进度检查清单（7 章节自动检测 + 手动切换）
- [x] 格式要求抽屉（4 预设模板 + 自定义上传）
- [x] Diff 建议卡片（逐条确认/修改/拒绝 + 批量操作）
- [x] 大纲粒度校验（LLM 三粒度分类 + 确认门禁）
- [x] 辩论编排器（R→D→R 循环，最多 3 轮，Reviewer 审查）
- [x] 阶段持久化（聊天消息保存、大纲写入 outline.md、状态推进）

### RESEARCHING 阶段

- [x] RESEARCHING 阶段设计文档（`doc/RESEARCHING.md`：子问题拆解/IDE模式/LaTeX模式/沙箱执行/输出规范）
- [ ] 子问题拆解引擎（LLM + Pydantic 结构化输出 → tasks.json）
- [ ] 代码执行沙箱（subprocess 隔离 + 日志收集 + 结果扫描）
- [ ] IDE 模式（Executor 写代码→执行→自修复→Reviewer 审查循环）
- [ ] LaTeX 推导模式（Executor 推导→Researcher 引文→Reviewer 审查循环）
- [ ] 研究结果面板（图表预览 + 数据表格 + 内联建议）
- [ ] 阶段持久化（tasks.json + results/ + code.zip + derivation.tex）

### WRITING 阶段

- [ ] WRITING 阶段设计文档
- [ ] IMRaD 大纲自动生成
- [ ] 逐章撰写（Introduction / Methods / Results / Discussion / Conclusion）
- [ ] 引用管理（GB/T 7714 / APA 格式自动对应）
- [ ] 图表自动生成与嵌入

### POLISHING 阶段

- [ ] POLISHING 阶段设计文档
- [ ] 全文润色（学术语言规范化、逻辑连贯性检查）
- [ ] 查重检查（重复率检测、问题段落标注）
- [ ] 格式规范（字体、行距、页边距、标题层级、图表编号）
- [ ] 答辩 PPT 生成
- [ ] 问答准备（预测评委问题 + 应答要点）
