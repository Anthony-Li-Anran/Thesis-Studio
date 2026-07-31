"""Thesis Studio — 面向毕业论文生成的 AI 研究助手。

基于 Clean Architecture + Hexagonal Architecture + SOLID 原则构建。

分层结构：
- domain/     领域层：实体、端口接口、领域异常（最内层，零外部依赖）
- application/ 应用层：用例/服务编排（依赖领域端口）
- infrastructure/ 基础设施层：端口适配器实现（依赖外部框架）
- presentation/ 接口层：FastAPI、Chainlit、NiceGUI
- config/     配置管理
"""

__version__ = "0.1.0"
