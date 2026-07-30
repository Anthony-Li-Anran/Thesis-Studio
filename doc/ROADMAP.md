# Thesis Studio 开发路线图

采用边开发边文档的策略：每个阶段完成后更新对应文档，不预先写全部内容。

## Phase 1: 基础框架（1-2 周）

- [ ] 项目结构搭建（Poetry/uv 初始化）
- [ ] FastAPI 后端基础架构
- [ ] Chainlit 对话交互界面框架
- [ ] NiceGUI 管理面板框架
- [ ] SQLite + ChromaDB 数据库集成
- [ ] 基础配置管理（.env）

## Phase 2: 文献管理（2 周）

- [ ] 文献检索模块（Semantic Scholar、arXiv API）
- [ ] PDF 解析与存储（PyMuPDF、marker）
- [ ] 文献库管理界面
- [ ] 向量化与语义检索

## Phase 3: AI 辅助写作（2-3 周）

- [ ] LLM 集成（Ollama 本地模型 + OpenAI API 备选）
- [ ] 文献综述生成
- [ ] 研究问题定义辅助
- [ ] 论文大纲生成

## Phase 4: 数据分析（1-2 周）

- [ ] 数据导入与清洗工具
- [ ] 基础统计分析
- [ ] 可视化图表生成

## Phase 5: 文档输出（1-2 周）

- [ ] 论文章节内容生成
- [ ] Word 文档导出（python-docx）
- [ ] 引用格式化管理
- [ ] 答辩 PPT 生成（python-pptx）

## Phase 6: 完善与发布（1 周）

- [ ] 单元测试（pytest）
- [ ] 用户文档编写
- [ ] 部署脚本（可选 Docker）
- [ ] GitHub 开源发布

---

**总周期**：约 8-12 周（单人开发，含调试与文档）
