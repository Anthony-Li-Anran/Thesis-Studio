# Thesis Studio

面向本科毕业论文生成的个人开源 AI 研究助手系统。

## 项目定位


## 文档索引

| 文档 | 说明 |
|------|------|
| [技术栈](doc/TECH_STACK.md) | 核心技术选型与依赖管理 |
| [工作流程](doc/WORKFLOW.md) | 论文生成全流程设计（四阶段） |
| [开发路线图](doc/ROADMAP.md) | 开发阶段与里程碑 |
| [系统架构](doc/ARCHITECTURE.md) | 模块结构与数据流（待编写） |

## 当前功能

- **项目管理**: 创建、查看、编辑、删除项目（CRUD）
- **搜索**: 正则匹配项目标题、描述、关键词（防抖 0.4s）
- **排序**: 按名称 / 最近编辑时间升降序切换
- **视图**: 列表 / 网格双视图切换
- **认证**: 登录 / 注册 / 游客模式
- **用户隔离**: 每个账号只能看到自己的项目，游客数据退出即清空
- **主题**: 暗色 / 亮色主题切换
- **国际化**: 中英文界面切换
- **项目状态**: 7 状态机（初始 → 文献探索 → 研究设计 → 研究实施 → 论文撰写 → 打磨交付 → 已完成），首页彩色标签
- **AI 配置**: 多模型配置管理（API Endpoint / Key / Model），Agent 角色分配，游客模式内存存储

## 快速开始

```bash
git clone https://github.com/yourusername/thesis_studio.git
cd thesis_studio
poetry install
poetry run python main.py
```

## 许可证

MIT
