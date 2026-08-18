# Thesis Studio

面向本科毕业论文生成的个人开源 AI 研究助手系统。

## 项目定位

**场景B**：用户带着明确的研究题目入场，AI 辅助完成从文献探索、研究规划、研究实施、论文撰写到打磨交付的全流程。系统不负责"帮用户找题目"，而是帮用户**把已有的题目落地为一篇高质量学术论文**。

## 文档索引

| 文档 | 说明 |
|------|------|
| [技术栈](doc/TECH_STACK.md) | 核心技术选型与依赖管理 |
| [工作流程](doc/WORKFLOW.md) | 论文生成全流程设计（四阶段七状态） |
| [文献探索](doc/EXPLORING.md) | EXPLORING 阶段设计（输入输出、工作流） |
| [研究规划](doc/DESIGNING.md) | DESIGNING 阶段设计（输入输出、大纲） |
| [开发路线图](doc/ROADMAP.md) | 开发阶段与里程碑 |
| [系统架构](doc/ARCHITECTURE.md) | 模块结构与数据流 |

## 当前功能

- **项目管理**: 创建、查看、编辑、删除项目（CRUD）
- **搜索**: 正则匹配项目标题、描述、关键词（防抖 0.4s）
- **排序**: 按名称 / 最近编辑时间升降序切换
- **视图**: 列表 / 网格双视图切换
- **认证**: 登录 / 注册 / 游客模式
- **用户隔离**: 每个帐号只能看到自己的项目，游客数据退出即清空
- **主题**: 暗色 / 亮色主题切换
- **国际化**: 中英文界面切换
- **项目状态**: 7 状态机（初始 → 文献探索 → 研究规划 → 研究实施 → 论文撰写 → 打磨交付 → 已完成），首页彩色标签
- **AI 配置**: 多模型配置管理（API Endpoint / Key / Model），Agent 角色分配，游客模式内存存储
- **文献探索**: 微信式聊天室 + 知识图谱 + 文献详情面板，Researcher Agent 自动检索/聚类/综述

## 快速开始

```bash
git clone https://github.com/yourusername/thesis_studio.git
cd thesis_studio
conda activate thesis_studio
pip install -e ".[dev]"
python main.py
```

## 许可协议

MIT
