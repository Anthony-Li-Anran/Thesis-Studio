# RESEARCHING 阶段设计文档

> 研究实施：基于 DESIGNING 产出的研究总规划，执行数据收集、清洗、分析、结果解读。

---

## 一、定位

RESEARCHING 是整个研究的**执行环节**。
与 EXPLORING（文本对话）和 DESIGNING（规划决策）不同，
RESEARCHING 涉及**实际的数据操作**：跑代码、处理文件、生成图表、输出统计结果。

DESIGNING 告诉你 要做什么，RESEARCHING 负责 把它做出来。

---

## 二、输入

### 主要输入：来自 DESIGNING 的研究总规划

DESIGNING 阶段产出的大纲（`outline.md`）是 RESEARCHING 的唯一核心输入。
大纲只提供**章节骨架**（小节标题），不包含任何实现细节。

| 章节 | 提供给 RESEARCHING 的信息 | 示例 |
|------|--------------------------|------|
| **1.2 研究问题** | 要回答的核心问题 | `如何降低 Transformer 的注意力复杂度？` |
| **3.1 研究范式** | 小节标题，指明研究方向 | `3.1 Softmax Kernel with Random Fourier Features` |
| **3.2 研究假设** | 小节标题，暗示要验证的假设 | `3.2 近似误差上界分析` |
| **3.3 实验/调查方案** | 小节标题，确定实验类型 | `3.3 长序列分类实验` |
| **3.4 数据来源与采集** | 小节标题，确定数据方向 | `3.4 合成序列数据生成` |
| **3.5 分析方法** | 小节标题，确定分析路线 | `3.5 注意力效率对比分析` |
| **4 预期结果** | 小节标题，确定输出目标 | `4.1 精度对比实验` |

> 大纲只描述"研究什么"，不描述"怎么做"。数据集选什么、用什么统计方法、实验参数怎么设——这些全部是 RESEARCHING 阶段自己决定。

### 辅助输入：来自 Project 实体

| 字段 | 类型 | 用途 |
|------|------|------|
| `research_question` | `str` | 研究问题（与大纲 1.2 对应） |
| `hypothesis` | `str` | 研究假设（与大纲 3.2 对应） |
| `methodology` | `str` | 方法论简述 |

> 注：EXPLORING 产出的文献库（papers、clusters、review）在本阶段仅作为背景参考，不直接驱动工作流。

---

## 三、输出

### 核心产出：四个文件

| 输出 | 形式 | 内容 | 消费方 |
|------|------|------|--------|
| **tasks.json** | 文件 | 所有子问题清单，含编号、标题、类型、假设、状态、结果解读 | WRITING（Results + Discussion） |
| **results/** | 文件夹 | 按编号存放运行结果：图表（PNG/SVG）、数据（CSV）、日志（log） | WRITING（Results 图表引用） |
| **code.zip** | 压缩包 | 所有实证类子问题的可复现代码，含依赖说明 | 审稿/复现 |
| **derivation.tex** | 文件 | 独立可编译的完整 LaTeX 文档，所有理论类子问题的推导证明 | WRITING（Methods 拼接） |

### 子任务编号规则

每个子任务有唯一 ID，格式：`{类型首字母}{章节号}{序号}`

| 类型 | 首字母 | 示例 |
|------|--------|------|
| 理论 | T | `T301` = 第3章第1个理论任务 |
| 实证 | E | `E401` = 第4章第1个实证任务 |

### tasks.json 结构

```json
{
  "tasks": [
    {
      "id": "T301",
      "title": "Softmax Kernel with Random Fourier Features",
      "type": "theory",
      "hypothesis": "RFF 可在 O(n) 复杂度内近似 Softmax 注意力",
      "status": "completed",
      "results": {
        "derivation_section": "T301",
        "key_findings": ["证明了 RFF 近似的误差上界为 O(log n)"],
        "interpretation": "该结果与 Choromanski 等 (2021) 的 Performer 一致，但本推导给出了更紧的界。"
      }
    },
    {
      "id": "E401",
      "title": "Long Sequence Classification",
      "type": "empirical",
      "hypothesis": "RFF 注意力在长序列上保持分类精度",
      "status": "completed",
      "results": {
        "files": ["E401_accuracy.csv", "E401_figure_1.png", "E401_run.log"],
        "key_metrics": {"accuracy": 0.94, "runtime_s": 12.3},
        "interpretation": "序列长度 4096 时精度仅下降 0.3%，验证了 RFF 的稳定性。但 CPU 推理速度仍慢于基线，可能需要进一步优化。"
      }
    }
  ],
  "summary": "全部 5 个子问题完成，3 个假设支持，1 个部分支持，1 个不支持。"
}
```

### 文件结构

```
data/projects/{id}/researching/
├── tasks.json
├── results/
│   ├── E401_accuracy.csv
│   ├── E401_figure_1.png
│   ├── E402_run.log
│   └── ...
├── code.zip
│   ├── E401_experiment.py
│   ├── E402_benchmark.py
│   └── requirements.txt
└── derivation.tex
```

### 关键设计决策

- **derivation.tex 是独立可编译的完整文档**：包含 preamble、章节结构，可单独编译为 PDF，也可供 WRITING 阶段拼入方法论章节
- **结果解读内聚在 tasks.json 中**：每个子问题的 `interpretation` 字段直接支撑 WRITING 阶段的 Discussion 撰写
- **results/ 按 id 命名**：文件名带编号前缀，与 tasks.json 中的 id 一一对应
- **code.zip 含依赖**：包含 `requirements.txt`，确保可复现

---

## 四、工作流

### 场景一：实证类子问题

每个实证子问题走 **生成 → 执行 → 验证 → 迭代** 循环：

```
子问题 "4.1 Long Sequence Classification"
    ↓
LLM 生成 Python 脚本
    ↓
沙箱执行（subprocess + timeout）
    ↓
收集结果：stdout + 文件（图表/CSV）+ 日志
    ↓
LLM 检查结果合理性
    ├── 合理 → 用户确认 → 保存代码 + 结果
    └── 不合理 → LLM 修代码 → 回到执行
        （最多 3 轮）
```

**关键设计**：
- 代码不是 AI 的，是用户的。AI 生成初稿，用户可随时编辑修改
- 执行在现有 conda 环境（`thesis_studio`）中运行，沙箱限制可写目录
- 每轮执行都保存 log，失败代码也保留，方便追溯
- 用户点击"采纳"后自动 git commit

### 场景二：理论类子问题

每个理论子问题走 **文献检索 → 推导生成 → 用户审查** 循环：

```
子问题 "3.1 Softmax Kernel with RFF"
    ↓
从 EXPLORING 文献库检索相关论文，提取关键定理/公式
    ↓
LLM 基于文献逐步推导，标注引用
    ↓
生成 LaTeX 源码，追加到 derivation.tex 对应章节
    ↓
用户审查 + 编辑
    ├── 满意 → 采纳
    └── 不满意 → 聊天讨论 / LLM 重写
```

**关键设计**：
- 推导基于 EXPLORING 文献库，每步标注 `\cite{}`
- 推导结果直接追加到 `derivation.tex`，保持完整可编译
- 用户是最终审查者，AI 只是助手

﻿### 子问题拆解

DESIGNING 产出的大纲进入 RESEARCHING 后，LLM 自动解析所有 `###` 标题：

```
outline.md
    ↓
LLM 解析每个 ### 标题
    ↓
判定类型：理论 / 实证
    ↓
生成 tasks.json 骨架
    ↓
用户确认 / 调整
```

---

﻿## 五、前端设计

### 设计原则

参考 TRAE、ChatGPT Canvas、Cursor 等主流 AI 编程工具的布局模式：
- **三栏布局**：任务列表 + 编辑区 + 执行结果，信息密度高但不拥挤
- **双视图切换**：IDE 视图（实证类）+ LaTeX 视图（理论类），一键切换
- **AI 内联建议**：不弹窗不打断，AI 建议直接出现在代码旁
- **任务即文件树**：点击任务 = 打开关联文件，零心智负担

### 整体布局

```
┌──────────┬────────────────────────┬───────────────────┐
│  Header: 返回 | 阶段进度 | [IDE ●══ LaTeX] | [导出]  │
├──────────┼────────────────────────┼───────────────────┤
│ 任务列表  │    编辑区（主）          │   执行结果（右）     │
│          │                        │                   │
│ ▼ 3 理论  │  [Chat] [Editor] Tab   │  > Execution Log   │
│  ✓ 3.1   │                        │  accuracy: 0.94    │
│  ✓ 3.2   │  import torch          │                   │
│  ○ 3.3   │  model = ...           │  ┌─ figure_1 ────┐ │
│ ▼ 4 实证  │  ...                   │  │  [chart]      │ │
│  * 4.1   │                        │  └───────────────┘ │
│  ○ 4.2   │  [▶ Run] [💾 Save]    │                   │
│  ○ 4.3   │  [✅ Apply]            │  [Satisfied]      │
│          │                        │  [Rerun]          │
│          │  ── AI Suggestion ──   │                   │
│          │  "Try batch_size=64"   │                   │
│          │  [Accept] [Reject]     │                   │
└──────────┴────────────────────────┴───────────────────┘
```

### 三区详解

**左区：任务列表（~20%）**

- 固定宽度，始终可见，可折叠
- 树形结构：章 → 节 → 子任务，展开子任务显示其下文件
- 状态图标：`*` 进行中 / `✓` 已完成 / `○` 待处理
- 点击实证任务自动切 IDE 视图，点击理论任务自动切 LaTeX 视图
- 底部常驻 `derivation.tex` 入口（理论汇总文档）

**中区：编辑区（~50%）**

- 实证子问题：CodeMirror 6 Python 编辑器，语法高亮 + 自动补全
- 理论子问题：双 Tab — Chat（讨论推导思路）和 Editor（编辑 LaTeX 源码）
- LaTeX Editor 支持 KaTeX 实时预览
- [▶ Run] 执行代码 / [💾 Save] 保存 / [✅ Apply] 采纳并 git commit
- 采纳后任务状态自动更新为 `completed`

**右区：执行结果（~30%）**

- 执行日志：`ui.log()` 展示 stdout/stderr，自动滚动
- 图表预览：`ui.image()` 展示生成的 PNG/SVG
- 数据表格：`ui.table()` 展示 CSV 结果
- [Satisfied] / [Rerun] 按钮：用户评判结果，不满意则触发 AI 修复

### 两视图切换

Header 中放置滑动 Switch，在 IDE 和 LaTeX 间切换，切换保持当前选中任务：

| 视图 | 适用任务 | 中区 | 右区 |
|------|---------|------|------|
| **IDE** | 实证类（E 开头） | 代码编辑器 + Run/Save/Apply | 执行日志 + 图表 + 数据表格 |
| **LaTeX** | 理论类（T 开头） | Chat Tab / LaTeX Editor Tab | KaTeX 实时预览 |

### 核心组件

| 组件 | 技术 | 说明 |
|------|------|------|
| 代码编辑器 | CodeMirror 6 | 轻量（~100KB）、语法高亮、可编辑 |
| LaTeX 编辑器 | CodeMirror 6 + KaTeX | 左侧编辑源码，右侧实时渲染 |
| AI 聊天 | 复用 ChatRoom 组件 | @mention、流式输出、Agent 头像 |
| 任务列表 | NiceGUI `ui.tree()` | 树形展开，文件联动 |
| 执行日志 | NiceGUI `ui.log()` | 终端输出实时流 |
| 图表预览 | NiceGUI `ui.image()` | 支持 PNG/SVG |
| 数据表格 | NiceGUI `ui.table()` | CSV 结果展示 |
| 内联建议 | AI 行内 Diff 卡片 | 选中代码行 → AI 建议 → 接受/拒绝 |

### 与 EXPLORING/DESIGNING 的复用

- 复用 ChatRoom 组件（@mention、流式输出、建议按钮、Agent 头像/颜色）
- 复用双栏布局框架，扩展为三栏（`flex:1; display:flex; overflow:hidden`）
- 复用 Header（返回按钮、阶段进度、主题切换、语言切换）
- 复用文献库对话框（Researcher 引用文献时弹出）
- 新增：CodeMirror 6 编辑器、KaTeX 预览、任务列表树、执行结果面板、视图切换 Switch

> 新增依赖仅 CodeMirror 6 + KaTeX，CDN 引入即可。界面方案为暂定，后续实现时可能调整。

---

## 六、Agent 协作模式

### 两种模式，两支 Agent 团队

RESEARCHING 不是 AI 提建议，而是 AI **主动写代码/推导、执行、debug、自我审查**。用户是最终审查者和决策者。

### IDE 模式（实证类子问题）

三 Agent 循环协作，直到 Reviewer 通过：

```
Executor 写代码 → 沙箱执行 → 报错？→ 自己读日志 debug → 重跑
    ↓
Researcher 提供算法思路、解释结果、关联文献
    ↓
Reviewer 审查：代码是否验证了假设？结果是否合理？
    ↓
不通过 → Executor 修改 → 再执行 → 再审查
通过 → 等待用户确认
```

| Agent | 职责 |
|-------|------|
| **Executor** | 写 Python 代码、在沙箱中执行、读取错误日志、自修复 bug、重跑 |
| **Researcher** | 提供算法/方法选择建议、解释实验结果含义、从文献库引用相关论文 |
| **Reviewer** | 审查代码是否验证了假设、结果是否合理、是否有遗漏的边界情况 |

### LaTeX 模式（理论类子问题）

三 Agent 循环协作，直到 Reviewer 通过：

```
Executor 生成 LaTeX 推导步骤、逐步推演公式
    ↓
Researcher 从文献库检索相关定理、提供引用
    ↓
Reviewer 审查：推导逻辑是否自洽？数学是否正确？引文是否匹配？
    ↓
不通过 → Executor 修正 → 再审查
通过 → 等待用户确认
```

| Agent | 职责 |
|-------|------|
| **Executor** | 生成 LaTeX 推导、逐步推演公式、处理数学符号 |
| **Researcher** | 从 EXPLORING 文献库检索相关定理作为推导起点、提供 `\cite{}` |
| **Reviewer** | 检查推导逻辑是否自洽、数学推理是否正确、引文是否匹配 |

### 循环规则

与 DESIGNING 阶段一致：
- Agent 间通过 @mention 通信，自动流转
- 最多 3 轮循环，达到上限后由 Executor 汇总
- 用户可随时打断，输入框发送消息即中断当前循环
- Executor 执行代码前必须向用户说明并征求同意

### 数据获取

Executor 自带数据获取 Skill，会自动：
1. 根据子问题标题判断需要什么数据
2. 搜索公开数据集、API 或合成数据方案
3. 向用户明确说明数据来源，征求同意
4. 如需用户上传，开放上传路径

### 阶段完成条件

所有子问题 `status: completed` 后，用户点击确认按钮，状态推进到 WRITING。

### 持久化

- `tasks.json` 实时更新，每完成一个子问题立即写入
- 代码、结果、推导文件实时落盘
- 用户退出后重新进入，从上次中断处继续

### 与 DESIGNING 的区别

| | DESIGNING | RESEARCHING |
|------|-----------|-------------|
| Agent 做什么 | 辩论、建议修改大纲 | **主动写代码/推导、执行、debug** |
| 产物 | 文字修改建议 | 代码文件 + LaTeX 源码 + 运行结果 |
| 用户角色 | 编辑大纲、确认 | 审查代码/推导、点运行、点采纳 |
| 循环 | 对话辩论 | 写→执行→检查→修→再执行 |

---


﻿## 七、技术实现（暂定）

### 后端

| 组件 | 技术 | 理由 |
|------|------|------|
| 子问题拆解 | LLM + Pydantic 结构化输出 | 复用 `classify_intent` 模式 |
| 代码生成 | `LLMProvider.generate()` | 现有 LLM 适配器 |
| 代码执行 | `subprocess.run()` + 沙箱 | 现有 `sandbox.py` 路径约束 |
| 结果收集 | `glob` + 文件读取 | 扫描输出目录的图表/CSV/log |
| 推导生成 | `LLMProvider.generate()` + 文献库 | 基于 EXPLORING 文献库标注引用 |
| LaTeX 生成 | LLM 逐步推导 → LaTeX 源码 | 追加到 `derivation.tex` |
| 文件打包 | `zipfile` + `shutil` | 标准库 |

### 关键技术决策

- **不做 IDE**：不嵌入终端、文件树、Git 面板，最小化复杂度
- **不做 Jupyter**：不引入 kernel 管理，直接用 subprocess 跑脚本
- **代码是用户的**：AI 生成初稿，用户在编辑器里自由修改
- **采纳时 git commit**：每个子问题完成后自动版本记录

> 技术方案为暂定，后续实现时可能调整。
