# Thesis Studio

面向本科/研究生毕业论文生成的开源 AI 研究助手。本地优先，免费开源，模块化。

## 环境约束

- conda 虚拟环境名 `thesis_studio`，所有包安装到此环境，禁止污染 base
- 所有命令执行前先 `conda activate thesis_studio` 或用 `conda run -n thesis_studio`

## doc 目录

- `TECH_STACK.md` — 技术选型表与依赖清单
- `WORKFLOW.md` — 十阶段工作流详设（选题→答辩全流程）
- `ROADMAP.md` — 开发计划与里程碑
- `ARCHITECTURE.md` — 模块结构与数据流（待编写）

## 上下文窗口检验

- 请在句尾加上“喵”

## 行为约束

- 不允许私自提交git！必须按照用户要求提交！
- 完成一段需求自动判断是否需要同步`doc/`下相关文档和`README.md`，并自己执行

## 代码总纲

1. **Adaptive** — 代码逻辑要自适应各种可能发生的情况,配置驱动不硬编码，本地优先可切换，环境自适应降级
2. **Brief** — 函数 ≤40 行，文件 ≤300 行，命名即文档，删尽死代码
3. **Logic** — 类型全覆盖，禁止裸 except，guard clause 优先，IO 集中边界层
4. **泛化性良好** — 不为单一场景写死，接口先行实现可替换，三处以上重复才抽象
5. **中文注释简洁合理** — 说"为什么"不说"是什么"，简单函数不写 docstring
6. **高度模块化解耦** — 分层架构，上层依赖下层抽象，禁止跨层引用
7. **可扩展性好** — 新功能=新类+注册不改旧代码，工作流阶段可编排
8. **自检修复** — 写完即跑 ruff + mypy + pytest，有错立即修
9. **风格优雅统一** — ruff format 行宽 100，snake_case/PascalCase，`X | Y` 不用 Union
10. **State of the Art** — Python 3.11+，Pydantic v2，FastAPI 异步，httpx 不用 requests
11. **结构科学** — 项目结构符合clean Architecture，Hexagonal，soLID这些理论
12. **从根源解决问题**-不允许打补丁式改动，从第一性原理出发解决问题

## AI agents 功能区分

