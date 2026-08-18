# EXPLORING 阶段设计文档

> 文献探索：围绕用户方向检索文献、聚类分析、产出综述，为 DESIGNING 提供决策依据。

---

## 一、定位

EXPLORING 是项目启动后的第一个工作阶段。用户带着研究方向入场，AI 辅助完成文献检索、筛选、聚类、综述，产出一份结构化的领域知识全景。这份产出是 DESIGNING 阶段做研究规划的基础。

---

## 二、输入

| 输入 | 来源 | 说明 |
|------|------|------|
| 用户原始方向 | 项目创建时填写 | 用户带入场的研究方向，如"机器学习在医疗诊断中的应用" |
| 专业背景 | 用户信息 | 可选，用于检索式优化 |

---

## 三、输出

| 输出 | 消费方 | 说明 |
|------|--------|------|
| 文献综述 | DESIGNING | 按主题聚类的综述报告，梳理研究脉络、标注关键论点和争议点 |
| 文献库 | DESIGNING | 结构化论文元数据（标题、作者、摘要、关键词、质量评分），持久化到 SQLite |
| 研究空白 | DESIGNING | 综述中识别出的未被覆盖的研究方向 |

---

## 四、工作流

```
用户方向
    ↓
检索式构建 → 自动生成中英文检索式
    ↓
批量检索 → Semantic Scholar + arXiv
    ↓
去重筛选 → 标题/摘要初筛，全文质量深度筛选
    ↓
AI 聚类 → 按主题分组，生成聚类标签
    ↓
综述生成 → 按主题梳理脉络，标注争议点和研究空白
    ↓
文献综述 + 文献库 + 研究空白
```

---

## 五、界面

### 聊天室 + 知识图谱 + 文献详情

微信式聊天室 + 知识图谱（echarts 力导向图）+ 文献详情面板（右侧滑出），三区联动。

### 文献库入口

页面顶部提供**文献库按钮**，用户可随时打开文献库面板，浏览已入库的论文列表：

- 查看论文标题、作者、摘要、关键词
- 筛选和排序
- 标记核心文献 / 排除无关文献
- 确认文献覆盖度，为进入 DESIGNING 做准备

---

## 六、上下游

```
用户原始方向
    ↓
EXPLORING
    ↓ 产出：文献综述 + 文献库 + 研究空白
    ↓
DESIGNING
    ↓ 产出：论文题目 + 论文大纲
    ↓
RESEARCHING → WRITING → POLISHING → COMPLETED
```

---

## 七、技术实现

### 学术搜索

| API | 说明 |
|-----|------|
| Semantic Scholar | 英文文献检索，免费 key 可选 |
| arXiv | 预印本检索，无需认证 |

### AI 聚类与综述

由 LLM 直接进行主题分析和综述生成，不依赖 scikit-learn 等算法包。

### 文献持久化

论文检索后自动通过 `PaperRepository` 持久化到 SQLite，文献库面板从数据库读取展示。

### 代码结构

```
domain/agent/researcher.py      → Agent 协议与数据模型
domain/skill/                   → Skill 协议与接口定义
infrastructure/search/          → Semantic Scholar / arXiv 客户端
infrastructure/skill/           → 4 个 Skill 实现
infrastructure/agent/           → Researcher Agent 实现
infrastructure/db/              → SQLite 文献库持久化
application/exploring/          → 消息路由 + 流式 SSE + pipeline
presentation/ui/exploring/      → 聊天室 + 知识图谱 + 文献详情 + 文献库面板
```
